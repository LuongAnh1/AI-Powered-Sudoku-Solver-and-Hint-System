# AI-Powered Sudoku Solver - C++ Engine Developer Guide

Tài liệu này hướng dẫn chi tiết về kiến trúc mã nguồn của lõi thuật toán C++ (Engine) và quy trình chuẩn để bảo trì, tối ưu hóa hoặc thêm mới một chiến thuật giải Sudoku vào hệ thống.

---

## 1. Kiến trúc tách lớp (Layered Architecture)

Lõi C++ được thiết kế theo nguyên tắc Tách biệt mối quan tâm (Separation of Concerns) và Bất biến trạng thái khi truy vấn (Read-only Queries). Hệ thống chia làm 5 thành phần chính:

1. Thành phần Dữ liệu Lõi (`src/types.hpp`): Định nghĩa các cấu trúc dữ liệu nguyên thủy như Cell, Grid, RegionType (Enum) và cấu trúc dữ liệu đầu ra HintResult.
2. Thành phần Định dạng Hiển thị (`src/utils/hint_formatter`): Chuyên trách việc sinh chuỗi giải thích (explanation) dựa trên dữ liệu truyền vào. Lớp thuật toán không tự tạo văn bản giải thích trực tiếp để phục vụ khả năng bản địa hóa (đa ngôn ngữ) về sau.
3. Thành phần Chiến thuật (`src/strategies/`): Chứa các module thuật toán độc lập. Các hàm này nhận vào bảng SudokuGrid và chỉ đọc trạng thái để tìm kiếm mô hình logic, sau đó trả về cấu trúc HintResult.
4. Thành phần Orchestrator (`src/solver_engine`): Điều phối luồng chạy thác nước (Waterfall). Đây là nơi duy nhất thực hiện việc thay đổi trạng thái của lưới (PlaceValue, RemoveCandidate) khi nhận được phản hồi hành động từ HintResult.
5. Thành phần Cầu nối (`src/bindings.cpp`): Đăng ký xuất khẩu các lớp dữ liệu và hàm C++ sang Python qua thư viện Pybind11 dưới dạng file `.pyd`.

---

## 2. Quy tắc khi phát triển chiến thuật mới

Khi viết một hàm tìm kiếm chiến thuật giải mới (ví dụ: FindMyNewStrategy), cần tuân thủ các quy tắc sau để giữ tính nhất quán hệ thống:

Quy tắc 1: Không thay đổi Grid trực tiếp trong thuật toán
- Thuật toán chỉ thu thập tọa độ ô và giá trị cần xóa vào mảng elims kiểu `std::vector<CandidateElimination>`. Việc áp dụng xóa thực tế sẽ do Engine trung tâm hoặc Python đảm nhiệm sau khi nhận được HintResult.

Quy tắc 2: Tách biệt hoàn toàn ngôn ngữ hiển thị
- Khai báo một hàm định dạng tĩnh trong HintFormatter (ví dụ: `HintFormatter::MyNewStrategy(args)`), thực hiện định dạng chuỗi tại `hint_formatter.cpp`, và truyền kết quả đó vào hàm `Factory CreateEliminateHint`.

Quy tắc 3: Kiểm tra hành động thực tế (No-op Hint Prevention)
- Chỉ trả về trạng thái tìm thấy thành công (`found = true`) nếu mảng `elims` thực sự chứa ít nhất 1 phần tử để tránh việc lặp lại gợi ý không có tác dụng thực tế lên bảng.

---

## 3. Quy trình thêm một Chiến thuật mới

Ví dụ khi thêm chiến thuật "XY-Chain" vào hệ thống:

Bước A: Định nghĩa câu giải thích trong HintFormatter
1. Mở file `src/utils/hint_formatter.hpp` và khai báo hàm định dạng:
```cpp
static std::string XYChain(const std::vector<std::pair<int, int>>& chainCells, int v);
```

2. Mở file `src/utils/hint_formatter.cpp` và triển khai chi tiết việc ghép chuỗi:
```cpp
std::string HintFormatter::XYChain(const std::vector<std::pair<int, int>>& chainCells, int v) {
    return "Tìm thấy XY-Chain gồm " + std::to_string(chainCells.size()) + " ô... loại bỏ số " + std::to_string(v);
}
```

Bước B: Khai báo thuật toán trong Strategy Manager
- Mở file `src/strategies/strategy_manager.hpp` và khai báo nguyên mẫu hàm:
```cpp
HintResult FindXYChain(SudokuGrid& grid);
```

Bước C: Triển khai thuật toán
- Viết logic tìm kiếm trong file .cpp thích hợp trong thư mục `src/strategies/`. Khi tìm thấy mô hình thành công, thu thập các ô tạo thành mô hình vào mảng patternCells, các ứng viên cần xóa vào mảng `elims`. Gọi hàm Factory để trả về kết quả:
```cpp
std::string msg = HintFormatter::XYChain(chainCells, v);
return HintResult::CreateEliminateHint("XY-Chain", patternCells, elims, msg);
```

Bước D: Đăng ký vào Waterfall Orchestrator
- Mở file `src/solver_engine.cpp`, tìm đến hàm `GetNextHint()`. Chèn thuật toán của bạn vào tầng ưu tiên mong muốn trong mô hình thác nước:
```cpp
result = FindXYChain(grid); if (result.found) return result;
```

---

## 4. Quy trình Đăng ký cổng giao tiếp Pybind11 (Bindings)

Khi bổ sung bất kỳ hàm Thành viên (Getter/Setter) hoặc cấu trúc dữ liệu mới nào trong lớp `SolverEngine` mà phía Python cần gọi trực tiếp, bắt buộc phải đăng ký trong file `src/bindings.cpp`.

Quy tắc đăng ký:
1. Đối với cấu trúc dữ liệu mới: Đăng ký kiểu lớp (`py::class_<T>`) và định nghĩa các trường thuộc tính chỉ đọc/ghi thích hợp.
2. Đối với phương thức của SolverEngine: Đăng ký bằng hàm `.def("tên_hàm_python", &SolverEngine::TênHàmC++)`.

*Ví dụ:* Khi cần cho phép gọi hàm điền số và lấy thông tin ứng viên từ Python:
```cpp
py::class_<SolverEngine>(m, "SolverEngine")
    .def("place_value", &SolverEngine::PlaceValue, "Đặt số chính thức và lan truyền ràng buộc")
    .def("get_grid_candidates", &SolverEngine::GetGridCandidates, "Lấy toàn bộ số nháp hiện hành");
```

---

## 5. Hướng dẫn Biên dịch & Kiểm thử nhanh

Cách 1: Biên dịch kiểm thử tích hợp độc lập (C++ Console)
Chạy lệnh sau tại thư mục gốc để biên dịch file exe kiểm tra nhanh logic thuật toán mà không cần Python:
```bash
g++ -std=c++17 src/tests/test_runner.cpp src/solver_engine.cpp src/utils/hint_formatter.cpp src/strategies/*.cpp -o test_engine.exe
./test_engine.exe
```
*(Lưu ý: Nếu chạy lệnh trên trong Windows PowerShell và gặp lỗi wildcard không nhận diện được ký tự `*`, hãy chuyển sang sử dụng Git Bash hoặc liệt kê chi tiết các đường dẫn tệp tin `.cpp` cần biên dịch).*

Cách 2: Đóng gói thư viện động cho Python (.pyd)
Sử dụng CMake từ PowerShell để biên dịch và tự động liên kết tĩnh các thư viện chuẩn cho môi trường Windows:
```powershell
# Tạo thư mục build nếu chưa tồn tại và di chuyển vào trong
if (-not (Test-Path build)) { New-Item -ItemType Directory -Path build }
cd build
Remove-Item -Recurse -Force *
cmake -DPython_EXECUTABLE=..\venv\Scripts\python.exe ..
cmake --build . --config Release
```

### Chuyển file `.pyd` vào thư mục `app/`
Để ứng dụng GUI Python có thể nạp được module `sudoku_solver_cpp`, sao chép file `.pyd` vào thư mục `app/`:

```powershell
Copy-Item -Path .\Release\sudoku_solver_cpp.cp312-win_amd64.pyd -Destination ..\app\
```

Hoặc nếu bạn đang ở thư mục gốc của dự án sau khi build:
```powershell
Copy-Item -Path build\Release\sudoku_solver_cpp.cp312-win_amd64.pyd -Destination app\
```

Khi file đã ở trong `app/`, Python sẽ có thể import `sudoku_solver_cpp` trực tiếp từ `app/main.py` và các module GUI.
