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
 * (ví dụ: sudoku_solver_cpp.cp312-win_amd64.pyd) sẽ được tạo ra trong thư mục "build/".
 * Để nạp module này trong Python, hãy đặt tệp tin này cạnh mã nguồn Python chính
 * hoặc bổ sung đường dẫn thư mục "build" vào "sys.path".
 * =====================================================================================
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h> // Tự động ánh xạ std::vector sang Python List, std::pair sang Tuple
#include "types.hpp"
#include "solver_engine.hpp"

namespace py = pybind11;

PYBIND11_MODULE(sudoku_solver_cpp, m) {
    m.doc() = "Pybind11 C++ Sudoku Solver Engine Module";

    // 1. Ánh xạ cấu trúc CandidateElimination sang Python
    py::class_<CandidateElimination>(m, "CandidateElimination")
        .def(py::init<>())
        .def_readonly("row", &CandidateElimination::row)
        .def_readonly("col", &CandidateElimination::col)
        .def_readonly("value", &CandidateElimination::value);

    // 2. Ánh xạ cấu trúc HintResult nâng cao sang Python
    py::class_<HintResult>(m, "HintResult")
        .def(py::init<>())
        .def_readonly("found", &HintResult::found)
        .def_readonly("strategy_name", &HintResult::strategyName)
        .def_readonly("explanation", &HintResult::explanation)
        .def_readonly("fill_row", &HintResult::fillRow)
        .def_readonly("fill_col", &HintResult::fillCol)
        .def_readonly("fill_value", &HintResult::fillValue)
        .def_readonly("pattern_cells", &HintResult::patternCells) // Trả về list of tuples dạng [(r1, c1), (r2, c2)]
        .def_readonly("eliminations", &HintResult::eliminations);  // Trả về list chứa các đối tượng CandidateElimination

    // 3. Ánh xạ lớp SolverEngine sang Python
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
             "In trạng thái bảng số hiện tại ra cửa sổ dòng lệnh C++")

        // Ánh xạ hàm lấy gợi ý từng bước (Nếu SolverEngine của bạn có hàm này)
        .def("get_next_hint", &SolverEngine::GetNextHint,
             "Phân tích trạng thái hiện tại và trả về bước gợi ý tối ưu tiếp theo")
             
        .def("remove_candidate", &SolverEngine::RemoveCandidate,
               "Xóa ứng cử viên");
}