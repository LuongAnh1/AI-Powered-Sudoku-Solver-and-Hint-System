# AI-Powered Sudoku Solver & Hint System

Dự án **Trình giải & Gợi ý Sudoku thông minh** kết hợp sức mạng xử lý hiệu năng cao của **C++ (Lõi thuật toán giải logic)** và sự linh hoạt của **Python (Thị giác máy tính OpenCV & Giao diện đồ họa CustomTkinter)**. 

Khác với các trình giải Sudoku thông thường chỉ đưa ra đáp án cuối cùng bằng thuật toán vét cạn (Backtracking), dự án này mô phỏng **tư duy suy luận logic của con người** (từ các cấp độ cơ bản như Naked/Hidden Singles cho đến nâng cao như Pointing, Box/Line Reduction, X-Wing, Swordfish, XY-Wing, XYZ-Wing...) để đưa ra **chỉ dẫn từng bước (Step-by-step Hint)** giúp người dùng học cách giải.

---

## ✨ Tính năng nổi bật

*   **Mô phỏng tư duy suy luận:** Trình bày gợi ý từng bước (Step-by-step Hint) kèm mô tả thuật toán chi tiết thay vì chỉ cung cấp đáp án thô.
*   **Tự động quản lý số nháp (Pencil Marks):** Tự động tính toán tập hợp ứng viên khả dĩ cho các ô trống và thực hiện **đồng bộ hai chiều thời gian thực** giữa giao diện Python và lõi C++ (đồng bộ ngược khi có thay đổi).
*   **Trực quan hóa mô hình bằng màu sắc:** Sử dụng hệ màu sắc phân biệt trực quan để tô màu mô hình logic áp dụng (Vàng), ô mục tiêu hành động điền số (Xanh lá) và các ứng viên nháp bị loại trừ (Đỏ).
*   **Giải nhanh thông minh (Quick Solve):** Hoàn thành bảng số ngay lập tức đồng thời xuất toàn bộ báo cáo phân tích logic chi tiết từng bước ra khung nhật ký để người dùng lưu vết.
*   **Thị giác máy tính (Computer Vision):** Nhận diện đề bài trực tiếp từ ảnh chụp Sudoku thông qua OpenCV và mô hình mạng Neural tích hợp ONNX.

---

## 🗺️ Kiến trúc Hệ thống

Hệ thống được thiết kế theo dạng đường ống (Pipeline) chia làm 3 khối độc lập:
1.  **UI/UX (Python/CustomTkinter):** Nhận tương tác, quản lý hiển thị lưới số nháp, số lớn và tô màu trạng thái gợi ý.
2.  **Computer Vision (Python/OpenCV):** Quét ảnh, định vị căn thẳng bảng 9x9 và nhận diện chữ số số hóa nạp vào bảng.
3.  **Core Algorithm Engine (C++17 & Pybind11):** Nhận ma trận số và thực hiện suy luận logic tốc độ cao thông qua cầu nối thư viện động `.pyd`.

---

## 📁 Cấu trúc Thư mục Dự án

Chi tiết sơ đồ các file và thư mục trong dự án được cập nhật tại file:
👉 **[Sơ đồ cấu trúc dự án tại structure.txt](structure.txt)**

---

## 💻 Phát triển & Tinh chỉnh Thuật toán C++ (Developer Guide)

Nếu bạn có nhu cầu đóng góp, bảo trì hoặc phát triển thêm các thuật toán logic mới cho lõi C++ (ví dụ: thêm các chiến thuật giải nâng cao hoặc thay đổi cách thức tối ưu hóa bộ nhớ), vui lòng tham khảo tài liệu hướng dẫn chi tiết dành riêng cho nhà phát triển tại:
👉 **[Hướng dẫn phát triển thuật toán tại src/DEVELOPER_GUIDE.md](src/DEVELOPER_GUIDE.md)**

---

## ⚙️ Hướng dẫn cài đặt ban đầu

Nếu đây là lần đầu tiên bạn tải dự án này về máy, vui lòng đọc và làm theo hướng dẫn cài đặt chi tiết (bao gồm cài trình biên dịch C++ và cấu hình CMake) tại:
👉 **[Hướng dẫn cài đặt chi tiết tại SETUP.md](SETUP.md)**

Biên dịch và sử dụng lõi tính toán C++ cùng GUI Python, build file `sudoku_solver_cpp.cp312-win_amd64.pyd` theo hướng dẫn trong:
👉 **[Developer Guide tại src/DEVELOPER_GUIDE.md](src/DEVELOPER_GUIDE.md) mục số 5**

Sau khi build, copy file `.pyd` vào thư mục `app/` để `python app/main.py` có thể import module `sudoku_solver_cpp`.

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

### 2. Khởi chạy ứng dụng (Run App)
Sau khi môi trường ảo đã được kích hoạt thành công, chạy lệnh sau từ thư mục gốc của dự án để khởi động giao diện đồ họa chính:
```bash
python app/main.py
```

### 3. Thoát khỏi môi trường ảo (Deactivate)
Khi đã làm việc xong và muốn quay về môi trường Python mặc định của hệ thống, chạy lệnh:
```bash
deactivate
```