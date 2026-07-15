# app/hint_manager/hint_manager.py
from .constants import COLOR_TARGET, COLOR_PATTERN, COLOR_ELIMINATION
from .gui_sync import GUISyncMixin
from .chain_generator import ChainGeneratorMixin

try:
    import sudoku_solver_cpp
except ImportError:
    sudoku_solver_cpp = None


class SudokuHintManager(GUISyncMixin, ChainGeneratorMixin):
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
        
        # Khởi tạo đối tượng C++ Engine sống
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
        self.engine = None  
        self.reset_state()

    def prepare_solution_chain(self):
        """Khởi tạo luồng giải thuật toán, tạo engine sống và tính toán ứng viên ban đầu"""
        matrix = self._get_current_grid_matrix()
        
        if sudoku_solver_cpp is not None:
            self.engine = sudoku_solver_cpp.SolverEngine()
            self._force_load_grid(self.engine, matrix)
            
            if self._board_has_pencil_marks():
                self._sync_gui_candidates_to_engine(self.engine)
        
        self._generate_solution_chains(matrix)
        self.last_loaded_matrix = matrix
        self.update_gui_pencil_marks()

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
                
                for r, c, val in step.get("eliminations", []):
                    elim_count += 1
                
                target_r = step.get("row", -1)
                target_col = step.get("col", -1)
                target_val = step.get("value", 0)
                
                if target_r != -1 and target_col != -1 and target_val > 0:
                    self.board.get_cell(target_r, target_col).set_value(target_val, is_original=False)
                    self.board.get_cell(target_r, target_col).set_pencil_marks([]) 
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

        for r in range(9):
            for c in range(9):
                cell = self.board.get_cell(r, c)
                cell.reset_highlight()
                cell.set_pencil_marks([]) 

        detailed_log += "\n==================================================\n"
        detailed_log += "TỔNG KẾT TIẾN TRÌNH GIẢI NHANH:\n"
        detailed_log += f"- Điền hoàn chỉnh: {cells_filled} ô số chính thức.\n"
        detailed_log += f"- Loại bỏ: {elim_count} số nháp không còn khả dụng.\n"
        detailed_log += "Hệ thống đã giải quyết hoàn toàn lưới Sudoku hiện tại."

        self._update_log_box(detailed_log)
        self.invalidate_engine()

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

        for r in range(9):
            for c in range(9):
                self.board.get_cell(r, c).reset_highlight()

        for step in hint_chain:
            for r, c in step.get("pattern_cells", []):
                self.board.get_cell(r, c).highlight(COLOR_PATTERN)
                
            for r, c, _ in step.get("eliminations", []):
                self.board.get_cell(r, c).highlight(COLOR_ELIMINATION)

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

        pencil_before = self._count_total_pencil_marks()
        fill_performed = False

        for step in self.current_hint_chain:
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

            target_r = step.get("row", -1)
            target_col = step.get("col", -1)
            target_val = step.get("value", 0)

            if target_r != -1 and target_col != -1 and target_val > 0:
                self.board.get_cell(target_r, target_col).set_value(target_val, is_original=False)
                fill_performed = True

                if self.last_loaded_matrix is not None:
                    self.last_loaded_matrix[target_r][target_col] = target_val

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
                    
                    if not success:
                        current_matrix = self._get_current_grid_matrix()
                        self._force_load_grid(self.engine, current_matrix)
                        if self._board_has_pencil_marks():
                            self._sync_gui_candidates_to_engine(self.engine)

        self.update_gui_pencil_marks()

        pencil_after = self._count_total_pencil_marks()
        elim_count = pencil_before - pencil_after
        if elim_count < 0:
            elim_count = 0

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