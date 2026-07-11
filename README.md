# AI-Powered Sudoku Solver & Hint System

Dự án **Trình giải & Gợi ý Sudoku thông minh** kết hợp sức mạnh xử lý hiệu năng cao của **C++ (Thuật toán Engine)** và sự linh hoạt của **Python (Thị giác máy tính OpenCV & Giao diện UI)**. 

Khác với các trình giải Sudoku thông thường chỉ đưa ra đáp án cuối cùng bằng thuật toán vét cạn, dự án này mô phỏng **tư duy suy luận logic của con người** (như Naked/Hidden Pairs, Pointing, X-Wing...) để đưa ra **chỉ dẫn từng bước (Step-by-step Hint)** giúp người dùng học cách giải.

---

## 🗺️ Kiến trúc Hệ thống

Hệ thống được thiết kế theo dạng đường ống (Pipeline) chia làm 3 khối độc lập:
1.  **UI/UX (Python/CustomTkinter):** Nhận tương tác, hiển thị trực quan gợi ý hoặc đáp án chồng lên ảnh gốc.
2.  **Computer Vision (Python/OpenCV):** Quét ảnh/camera, định vị bảng 9x9 và nhận diện chữ số số hóa.
3.  **Core Algorithm Engine (C++17):** Nhận ma trận số và thực hiện suy luận logic tốc độ cao.

---

## 📁 Cấu trúc Thư mục Dự án

```text
Sudoku-Solver-Project/
├── README.md              # Giới thiệu và luồng làm việc hàng ngày
├── SETUP.md               # Hướng dẫn cài đặt môi trường chi tiết
├── requirements.txt       # Quản lý thư viện Python
├── CMakeLists.txt         # Quản lý biên dịch C++ (CMake)
├── src/                   # Lõi thuật toán C++
│   ├── main.cpp           # File chạy test độc lập C++
│   └── solver.cpp         # Định nghĩa các thuật toán giải logic
└── app/                   # Ứng dụng Python (UI & Computer Vision)
    └── main.py            # Giao diện và luồng xử lý ảnh chính
```

---

## ⚙️ Hướng dẫn cài đặt ban đầu

Nếu đây là lần đầu tiên bạn tải dự án này về máy, vui lòng đọc và làm theo hướng dẫn cài đặt chi tiết (bao gồm cài trình biên dịch C++ và cấu hình CMake) tại:
👉 **[Hướng dẫn cài đặt chi tiết tại SETUP.md](SETUP.md)**

---

## 🔄 Luồng làm việc hàng ngày (Workflow)

Sau khi đã hoàn tất cài đặt ở file `SETUP.md`, đây là các lệnh bạn sẽ sử dụng hàng ngày để làm việc với môi trường ảo Python của dự án:

### 1. Truy cập vào môi trường ảo (Activate)
Mỗi khi mở một Terminal mới để làm việc, hãy di chuyển vào thư mục dự án và chạy:

*   **Windows (CMD):**
    ```cmd
    .\venv\Scripts\activate
    ```
*   **Windows (PowerShell):**
    ```powershell
    .\venv\Scripts\Activate.ps1
    ```
*   **Linux / macOS:**
    ```bash
    source venv/bin/activate
    ```
*(Khi kích hoạt thành công, bạn sẽ thấy ký tự `(venv)` xuất hiện ở đầu dòng lệnh).*

### 2. Thoát khỏi môi trường ảo (Deactivate)
Khi đã làm việc xong và muốn quay về môi trường Python mặc định của hệ thống, chạy lệnh:
```bash
deactivate
```
*(Ký tự `(venv)` ở đầu dòng lệnh sẽ biến mất).*