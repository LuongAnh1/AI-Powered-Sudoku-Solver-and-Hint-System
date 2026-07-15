# app/hint_manager/gui_sync.py
import sys

try:
    import sudoku_solver_cpp
except ImportError:
    sudoku_solver_cpp = None


class GUISyncMixin:
    # Định nghĩa sẵn các thuộc tính để IDE tự động nhận diện từ lớp chính
    board = None
    engine = None
    explanation_box = None
    TRANSPOSE_INPUT_MATRIX = False

    def _get_current_grid_matrix(self):
        """Trích xuất ma trận số lớn từ giao diện hiện tại"""
        matrix = []
        for r in range(9):
            row_vals = []
            for c in range(9):
                cell_text = self.board.get_cell(r, c).main_label.cget("text").strip()
                row_vals.append(int(cell_text) if cell_text.isdigit() else 0)
            matrix.append(row_vals)
        return matrix

    def _get_cell_candidates(self, cell):
        """Lấy danh sách các số nháp hiện tại của một ô"""
        candidates = []
        for val, lbl in cell.pencil_labels.items():
            if lbl.cget("text") != "":
                candidates.append(val)
        return candidates

    def _board_has_pencil_marks(self) -> bool:
        """Kiểm tra xem trên lưới hiện tại đã có số nháp nào được vẽ chưa"""
        for r in range(9):
            for c in range(9):
                cell = self.board.get_cell(r, c)
                if self._get_cell_candidates(cell):
                    return True
        return False

    def _count_total_pencil_marks(self) -> int:
        """Đếm tổng số lượng số nháp đang hiển thị trên toàn bộ các ô trống"""
        total = 0
        for r in range(9):
            for c in range(9):
                cell = self.board.get_cell(r, c)
                if cell.main_label.cget("text") == "":
                    total += len(self._get_cell_candidates(cell))
        return total

    def update_gui_pencil_marks(self):
        """Lấy dữ liệu ứng viên hiện tại từ C++ Engine và cập nhật đồng bộ lên các ô trên GUI"""
        if self.engine is None or sudoku_solver_cpp is None:
            return
            
        try:
            if hasattr(self.engine, "get_grid_candidates"):
                all_candidates = self.engine.get_grid_candidates()
            elif hasattr(self.engine, "GetGridCandidates"):
                all_candidates = self.engine.GetGridCandidates()
            else:
                return

            for r in range(9):
                for c in range(9):
                    cell = self.board.get_cell(r, c)
                    cell_text = cell.main_label.cget("text")
                    
                    if not cell_text:  
                        candidates = all_candidates[r][c]
                        cell.set_pencil_marks(candidates)
                    else:
                        cell.set_pencil_marks([])
                        
        except Exception as e:
            print(f"⚠️ [WARNING] Không thể đồng bộ hóa ứng viên lên giao diện: {e}")

    def _update_log_box(self, text):
        """Ghi chuỗi giải thích vào khung text nhật ký giao diện"""
        self.explanation_box.configure(state="normal")
        self.explanation_box.delete("0.0", "end")
        self.explanation_box.insert("0.0", text)
        self.explanation_box.configure(state="disabled")