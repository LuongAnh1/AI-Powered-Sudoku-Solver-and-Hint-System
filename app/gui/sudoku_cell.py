# app/gui/sudoku_cell.py
import customtkinter as ctk

class SudokuCell(ctk.CTkFrame):
    def __init__(self, master, row, col, **kwargs):
        # Đặt mặc định 100% tất cả các ô đều có màu nền trắng tinh khiết
        self.default_color = "#FFFFFF"

        super().__init__(master, fg_color=self.default_color, corner_radius=0, border_width=0, **kwargs)
        self.row = row
        self.col = col

        self.grid_propagate(False)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # 1. Khung chứa số nháp (Pencil marks)
        self.pencil_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.pencil_frame.grid(row=0, column=0, sticky="nsew")
        
        for r in range(3):
            self.pencil_frame.grid_rowconfigure(r, weight=1)
            self.pencil_frame.grid_columnconfigure(r, weight=1)
        
        self.pencil_labels = {}
        for i in range(1, 10):
            r = (i - 1) // 3
            c = (i - 1) % 3
            lbl = ctk.CTkLabel(self.pencil_frame, text="", font=ctk.CTkFont(family="Segoe UI", size=11, weight="normal"), text_color="#64748B")
            lbl.grid(row=r, column=c, sticky="nsew", padx=0, pady=0)
            self.pencil_labels[i] = lbl

        # 2. Nhãn số lớn chính thức (ĐÃ PHÓNG TO LÊN 36 cực kỳ nổi bật)
        self.main_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(family="Segoe UI", size=36, weight="normal"))
        self.main_label.grid(row=0, column=0, sticky="nsew")

    def bind_click(self, callback):
        self.bind("<Button-1>", lambda event: callback(self.row, self.col))
        self.main_label.bind("<Button-1>", lambda event: callback(self.row, self.col))
        self.pencil_frame.bind("<Button-1>", lambda event: callback(self.row, self.col))
        for lbl in self.pencil_labels.values():
            lbl.bind("<Button-1>", lambda event: callback(self.row, self.col))

    def set_value(self, val: int, is_original=False):
        self.main_label.tkraise()
        if val > 0:
            # Đề gốc: Xanh hải quân đậm cổ điển (#1A365D)
            # Số máy giải: Xanh hoàng gia sáng hiện đại (#2563EB)
            color = "#1A365D" if is_original else "#2563EB"
            self.main_label.configure(text=str(val), text_color=color)
        else:
            self.main_label.configure(text="")

    def set_pencil_marks(self, candidates: list):
        self.pencil_frame.tkraise()
        for val, lbl in self.pencil_labels.items():
            lbl.configure(text=str(val) if val in candidates else "")

    def highlight(self, color_hex):
        self.configure(fg_color=color_hex)

    def reset_highlight(self):
        """Khôi phục lại màu nền trắng ban đầu của ô"""
        self.configure(fg_color=self.default_color)