cmake_minimum_required(VERSION 3.15)
project(SudokuSolverEngine LANGUAGES CXX)

# Yêu cầu chuẩn C++17 trở lên
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Tìm gói pybind11 đã cài từ pip ở trên để làm cầu nối C++/Python
find_package(pybind11 REQUIRED)

# Khai báo file nguồn C++
set(SOURCES 
    src/solver.cpp
)

# Tạo thư viện C++ có thể import được vào Python
pybind11_add_module(sudoku_engine ${SOURCES})

# (Tùy chọn) Tạo thêm file chạy độc lập C++ để bạn dễ test thuật toán trước
add_executable(sudoku_test src/main.cpp src/solver.cpp)