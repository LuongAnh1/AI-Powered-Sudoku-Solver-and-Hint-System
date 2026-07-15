# app/gui/sudoku_board.py
import customtkinter as ctk
from gui.sudoku_cell import SudokuCell

class SudokuBoard(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        # Đổi fg_color và border_color sang màu nền tối #1E293B đồng nhất với card chứa
        super().__init__(master, fg_color="#1E293B", corner_radius=8, border_width=3, border_color="#1E293B", **kwargs)
        
        self.grid_propagate(False)
        
        for r in range(3):
            self.grid_rowconfigure(r, weight=1)
            self.grid_columnconfigure(r, weight=1)

        self.cells = {}
        for sub_r in range(3):
            for sub_c in range(3):
                # CBD5E1 tạo thành các đường lưới nhạt rõ ràng phân tách giữa các ô vuông con
                sub_frame = ctk.CTkFrame(self, fg_color="#CBD5E1", corner_radius=0)
                sub_frame.grid(row=sub_r, column=sub_c, sticky="nsew", padx=1.5, pady=1.5)
                
                sub_frame.grid_propagate(False)
                
                for i in range(3):
                    sub_frame.grid_rowconfigure(i, weight=1)
                    sub_frame.grid_columnconfigure(i, weight=1)

                for r in range(3):
                    for c in range(3):
                        abs_r = sub_r * 3 + r
                        abs_c = sub_c * 3 + c
                        cell = SudokuCell(sub_frame, row=abs_r, col=abs_c)
                        cell.grid(row=r, column=c, sticky="nsew", padx=0.5, pady=0.5)
                        self.cells[(abs_r, abs_c)] = cell

    def get_cell(self, row: int, col: int) -> SudokuCell:
        return self.cells[(row, col)]

    def register_cell_clicks(self, callback):
        """Đăng ký hàm xử lý sự kiện click cho toàn bộ 81 ô"""
        for cell in self.cells.values():
            cell.bind_click(callback)

    def clear_all(self):
        """Dọn dẹp toàn bộ giá trị số chính thức, số nháp và màu sắc của lưới"""
        for cell in self.cells.values():
            cell.set_value(0)
            cell.set_pencil_marks([])  # Xóa toàn bộ ghi chú nháp cũ
            cell.reset_highlight()