# Hướng dẫn Cài đặt Môi trường (Setup Guide)

Tài liệu này hướng dẫn chi tiết cách cài đặt trình biên dịch C++ (hỗ trợ C++17 trở lên), cấu hình hệ thống build CMake và cài đặt các thư viện Python cần thiết cho dự án.

---

## Bước 1: Cài đặt Trình biên dịch C++ & CMake

Tùy thuộc vào hệ điều hành bạn đang sử dụng, hãy cài đặt trình biên dịch theo hướng dẫn dưới đây:

### 1. Trên Windows (Khuyên dùng MSYS2)
Chúng ta sẽ cài đặt bộ biên dịch **GCC/G++ (MinGW-w64)** thông qua **MSYS2** để tương thích tốt nhất với CMake:
1.  Tải và cài đặt MSYS2 từ trang chủ: [msys2.org](https://www.msys2.org/).
2.  Mở công cụ **MSYS2 UCRT64** từ Start Menu và chạy lệnh sau:
    ```bash
    pacman -S mingw-w64-ucrt-x86_64-gcc mingw-w64-ucrt-x86_64-cmake mingw-w64-ucrt-x86_64-make
    ```
3.  **Cấu hình biến môi trường (Environment Variables):**
    *   Thêm đường dẫn `C:\msys64\ucrt64\bin` vào biến môi trường `Path` của Windows để hệ thống nhận diện được lệnh `g++` và `cmake` từ CMD/PowerShell thông thường.

*(Hoặc tùy chọn khác: Cài đặt **Visual Studio Community** và chọn gói "Desktop development with C++" để sử dụng trình biên dịch MSVC).*

### 2. Trên Linux (Ubuntu/Debian)
Mở Terminal và chạy lệnh sau để cài đặt nhanh toàn bộ công cụ biên dịch và CMake:
```bash
sudo apt update
sudo apt install build-essential cmake g++ -y
```

### 3. Trên macOS
1.  Cài đặt **Command Line Tools** của Xcode bằng cách chạy lệnh sau trong Terminal:
    ```bash
    xcode-select --install
    ```
2.  Cài đặt **CMake** thông qua Homebrew (nếu chưa có Homebrew, cài đặt từ [brew.sh](https://brew.sh/)):
    ```bash
    brew install cmake
    ```

---

## Bước 2: Cài đặt môi trường Python & Thư viện

Sau khi đã có trình biên dịch C++, tiến hành tạo môi trường ảo Python và cài đặt các thư viện cần thiết.

1.  Mở Terminal/CMD tại thư mục gốc của dự án.
2.  Khởi tạo môi trường ảo Python:
    ```bash
    # Windows & Linux & macOS
    python -m venv venv
    ```
3.  Kích hoạt môi trường ảo (Xem hướng dẫn kích hoạt chi tiết cho từng hệ điều hành tại mục **Workflow** trong [README.md](README.md)).
4.  Cài đặt các thư viện từ file `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```
    *(Quá trình này sẽ tự động cài đặt OpenCV, NumPy, CustomTkinter và **pybind11** để làm cầu nối liên kết C++).*

---

## Bước 3: Biên dịch Lõi thuật toán C++ bằng CMake

Khi môi trường đã sẵn sàng, chúng ta tiến hành biên dịch mã nguồn C++ thành thư viện dùng được cho Python.

1.  Tại thư mục gốc dự án, tạo thư mục `build` và di chuyển vào trong:
    ```bash
    mkdir build
    cd build
    ```
2.  Cấu hình hệ thống và tiến hành biên dịch:
    ```bash
    # Cấu hình hệ thống build
    cmake ..

    # Tiến hành biên dịch (tạo ra file thư viện sudoku_engine)
    cmake --build .
    ```
    Sau khi biên dịch thành công, một file thư viện (có đuôi `.pyd` trên Windows hoặc `.so` trên Linux/macOS) sẽ được tạo ra trong thư mục `build`. Di chuyển file này vào thư mục `app/` để Python có thể `import` và sử dụng trực tiếp.