# app/hint_manager/chain_generator.py
import re

try:
    import sudoku_solver_cpp
except ImportError:
    sudoku_solver_cpp = None


class ChainGeneratorMixin:
    TRANSPOSE_INPUT_MATRIX = False
    TRANSPOSE_OUTPUT_COORDINATES = False
    hint_chains = []
    chain_index = 0

    def _parse_hint_result(self, hint_cpp) -> dict:
        """Phân tích cấu trúc dữ liệu HintResult từ C++ sang Dictionary của Python"""
        if isinstance(hint_cpp, dict):
            return hint_cpp

        def get_attr(obj, *names, default=None):
            for name in names:
                if hasattr(obj, name):
                    return getattr(obj, name)
            return default

        found = get_attr(hint_cpp, "found", "found_", default=False)
        strategy_name = get_attr(hint_cpp, "strategyName", "strategy_name", default="")
        explanation = get_attr(hint_cpp, "explanation", default="")
        fill_row = get_attr(hint_cpp, "fillRow", "fill_row", default=-1)
        fill_col = get_attr(hint_cpp, "fillCol", "fill_col", default=-1)
        fill_value = get_attr(hint_cpp, "fillValue", "fill_value", default=0)

        pattern_cells = []
        raw_patterns = get_attr(hint_cpp, "patternCells", "pattern_cells", default=[])
        for p in raw_patterns:
            r, c = -1, -1
            if hasattr(p, "__len__") and len(p) >= 2:
                r, c = p[0], p[1]
            elif hasattr(p, "first") and hasattr(p, "second"):
                r, c = p.first, p.second
            elif hasattr(p, "row") and hasattr(p, "col"):
                r, c = p.row, p.col
            
            if r != -1 and c != -1:
                if self.TRANSPOSE_OUTPUT_COORDINATES:
                    r, c = c, r  
                pattern_cells.append((r, c))

        eliminations = []
        raw_elims = get_attr(hint_cpp, "eliminations", default=[])
        for e in raw_elims:
            r = get_attr(e, "row", default=-1)
            c = get_attr(e, "col", default=-1)
            v = get_attr(e, "value", default=0)
            if r != -1 and c != -1 and v != 0:
                if self.TRANSPOSE_OUTPUT_COORDINATES:
                    r, c = c, r  
                eliminations.append((r, c, v))

        if self.TRANSPOSE_OUTPUT_COORDINATES and fill_row != -1 and fill_col != -1:
            fill_row, fill_col = fill_col, fill_row

        if self.TRANSPOSE_OUTPUT_COORDINATES and explanation:
            def swap_coord_match(match):
                r_val = match.group(1)
                c_val = match.group(2)
                return f"({c_val},{r_val})"
            explanation = re.sub(r'\((\d+)\s*,\s*(\d+)\)', swap_coord_match, explanation)

        return {
            "success": found,
            "strategy_name": strategy_name,
            "explanation": explanation,
            "row": fill_row,
            "col": fill_col,
            "value": fill_value,
            "pattern_cells": pattern_cells,
            "eliminations": eliminations
        }

    def _generate_solution_chains(self, matrix):
        """Khởi chạy thuật toán lập lịch trước toàn bộ chuỗi giải"""
        self.hint_chains = []
        self.chain_index = 0
        
        if sudoku_solver_cpp is None:
            return

        try:
            temp_engine = sudoku_solver_cpp.SolverEngine()
            working_matrix = [list(row) for row in matrix]
            seen_hint_signatures = set()
            all_steps = []
            safety_limit = 81
            
            self._force_load_grid(temp_engine, working_matrix)
            
            if self._board_has_pencil_marks():
                self._sync_gui_candidates_to_engine(temp_engine)

            while len(all_steps) < safety_limit:
                if hasattr(temp_engine, "get_next_hint"):
                    hint_cpp = temp_engine.get_next_hint()
                elif hasattr(temp_engine, "GetNextHint"):
                    hint_cpp = temp_engine.GetNextHint()
                else:
                    break

                hint = self._parse_hint_result(hint_cpp)
                if not hint or not hint.get("success", False):
                    break
                
                sig = f"{hint.get('strategy_name')}_{hint.get('row')}_{hint.get('col')}_{hint.get('value')}"
                if sig in seen_hint_signatures:
                    print(f"⚠️ [WARNING] Phát hiện C++ Engine lặp vòng lặp vô hạn ở bước: {sig}. Dừng lập lịch.")
                    break
                seen_hint_signatures.add(sig)

                all_steps.append(hint)
                self._sync_single_hint_to_target_engine(temp_engine, hint, working_matrix)

            current_chain = []
            for step in all_steps:
                current_chain.append(step)
                if step.get("value", 0) > 0:
                    self.hint_chains.append(current_chain)
                    current_chain = []
            
            if current_chain:
                self.hint_chains.append(current_chain)

            print(f"📊 [INFO] Lập lịch giải thành công. Tìm thấy {len(self.hint_chains)} chuỗi gợi ý logic.")

        except Exception as e:
            print(f"❌ [ERROR] Thất bại trong tiến trình chạy giải và lập lịch trước: {e}")
            self.hint_chains = []

    def _force_load_grid(self, target_engine, working_matrix):
        """Gửi ma trận sang C++ Engine"""
        matrix_to_load = working_matrix
        if self.TRANSPOSE_INPUT_MATRIX:
            matrix_to_load = [list(x) for x in zip(*working_matrix)]

        if hasattr(target_engine, "load_grid"):
            target_engine.load_grid(matrix_to_load)
        elif hasattr(target_engine, "LoadGrid"):
            target_engine.LoadGrid(matrix_to_load)

    def _sync_single_hint_to_target_engine(self, target_engine, hint, working_matrix):
        """Đồng bộ một bước gợi ý cụ thể vào động cơ C++ chỉ định"""
        for r, c, val in hint.get("eliminations", []):
            cpp_r, cpp_c = (c, r) if self.TRANSPOSE_INPUT_MATRIX else (r, c)
            try:
                if hasattr(target_engine, "remove_candidate"):
                    target_engine.remove_candidate(cpp_r, cpp_c, val)
                elif hasattr(target_engine, "RemoveCandidate"):
                    target_engine.RemoveCandidate(cpp_r, cpp_c, val)
            except Exception:
                pass

        target_r = hint.get("row", -1)
        target_col = hint.get("col", -1)
        target_val = hint.get("value", 0)
        
        if target_r != -1 and target_col != -1 and target_val > 0:
            cpp_r, cpp_c = (target_col, target_r) if self.TRANSPOSE_INPUT_MATRIX else (target_r, target_col)
            success = False
            
            for method in ["place_value", "PlaceValue", "set_cell", "SetCell"]:
                if hasattr(target_engine, method):
                    try:
                        getattr(target_engine, method)(cpp_r, cpp_c, target_val)
                        success = True
                        break
                    except Exception:
                        pass
            
            if not success:
                working_matrix[target_r][target_col] = target_val
                self._force_load_grid(target_engine, working_matrix)

    def _sync_gui_candidates_to_engine(self, target_engine):
        """
        Trích xuất trạng thái số nháp từ GUI và ghi đè ngược lại vào C++ Engine chỉ định.
        Với các ô trống, số nào KHÔNG xuất hiện trên GUI sẽ bị xóa khỏi bộ nhớ C++.
        """
        if target_engine is None or sudoku_solver_cpp is None:
            return

        for r in range(9):
            for c in range(9):
                cell = self.board.get_cell(r, c)
                cell_text = cell.main_label.cget("text").strip()
                
                # Chỉ đồng bộ đối với các ô trống
                if not cell_text:
                    gui_candidates = self._get_cell_candidates(cell)
                    
                    # Nếu ô trống này đã được khởi tạo/có chứa số nháp trên GUI
                    if gui_candidates:
                        for val in range(1, 10):
                            if val not in gui_candidates:
                                cpp_r, cpp_c = (c, r) if self.TRANSPOSE_INPUT_MATRIX else (r, c)
                                try:
                                    if hasattr(target_engine, "remove_candidate"):
                                        target_engine.remove_candidate(cpp_r, cpp_c, val)
                                    elif hasattr(target_engine, "RemoveCandidate"):
                                        target_engine.RemoveCandidate(cpp_r, cpp_c, val)
                                except Exception:
                                    pass