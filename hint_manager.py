# app/hint_manager.py
import os
import sys
import re

# Các màu sắc hiển thị gợi ý
COLOR_TARGET = "#C8E6C9"       # Xanh lá pastel - ô sẽ được điền số (fillValue)
COLOR_PATTERN = "#FFE082"      # Vàng hổ phách - các ô chứa mô hình logic (patternCells)
COLOR_ELIMINATION = "#FFCDD2"  # Đỏ nhạt - các ô bị loại bỏ số nháp (eliminations)

try:
    import sudoku_solver_cpp
except ImportError:
    sudoku_solver_cpp = None
    print("⚠️ [WARNING] Không tìm thấy module sudoku_solver_cpp. Chạy ở chế độ mô phỏng (Mock).")


class SudokuHintManager:
    def __init__(self, board, explanation_box, next_button):
        self.board = board
        self.explanation_box = explanation_box
        self.next_button = next_button
        
        self.state = "IDLE"
        self.current_hint_chain = []
        
        # Đồng bộ hệ tọa độ giữa GUI và C++
        self.TRANSPOSE_INPUT_MATRIX = False       
        self.TRANSPOSE_OUTPUT_COORDINATES = False  
        
        self.hint_chains = []
        self.chain_index = 0
        self.last_loaded_matrix = None
        
        # Khởi tạo đối tượng C++ Engine sống để theo dõi trạng thái tương tác hiện tại
        self.engine = None

    def handle_next_hint(self):
        if self.state == "IDLE":
            self._proc_show_hint_chain()
        elif self.state == "SHOWING_HINT":
            self._proc_apply_hint_chain()

    def reset_state(self):
        self.current_hint_chain = []
        self.state = "IDLE"
        if self.next_button:
            self.next_button.configure(text="Gợi ý kế tiếp", fg_color="#ef6c00", hover_color="#e65100")

    def invalidate_engine(self):
        self.hint_chains = []
        self.chain_index = 0
        self.last_loaded_matrix = None
        self.engine = None  # Hủy đối tượng C++ Engine sống
        self.reset_state()

    def prepare_solution_chain(self):
        """Khởi tạo luồng giải thuật toán, tạo engine sống và tính toán ứng viên ban đầu"""
        matrix = self._get_current_grid_matrix()
        
        # Khởi tạo Engine sống đồng hành cùng bàn cờ
        if sudoku_solver_cpp is not None:
            self.engine = sudoku_solver_cpp.SolverEngine()
            self._force_load_grid(self.engine, matrix)
            
            # ĐỒNG BỘ NGƯỢC: Nếu lưới giao diện đã có sẵn số nháp cũ, nạp đè vào engine sống
            if self._board_has_pencil_marks():
                self._sync_gui_candidates_to_engine(self.engine)
        
        # Tính toán chuỗi giải logic trước (lập lịch trình)
        self._generate_solution_chains(matrix)
        self.last_loaded_matrix = matrix

        # Hiển thị toàn bộ số nháp tính toán được lên lưới GUI
        self.update_gui_pencil_marks()

    def update_gui_pencil_marks(self):
        """Lấy dữ liệu ứng viên hiện tại từ C++ Engine và cập nhật đồng bộ lên các ô trên GUI"""
        if self.engine is None or sudoku_solver_cpp is None:
            return
            
        try:
            # Gọi hàm get_grid_candidates() từ thư viện C++ bạn đã xây dựng
            if hasattr(self.engine, "get_grid_candidates"):
                all_candidates = self.engine.get_grid_candidates()
            elif hasattr(self.engine, "GetGridCandidates"):
                all_candidates = self.engine.GetGridCandidates()
            else:
                return

            # Cập nhật số nháp cho từng ô trong số 81 ô
            for r in range(9):
                for c in range(9):
                    cell = self.board.get_cell(r, c)
                    cell_text = cell.main_label.cget("text")
                    
                    # Nếu ô chưa được điền số chính thức, hiển thị danh sách số nháp khả dĩ
                    if not cell_text:  
                        candidates = all_candidates[r][c]
                        cell.set_pencil_marks(candidates)
                    else:
                        # Đã có số chính thức thì xóa sạch hiển thị số nháp của ô đó
                        cell.set_pencil_marks([])
                        
        except Exception as e:
            print(f"⚠️ [WARNING] Không thể đồng bộ hóa ứng viên lên giao diện: {e}")

    def quick_solve(self):
        """Thực hiện giải nhanh toàn bộ bảng và dọn dẹp sạch sẽ các ứng viên nháp"""
        matrix = self._get_current_grid_matrix()
        
        if not self.hint_chains or self.last_loaded_matrix != matrix:
            self._generate_solution_chains(matrix)
            self.last_loaded_matrix = matrix

        if not self.hint_chains or self.chain_index >= len(self.hint_chains):
            self._update_log_box("Không có bước giải logic nào khả dụng để thực hiện giải nhanh.")
            return

        cells_filled = 0
        elim_count = 0
        step_counter = 1
        
        detailed_log = "=== TIẾN TRÌNH GIẢI NHANH LOGIC TOÀN BỘ BẢNG SUDOKU ===\n"

        for idx in range(self.chain_index, len(self.hint_chains)):
            chain = self.hint_chains[idx]
            detailed_log += f"\n--- CHUỖI PHÂN TÍCH LOGIC #{idx + 1} ---\n"
            
            for step in chain:
                name = step.get("strategy_name", "Thuật toán")
                desc = step.get("explanation", "").replace("\n", " ")
                
                # 1. Thống kê số lượng ứng cử viên nháp bị loại bỏ
                for r, c, val in step.get("eliminations", []):
                    elim_count += 1
                
                # 2. Áp dụng điền số chính thức trên giao diện
                target_r = step.get("row", -1)
                target_col = step.get("col", -1)
                target_val = step.get("value", 0)
                
                if target_r != -1 and target_col != -1 and target_val > 0:
                    self.board.get_cell(target_r, target_col).set_value(target_val, is_original=False)
                    self.board.get_cell(target_r, target_col).set_pencil_marks([]) # Ẩn số nháp khi đã điền số chính thức
                    cells_filled += 1
                    
                    r_show, c_show = target_r + 1, target_col + 1
                    detailed_log += (
                        f"➔ [BƯỚC {step_counter}] {name}:\n"
                        f"  {desc}\n"
                        f"  => ĐIỀN SỐ {target_val} VÀO Ô ({r_show}, {c_show}).\n"
                    )
                else:
                    detailed_log += f"• [Bước {step_counter}] {name}: {desc}\n"
                
                step_counter += 1

        # Dọn dẹp màu sắc highlight
        for r in range(9):
            for c in range(9):
                cell = self.board.get_cell(r, c)
                cell.reset_highlight()
                cell.set_pencil_marks([]) # Xóa tất cả các số nháp khi game đã hoàn thành

        detailed_log += "\n==================================================\n"
        detailed_log += "TỔNG KẾT TIẾN TRÌNH GIẢI NHANH:\n"
        detailed_log += f"- Điền hoàn chỉnh: {cells_filled} ô số chính thức.\n"
        detailed_log += f"- Loại bỏ: {elim_count} số nháp không còn khả dụng.\n"
        detailed_log += "Hệ thống đã giải quyết hoàn toàn lưới Sudoku hiện tại."

        self._update_log_box(detailed_log)
        self.invalidate_engine()

    def _get_current_grid_matrix(self):
        matrix = []
        for r in range(9):
            row_vals = []
            for c in range(9):
                cell_text = self.board.get_cell(r, c).main_label.cget("text").strip()
                row_vals.append(int(cell_text) if cell_text.isdigit() else 0)
            matrix.append(row_vals)
        return matrix

    def _get_cell_candidates(self, cell):
        candidates = []
        for val, lbl in cell.pencil_labels.items():
            if lbl.cget("text") != "":
                candidates.append(val)
        return candidates

    def _parse_hint_result(self, hint_cpp) -> dict:
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
            
            # ĐỒNG BỘ NGƯỢC: Áp dụng trạng thái ứng viên từ giao diện vào động cơ lập lịch tạm thời
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
        matrix_to_load = working_matrix
        if self.TRANSPOSE_INPUT_MATRIX:
            matrix_to_load = [list(x) for x in zip(*working_matrix)]

        if hasattr(target_engine, "load_grid"):
            target_engine.load_grid(matrix_to_load)
        elif hasattr(target_engine, "LoadGrid"):
            target_engine.LoadGrid(matrix_to_load)

    def _sync_single_hint_to_target_engine(self, target_engine, hint, working_matrix):
        """Đồng bộ một bước gợi ý cụ thể vào động cơ C++ chỉ định"""
        # 1. Đồng bộ hành động xóa ứng viên
        for r, c, val in hint.get("eliminations", []):
            cpp_r, cpp_c = (c, r) if self.TRANSPOSE_INPUT_MATRIX else (r, c)
            try:
                if hasattr(target_engine, "remove_candidate"):
                    target_engine.remove_candidate(cpp_r, cpp_c, val)
                elif hasattr(target_engine, "RemoveCandidate"):
                    target_engine.RemoveCandidate(cpp_r, cpp_c, val)
            except Exception:
                pass

        # 2. Đồng bộ hành động điền số chính thức
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

    def _proc_show_hint_chain(self):
        """BƯỚC HIỂN THỊ GỢI Ý: Tô màu mô hình phân tích và các ô bị loại trừ"""
        matrix = self._get_current_grid_matrix()
        
        empty_count = sum(row.count(0) for row in matrix)
        if empty_count == 0:
            self._update_log_box("Chúc mừng! Bảng Sudoku đã được giải quyết hoàn toàn.")
            self.invalidate_engine()
            return

        if not self.hint_chains:
            self.prepare_solution_chain()

        if not self.hint_chains or self.chain_index >= len(self.hint_chains):
            self._update_log_box("Không tìm thấy bước đi logic tiếp theo. Bàn cờ đã giải xong hoặc cần thuật toán quay lui (Backtracking).")
            self.reset_state()
            return

        hint_chain = self.hint_chains[self.chain_index]
        self.current_hint_chain = hint_chain
        self.state = "SHOWING_HINT"

        if self.next_button:
            self.next_button.configure(text="Áp dụng gợi ý", fg_color="#2e7d32", hover_color="#1b5e20")

        # Khôi phục màu nền cũ trước khi tô màu mới
        for r in range(9):
            for c in range(9):
                self.board.get_cell(r, c).reset_highlight()

        # Tô màu cho các ô thuộc mô hình logic và ô bị loại bỏ số nháp
        for step in hint_chain:
            for r, c in step.get("pattern_cells", []):
                self.board.get_cell(r, c).highlight(COLOR_PATTERN)
                
            for r, c, _ in step.get("eliminations", []):
                self.board.get_cell(r, c).highlight(COLOR_ELIMINATION)

        # Tô màu cho ô đích sẽ được điền số chính thức
        final_step = hint_chain[-1]
        target_r = final_step.get("row", -1)
        target_col = final_step.get("col", -1)
        target_val = final_step.get("value", 0)
        if target_r != -1 and target_col != -1 and target_val > 0:
            self.board.get_cell(target_r, target_col).highlight(COLOR_TARGET)

        explanation_text = "HỆ THỐNG PHÂN TÍCH TIẾN TRÌNH LOGIC (LẬP LỊCH TRƯỚC):\n"
        for idx, step in enumerate(hint_chain):
            step_num = idx + 1
            name = step.get("strategy_name", "Thuật toán")
            desc = step.get("explanation", "").replace("\n", " ")
            
            if step.get("value", 0) > 0:
                r_show, c_show = step.get("row", 0) + 1, step.get("col", 0) + 1
                val_show = step.get("value", 0)
                explanation_text += f"\n➔ [BƯỚC {step_num}] {name}:\n  {desc}\n  => ĐIỀN SỐ {val_show} VÀO Ô ({r_show}, {c_show}).\n"
            else:
                explanation_text += f"• [Bước {step_num}] {name}: {desc}\n"

        self._update_log_box(explanation_text)

    def _proc_apply_hint_chain(self):
        """BƯỚC ÁP DỤNG GỢI Ý: Thực tế hóa điền số, xóa số nháp trên C++ Engine và cập nhật lên GUI"""
        if not self.current_hint_chain:
            self.reset_state()
            return

        # 1. Đếm tổng số nháp trên lưới trước khi áp dụng gợi ý
        pencil_before = self._count_total_pencil_marks()

        fill_performed = False

        # Áp dụng từng bước nhỏ trong chuỗi gợi ý hiện hành vào cả live C++ engine và GUI
        for step in self.current_hint_chain:
            # Đồng bộ các ô loại bỏ ứng viên (đối với thuật toán nâng cao)
            for r, c, val in step.get("eliminations", []):
                if self.engine is not None:
                    cpp_r, cpp_c = (c, r) if self.TRANSPOSE_INPUT_MATRIX else (r, c)
                    try:
                        if hasattr(self.engine, "remove_candidate"):
                            self.engine.remove_candidate(cpp_r, cpp_c, val)
                        elif hasattr(self.engine, "RemoveCandidate"):
                            self.engine.RemoveCandidate(cpp_r, cpp_c, val)
                    except Exception:
                        pass

            # Đồng bộ ô điền số chính thức
            target_r = step.get("row", -1)
            target_col = step.get("col", -1)
            target_val = step.get("value", 0)

            if target_r != -1 and target_col != -1 and target_val > 0:
                # Cập nhật số lên bảng giao diện
                self.board.get_cell(target_r, target_col).set_value(target_val, is_original=False)
                fill_performed = True

                if self.last_loaded_matrix is not None:
                    self.last_loaded_matrix[target_r][target_col] = target_val

                # Cập nhật thông tin điền số vào live C++ Engine
                if self.engine is not None:
                    cpp_r, cpp_c = (target_col, target_r) if self.TRANSPOSE_INPUT_MATRIX else (target_r, target_col)
                    success = False
                    for method in ["place_value", "PlaceValue", "set_cell", "SetCell"]:
                        if hasattr(self.engine, method):
                            try:
                                getattr(self.engine, method)(cpp_r, cpp_c, target_val)
                                success = True
                                break
                            except Exception:
                                pass
                    
                    # Cơ chế dự phòng nếu C++ chưa được đăng ký hàm đặt số
                    if not success:
                        current_matrix = self._get_current_grid_matrix()
                        self._force_load_grid(self.engine, current_matrix)
                        if self._board_has_pencil_marks():
                            self._sync_gui_candidates_to_engine(self.engine)

        # 2. Đồng bộ lại toàn bộ số nháp thực tế từ C++ Engine lên lưới GUI
        self.update_gui_pencil_marks()

        # 3. Đếm số nháp còn lại trên lưới sau khi đồng bộ
        pencil_after = self._count_total_pencil_marks()
        
        # Tính toán chính xác hiệu số số nháp bị loại bỏ thực tế
        elim_count = pencil_before - pencil_after
        if elim_count < 0:
            elim_count = 0

        # Đặt lại màu nền của lưới về trắng
        for r in range(9):
            for c in range(9):
                self.board.get_cell(r, c).reset_highlight()

        new_matrix = self._get_current_grid_matrix()
        new_empty_count = sum(row.count(0) for row in new_matrix)
        
        if new_empty_count == 0:
            self._update_log_box("Chúc mừng! Bảng Sudoku đã được giải quyết hoàn toàn.")
        else:
            summary = f"Đã áp dụng toàn bộ chuỗi logic thành công (Xóa {elim_count} số nháp"
            if fill_performed:
                summary += " và cập nhật thành công ô số chính thức mới vào lưới cờ)."
            else:
                summary += ")."
            self._update_log_box(summary)

        self.chain_index += 1
        self.reset_state()

    def _update_log_box(self, text):
        self.explanation_box.configure(state="normal")
        self.explanation_box.delete("0.0", "end")
        self.explanation_box.insert("0.0", text)
        self.explanation_box.configure(state="disabled")

    def _board_has_pencil_marks(self) -> bool:
        """Kiểm tra xem trên toàn bộ lưới giao diện hiện tại có ít nhất một ô đang hiển thị số nháp hay không"""
        for r in range(9):
            for c in range(9):
                cell = self.board.get_cell(r, c)
                if self._get_cell_candidates(cell):
                    return True
        return False

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

    def _count_total_pencil_marks(self) -> int:
        """Đếm tổng số lượng ứng cử viên nháp hiện đang hiển thị trên toàn bộ các ô trống của lưới GUI"""
        total = 0
        for r in range(9):
            for c in range(9):
                cell = self.board.get_cell(r, c)
                # Chỉ đếm số nháp ở những ô hiện đang trống
                if cell.main_label.cget("text") == "":
                    total += len(self._get_cell_candidates(cell))
        return total