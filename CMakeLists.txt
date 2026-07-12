# 1. Yêu cầu phiên bản CMake tối thiểu để chạy dự án này
cmake_minimum_required(VERSION 3.15)

# 2. Đặt tên cho dự án và khai báo ngôn ngữ sử dụng (C++ - CXX)
project(SudokuSolverEngine LANGUAGES CXX)

# 3. Ép Compiler phải sử dụng chuẩn C++17 (chuẩn hiện đại, hỗ trợ nhiều tính năng mạnh)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 4. CHỈ ĐƯỜNG: Bảo Compiler nếu tìm file hpp thì hãy vào thư mục "src" tìm kiếm
include_directories(src)

# 5. ĐẶT BIẾN: Gom tất cả các file logic thuật toán vào một biến tên là ALGO_SOURCES
set(ALGO_SOURCES 
    src/solver_engine.cpp
    src/strategies/basic_strategies.cpp
    src/strategies/intersection_strategies.cpp
    src/strategies/fish_strategies.cpp
)

# 6. TẠO SẢN PHẨM: Tạo ra file chạy "sudoku_test.exe" bằng cách dịch file test_runner.cpp 
# và liên kết nó với các file thuật toán nằm trong biến ALGO_SOURCES ở trên
add_executable(sudoku_test 
    src/tests/test_runner.cpp 
    ${ALGO_SOURCES}
)