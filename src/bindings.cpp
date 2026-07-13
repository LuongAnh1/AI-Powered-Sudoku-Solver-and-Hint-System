/*
 * =====================================================================================
 * HƯỚNG DẪN BIÊN DỊCH MODULE PYTHON CẦU NỐI (PYBIND11) TRÊN WINDOWS
 * =====================================================================================
 *
 * Để đảm bảo CMake nhận diện đúng môi trường ảo (venv) thay vì Python của MSYS2/Hệ thống,
 * hãy thực hiện quy trình biên dịch theo các bước dưới đây từ cửa sổ PowerShell:
 *
 * 1. Di chuyển vào thư mục build:
 *    cd build
 *
 * 2. Dọn sạch bộ nhớ đệm CMake cũ (Bắt buộc nếu cấu hình trước đó bị lỗi):
 *    Remove-Item -Recurse -Force *
 *
 * 3. Chạy cấu hình CMake, chỉ định rõ đường dẫn bộ thông dịch Python của môi trường ảo (venv):
 *    cmake -DPython_EXECUTABLE=..\venv\Scripts\python.exe ..
 *
 * 4. Tiến hành biên dịch thư viện động ở chế độ Release:
 *    cmake --build . --config Release
 *
 * Sau khi biên dịch thành công, một tệp tin thư viện động có phần mở rộng là ".pyd"
 * (ví dụ: sudoku_solver_cpp.cp311-win_amd64.pyd) sẽ được tạo ra trong thư mục "build/".
 * Để nạp module này trong Python, hãy đặt tệp tin này cạnh mã nguồn Python chính
 * hoặc bổ sung đường dẫn thư mục "build" vào "sys.path".
 * =====================================================================================
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h> // Hỗ trợ ánh xạ std::vector <-> Python List
#include "solver_engine.hpp"

namespace py = pybind11;

PYBIND11_MODULE(sudoku_solver_cpp, m) {
    m.doc() = "Pybind11 C++ Sudoku Solver Engine Module";

    // Ánh xạ lớp SolverEngine sang Python
    py::class_<SolverEngine>(m, "SolverEngine")
        .def(py::init<>()) // Khởi tạo constructor không tham số SolverEngine()
        
        .def("load_grid", &SolverEngine::LoadGrid, 
             "Nạp ma trận Sudoku đầu vào kích thước 9x9 (Số 0 đại diện ô trống)",
             py::arg("input"))
             
        .def("solve_full", &SolverEngine::SolveFull, 
             "Thực hiện giải toàn bộ lưới Sudoku bằng các thuật toán")
             
        .def("get_grid", &SolverEngine::GetGrid, 
             "Lấy ma trận kết quả hiện tại dưới dạng danh sách lồng 9x9 trong Python")
             
        .def("print_grid", &SolverEngine::PrintGrid, 
             "In trạng thái bảng số hiện tại ra cửa sổ dòng lệnh C++");
}