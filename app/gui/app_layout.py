# app/gui/app_layout.py
import os
import sys
from tkinter import filedialog, messagebox
from PIL import Image

current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(current_dir)
if app_dir not in sys.path:
    sys.path.append(app_dir)

import customtkinter as ctk
from gui.sudoku_board import SudokuBoard

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class SudokuApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AI-Powered Sudoku Solver")
        self.geometry("1100x700")
        
        self.resizable(False, False)
        
        self.grid_columnconfigure(0, weight=3, minsize=550) 
        self.grid_columnconfigure(1, weight=2, minsize=350) 
        self.grid_rowconfigure(0, weight=1)

        self._init_left_panel()
        self._init_right_panel()
        
        self.sudoku_board.register_cell_clicks(self._on_cell_click)
        
        # Khởi tạo vùng chọn mặc định ở ô (0, 0) ngay khi khởi chạy app
        self._on_cell_click(0, 0)

    def _init_left_panel(self):
        left_frame = ctk.CTkFrame(self, fg_color="transparent")
        left_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        left_frame.grid_rowconfigure(0, weight=1) 
        left_frame.grid_rowconfigure(1, weight=0) 
        left_frame.grid_columnconfigure(0, weight=1)

        self.board_container = ctk.CTkFrame(left_frame, width=530, height=530, fg_color="#1E1E1E") 
        self.board_container.grid(row=0, column=0, padx=10, pady=10)
        self.board_container.grid_propagate(False)
        
        self.sudoku_board = SudokuBoard(self.board_container, width=510, height=510)
        self.sudoku_board.place(relx=0.5, rely=0.5, anchor="center")

        self.explanation_box = ctk.CTkTextbox(left_frame, height=100, font=ctk.CTkFont(size=14))
        self.explanation_box.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="nsew")
        self.explanation_box.insert("0.0", "Hệ thống sẵn sàng. Nhấp chuột vào một ô hoặc chọn 'Nạp ảnh Sudoku'.")
        self.explanation_box.configure(state="disabled")

    def _init_right_panel(self):
        right_frame = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=10)
        right_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=0)
        right_frame.grid_columnconfigure(0, weight=1)

        self.image_preview_label = ctk.CTkLabel(right_frame, text="Chưa có ảnh được nạp", fg_color="#1d1d1d", corner_radius=8)
        self.image_preview_label.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        control_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        control_frame.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")
        control_frame.grid_columnconfigure(0, weight=1)
        control_frame.grid_columnconfigure(1, weight=1)

        self.btn_load = ctk.CTkButton(control_frame, text="Nạp ảnh Sudoku", command=self._on_load_image)
        self.btn_load.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        self.btn_solve = ctk.CTkButton(control_frame, text="Giải nhanh", fg_color="#2e7d32", hover_color="#1b5e20")
        self.btn_solve.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        self.btn_next = ctk.CTkButton(control_frame, text="Gợi ý kế tiếp", fg_color="#ef6c00", hover_color="#e65100")
        self.btn_next.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.btn_reset = ctk.CTkButton(control_frame, text="Làm mới bảng", fg_color="#c62828", hover_color="#b71c1c", command=self._on_reset)
        self.btn_reset.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

    def _has_board_data(self) -> bool:
        """Kiểm tra xem lưới hiện tại có chứa bất kỳ giá trị số hoặc số nháp nào không"""
        for r in range(9):
            for c in range(9):
                cell = self.sudoku_board.get_cell(r, c)
                if cell.main_label.cget("text") != "":
                    return True
                for lbl in cell.pencil_labels.values():
                    if lbl.cget("text") != "":
                        return True
        return False

    def _on_load_image(self):
        """Xử lý nạp ảnh, hiển thị xem trước, chạy xử lý ảnh CV và cập nhật kết quả lên lưới"""
        file_path = filedialog.askopenfilename(
            title="Chọn ảnh Sudoku để nạp",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.webp")]
        )
        if not file_path:
            return

        if self._has_board_data():
            confirm = messagebox.askyesno(
                "Xác nhận ghi đè",
                "Phát hiện bảng Sudoku hiện tại đang có dữ liệu.\n"
                "Bạn có chắc chắn muốn xóa dữ liệu cũ và nạp dữ liệu mới từ hình ảnh này không?"
            )
            if not confirm:
                return

        self._update_explanation_box("Đang nạp ảnh và nhận dạng chữ số... Xin vui lòng đợi.")
        self.update_idletasks()

        try:
            pil_img = Image.open(file_path)
            preview_max_size = 280
            pil_img.thumbnail((preview_max_size, preview_max_size))
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)
            
            self.image_preview_label.configure(image=ctk_img, text="")
            self.image_preview_label.image = ctk_img
        except Exception as e:
            messagebox.showerror("Lỗi nạp ảnh", f"Không thể tải ảnh xem trước:\n{e}")
            self._update_explanation_box("Quá trình nạp hình ảnh xem trước thất bại.")
            return

        try:
            from cv.detector import find_sudoku_grid, extract_cells_smart
            from cv.recognizer import SudokuRecognizer
        except ImportError as e:
            messagebox.showerror("Lỗi Import", f"Không thể nạp thư viện xử lý ảnh (OpenCV/Recognizer):\n{e}")
            self._update_explanation_box("Thiếu thư viện xử lý hình ảnh.")
            return

        onnx_path = os.path.join(app_dir, "models", "digit_model.onnx")
        if not os.path.exists(onnx_path):
            messagebox.showerror("Lỗi hệ thống", f"Không tìm thấy mô hình AI tại đường dẫn:\n{onnx_path}")
            self._update_explanation_box("Thiếu file mô hình AI ONNX.")
            return

        try:
            warped_grid = find_sudoku_grid(file_path, output_size=450)
            if warped_grid is None:
                raise ValueError("Không phát hiện thấy khung lưới Sudoku hợp lệ trong ảnh.")

            cells_9x9 = extract_cells_smart(warped_grid, output_size=450, margin=4)

            recognizer = SudokuRecognizer(model_path=onnx_path)
            detected_matrix = recognizer.recognize_grid(cells_9x9)

            self.sudoku_board.clear_all()
            for r in range(9):
                for c in range(9):
                    val = detected_matrix[r][c]
                    if val > 0:
                        self.sudoku_board.get_cell(r, c).set_value(val, is_original=True)

            self._update_explanation_box("Tải ảnh và nhận diện lưới Sudoku thành công.")
            self._on_cell_click(0, 0)

        except Exception as e:
            self._update_explanation_box(f"Thất bại trong quá trình nhận dạng: {e}")
            messagebox.showerror("Lỗi xử lý ảnh", f"Xử lý ảnh không thành công:\n{e}")

    def _update_explanation_box(self, text: str):
        """Cập nhật nội dung cho hộp thông báo bên dưới lưới số"""
        self.explanation_box.configure(state="normal")
        self.explanation_box.delete("0.0", "end")
        self.explanation_box.insert("0.0", text)
        self.explanation_box.configure(state="disabled")

    def _on_cell_click(self, row, col):
        """Xử lý sự kiện click ô thông minh (Phân biệt rõ nét màu highlight và nền)"""
        box_r, box_c = (row // 3) * 3, (col // 3) * 3
        
        for r in range(9):
            for c in range(9):
                cell = self.sudoku_board.get_cell(r, c)
                
                if r == row and c == col:
                    cell.highlight("#ADCFFF")
                elif r == row or c == col or (r // 3 == box_r // 3 and c // 3 == box_c // 3):
                    cell.highlight("#E5F1FF")
                else:
                    cell.reset_highlight()

        self.explanation_box.configure(state="normal")
        self.explanation_box.delete("0.0", "end")
        self.explanation_box.insert("0.0", f"Đã chọn ô ở Hàng {row + 1}, Cột {col + 1}.\nMàu xanh dương chỉ hiển thị ở vùng được chọn.")
        self.explanation_box.configure(state="disabled")

    def _on_reset(self):
        self.sudoku_board.clear_all()
        self.explanation_box.configure(state="normal")
        self.explanation_box.delete("0.0", "end")
        self.explanation_box.insert("0.0", "Đã làm sạch bảng. Hệ thống sẵn sàng.")
        self.explanation_box.configure(state="disabled")
        self.after(100, lambda: self._on_cell_click(0, 0))

if __name__ == "__main__":
    app = SudokuApp()
    app.mainloop()