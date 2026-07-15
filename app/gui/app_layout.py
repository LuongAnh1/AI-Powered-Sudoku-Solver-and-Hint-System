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
from hint_manager import SudokuHintManager

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class SudokuApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AI-Powered Sudoku Solver")
        # Chiều rộng 1280px tiêu chuẩn widescreen cực kỳ cân đối
        self.geometry("1280x700")
        self.resizable(False, False)
        
        self.configure(fg_color="#0F172A")
        
        # GIẢI PHÁP: Cột trái (0) và cột phải (2) cố định kích thước (weight=0) để giữ vị trí.
        # Chỉ cột giữa chứa Sudoku (1) co giãn (weight=1) để chiếm không gian trống và bảo vệ viền bảng số.
        self.grid_columnconfigure(0, weight=0, minsize=320) # Cột giải thích cố định bên trái
        self.grid_columnconfigure(1, weight=1, minsize=540) # Cột lưới Sudoku co giãn tự do ở giữa
        self.grid_columnconfigure(2, weight=0, minsize=380) # Cột điều khiển cố định bên phải
        self.grid_rowconfigure(0, weight=1)

        self._init_left_panel()   # Thiết lập cột trái (Thương hiệu + Giải thích)
        self._init_middle_panel() # Thiết lập cột giữa (Lưới Sudoku)
        self._init_right_panel()  # Thiết lập cột phải (Ảnh gốc & Điều khiển)
        
        # Khởi tạo Hint Manager quản lý các bước giải đã lập lịch
        self.hint_manager = SudokuHintManager(self.sudoku_board, self.explanation_box, self.btn_next)
        
        self.sudoku_board.register_cell_clicks(self._on_cell_click)
        
        # Khởi tạo vùng chọn mặc định ở ô (0, 0) ngay khi khởi chạy app
        self._on_cell_click(0, 0)

    def _init_left_panel(self):
        """Khởi tạo cột trái: Thêm bộ nhận diện thương hiệu (Branding) và Khung giải thích"""
        # Khung chứa dọc ghép cụm thương hiệu và giải thích làm một để căn chỉnh mượt mà
        left_container = ctk.CTkFrame(self, fg_color="transparent")
        left_container.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="ns")
        left_container.grid_rowconfigure(1, weight=1)
        left_container.grid_columnconfigure(0, weight=1)

        # ==========================================
        # 1. BỘ NHẬN DIỆN THƯƠNG HIỆU (BRANDING)
        # ==========================================
        self.branding_frame = ctk.CTkFrame(left_container, fg_color="transparent")
        self.branding_frame.grid(row=0, column=0, sticky="w", pady=(0, 15))
        
        self.brand_title_frame = ctk.CTkFrame(self.branding_frame, fg_color="transparent")
        self.brand_title_frame.grid(row=0, column=0, sticky="w")
        
        self.brand_title_1 = ctk.CTkLabel(
            self.brand_title_frame, 
            text="SUDOKU", 
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"), 
            text_color="#FFFFFF"
        )
        self.brand_title_1.grid(row=0, column=0, sticky="w")
        
        self.brand_title_2 = ctk.CTkLabel(
            self.brand_title_frame, 
            text=" AI", 
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"), 
            text_color="#38BDF8"
        )
        self.brand_title_2.grid(row=0, column=1, sticky="w")
        
        self.brand_subtitle = ctk.CTkLabel(
            self.branding_frame, 
            text="Logical Deduction Engine", 
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="normal"), 
            text_color="#64748B"
        )
        self.brand_subtitle.grid(row=1, column=0, sticky="w", pady=(2, 0))

        # ==========================================
        # 2. KHUNG GIẢI THÍCH (EXPLANATION CARD)
        # ==========================================
        self.explanation_card = ctk.CTkFrame(
            left_container, 
            width=300,
            height=500,
            fg_color="#1E293B", 
            corner_radius=16, 
            border_width=1, 
            border_color="#334155"
        )
        self.explanation_card.grid(row=1, column=0, sticky="nw")
        self.explanation_card.grid_propagate(False)
        
        # Cấu hình lưới 1 cột hệ thống duy nhất bên trong thẻ để triệt tiêu lỗi chèn ép chữ
        self.explanation_card.grid_columnconfigure(0, weight=1)
        self.explanation_card.grid_rowconfigure(1, weight=1)

        # Khung phụ chứa tiêu đề (Icon + Title) giúp căn lề chính xác
        self.header_frame = ctk.CTkFrame(self.explanation_card, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.header_frame.grid_columnconfigure(1, weight=1)

        self.explanation_icon = ctk.CTkLabel(
            self.header_frame, 
            text="✦", # Ngôi sao vector hiển thị an toàn không lỗi font trên Windows
            font=ctk.CTkFont(size=20), 
            text_color="#38BDF8"
        )
        self.explanation_icon.grid(row=0, column=0, padx=(0, 8), sticky="w")

        self.explanation_title = ctk.CTkLabel(
            self.header_frame, 
            text="Giải thích", 
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), 
            text_color="#38BDF8"
        )
        self.explanation_title.grid(row=0, column=1, sticky="w")

        # Hộp văn bản đơn cột, đảm bảo luôn cách đều hai rìa của thẻ đúng 20px
        self.explanation_box = ctk.CTkTextbox(
            self.explanation_card, 
            fg_color="transparent", 
            text_color="#E2E8F0", 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="normal"),
            border_width=0,
            wrap="word"
        )
        self.explanation_box.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        self.explanation_box.insert("0.0", "Hệ thống sẵn sàng. Nhấp chuột vào một ô hoặc chọn 'Nạp ảnh Sudoku'.")
        self.explanation_box.configure(state="disabled")

    def _init_middle_panel(self):
        """Khởi tạo cột giữa: Bảng Sudoku rộng rãi, không bị chèn ép hay lẹm viền"""
        middle_frame = ctk.CTkFrame(self, fg_color="transparent")
        # Giữ khoảng đệm cân đối xung quanh khu vực bảng số trung tâm
        middle_frame.grid(row=0, column=1, padx=10, pady=20, sticky="nsew")
        
        self.board_card = ctk.CTkFrame(
            middle_frame, 
            width=500, 
            height=500, 
            fg_color="#1E293B", 
            corner_radius=16,
            border_width=2,
            border_color="#2563EB"
        ) 
        self.board_card.place(relx=0.5, rely=0.5, anchor="center")
        self.board_card.grid_propagate(False)
        
        self.sudoku_board = SudokuBoard(self.board_card, width=485, height=485)
        self.sudoku_board.place(relx=0.5, rely=0.5, anchor="center")

    def _init_right_panel(self):
        """Khởi tạo cột phải: Khung ảnh gốc dịch phải và cụm nút điều khiển chính"""
        right_frame = ctk.CTkFrame(self, fg_color="transparent")
        right_frame.grid(row=0, column=2, padx=(10, 20), pady=20, sticky="nsew")
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        # Đã đồng bộ sửa đổi tên biến cục bộ thành thực thể self.right_card
        self.right_card = ctk.CTkFrame(
            right_frame, 
            fg_color="#1E293B", 
            corner_radius=16, 
            border_width=1, 
            border_color="#334155"
        )
        self.right_card.grid(row=0, column=0, sticky="nsew")
        self.right_card.grid_rowconfigure(1, weight=1)
        self.right_card.grid_columnconfigure(0, weight=1)

        self.image_title = ctk.CTkLabel(
            self.right_card, 
            text="🖼️  ẢNH SUDOKU GỐC", 
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), 
            text_color="#38BDF8"
        )
        self.image_title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        self.image_container = ctk.CTkFrame(
            self.right_card, 
            fg_color="#0F172A", 
            corner_radius=12, 
            border_width=1, 
            border_color="#334155"
        )
        self.image_container.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

        self.image_preview_label = ctk.CTkLabel(
            self.image_container, 
            text="Chưa có ảnh được nạp\n\nNhấp chọn nút bên dưới để tải tệp lên", 
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#64748B"
        )
        self.image_preview_label.place(relx=0.5, rely=0.5, anchor="center")

        control_frame = ctk.CTkFrame(self.right_card, fg_color="transparent")
        control_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        control_frame.grid_columnconfigure(0, weight=1)
        control_frame.grid_columnconfigure(1, weight=1)

        button_font = ctk.CTkFont(family="Segoe UI", size=13, weight="bold")

        self.btn_load = ctk.CTkButton(
            control_frame, 
            text="Nạp ảnh Sudoku", 
            height=38,
            font=button_font,
            fg_color="#2563EB", 
            hover_color="#1D4ED8",
            corner_radius=8,
            command=self._on_load_image
        )
        self.btn_load.grid(row=0, column=0, columnspan=2, padx=5, pady=4, sticky="ew")

        self.btn_solve = ctk.CTkButton(
            control_frame, 
            text="⚡  Giải nhanh", 
            height=38,
            font=button_font,
            fg_color="#10B981", 
            hover_color="#059669",
            corner_radius=8,
            command=self._on_quick_solve
        )
        self.btn_solve.grid(row=1, column=0, padx=5, pady=4, sticky="ew")

        self.btn_next = ctk.CTkButton(
            control_frame, 
            text="💡  Gợi ý kế tiếp", 
            height=38,
            font=button_font,
            fg_color="#F97316", 
            hover_color="#EA580C",
            corner_radius=8,
            command=self._on_next_hint
        )
        self.btn_next.grid(row=1, column=1, padx=5, pady=4, sticky="ew")

        self.btn_reset = ctk.CTkButton(
            control_frame, 
            text="🔄  Làm mới bảng", 
            height=38,
            font=button_font,
            fg_color="#EF4444", 
            hover_color="#DC2626",
            corner_radius=8,
            command=self._on_reset
        )
        self.btn_reset.grid(row=2, column=0, columnspan=2, padx=5, pady=4, sticky="ew")

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

        self.hint_manager.invalidate_engine()

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
                raise ValueError("Không phát hiện thấy lưới Sudoku hợp lệ trong ảnh.")

            cells_9x9 = extract_cells_smart(warped_grid, output_size=450, margin=4)

            recognizer = SudokuRecognizer(model_path=onnx_path)
            detected_matrix = recognizer.recognize_grid(cells_9x9)

            self.sudoku_board.clear_all()
            for r in range(9):
                for c in range(9):
                    val = detected_matrix[r][c]
                    if val > 0:
                        self.sudoku_board.get_cell(r, c).set_value(val, is_original=True)

            self._update_explanation_box("Đang phân tích và lập lịch trình giải trước từ đề bài nhận dạng được...")
            self.update_idletasks()

            self.hint_manager.prepare_solution_chain()
            
            chain_len = len(self.hint_manager.hint_chains)
            if chain_len > 0:
                self._update_explanation_box(
                    f"Nhận dạng ảnh thành công và lập lịch trước {chain_len} bước giải logic.\n"
                    "Nhấn 'Gợi ý kế tiếp' để xem từng bước phân tích."
                )
            else:
                self._update_explanation_box(
                    "Nhận dạng ảnh thành công nhưng không thể tự động lập lịch giải.\n"
                    "Có thể đề bài không có lời giải logic duy nhất hoặc cần thuật toán quay lui."
                )

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

    def _on_next_hint(self):
        """Gọi xử lý bước gợi ý kế tiếp thông qua bộ điều phối HintManager"""
        self.hint_manager.handle_next_hint()

    def _on_quick_solve(self):
        """Giải nhanh toàn bộ các ô số chính thức dựa trên bộ lịch trình giải trước"""
        if not self._has_board_data():
            messagebox.showwarning("Bảng trống", "Không có dữ liệu đề bài để tiến hành giải nhanh.")
            return
        self.hint_manager.quick_solve()

    def _on_cell_click(self, row, col):
        """Xử lý sự kiện click ô thông minh (Phân biệt rõ nét màu highlight và nền)"""
        if self.hint_manager.state == "SHOWING_HINT":
            self.hint_manager.reset_state()

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
        self.explanation_box.insert("0.0", f"Đã chọn ô ở Hàng {row + 1}, Cột {col + 1}.\nMàu xanh dương chỉ hiển thị ô và các ô cùng hàng, cùng cột, cùng khối 3x3 với ô đang được chọn.")
        self.explanation_box.configure(state="disabled")

    def _on_reset(self):
        self.hint_manager.invalidate_engine()
        
        self.sudoku_board.clear_all()
        self.explanation_box.configure(state="normal")
        self.explanation_box.delete("0.0", "end")
        self.explanation_box.insert("0.0", "Đã làm sạch bảng. Hệ thống sẵn sàng.")
        self.explanation_box.configure(state="disabled")
        self.after(100, lambda: self._on_cell_click(0, 0))

if __name__ == "__main__":
    app = SudokuApp()
    app.mainloop()