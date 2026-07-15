import customtkinter as ctk

class TestCell(ctk.CTkFrame):
    def __init__(self, master):
        # Tạo ô vuông xám, viền mỏng
        super().__init__(master, fg_color="#2b2b2b", corner_radius=0, border_width=1, border_color="#555")
        
        # Bắt buộc các thành phần bên trong giãn ra hết cỡ
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Chữ số hiển thị tạm (Điền sẵn số 0 để ô có kích thước thực tế, không bị sập)
        self.lbl = ctk.CTkLabel(self, text="0", font=("Arial", 18), text_color="#aaaaaa")
        self.lbl.grid(row=0, column=0, sticky="nsew")

class TestBoard(ctk.CTkFrame):
    def __init__(self, master):
        # Tạo khung nền đen đậm, viền ngoài cùng
        super().__init__(master, fg_color="#111", corner_radius=0, border_width=2, border_color="#111")
        
        # Chia 3x3 khối lớn
        for i in range(3):
            self.grid_rowconfigure(i, weight=1)
            self.grid_columnconfigure(i, weight=1)

        for sub_r in range(3):
            for sub_c in range(3):
                # Tạo 1 khối 3x3
                sub_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
                sub_frame.grid(row=sub_r, column=sub_c, sticky="nsew", padx=2, pady=2)
                
                # Chia 3x3 ô nhỏ bên trong khối
                for i in range(3):
                    sub_frame.grid_rowconfigure(i, weight=1)
                    sub_frame.grid_columnconfigure(i, weight=1)
                
                # Nhét 9 ô nhỏ vào
                for r in range(3):
                    for c in range(3):
                        cell = TestCell(sub_frame)
                        cell.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)

# --- CHẠY THỬ ĐỘC LẬP ---
if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("600x600")
    app.title("Test Lưới Độc Lập")
    
    # Ép bảng dãn ra theo cửa sổ chính, chừa lề 50px
    board = TestBoard(app)
    board.pack(expand=True, fill="both", padx=50, pady=50)
    
    app.mainloop()