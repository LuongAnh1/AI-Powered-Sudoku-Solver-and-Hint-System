# Lệnh biên dịch
# cd build
# Remove-Item -Recurse -Force *
# cmake -DPython_EXECUTABLE=..\venv\Scripts\python.exe ..
# cmake --build . --config Release

# 1. Yêu cầu phiên bản CMake tối thiểu
cmake_minimum_required(VERSION 3.15)

# 2. Đặt tên cho dự án
project(SudokuSolverEngine LANGUAGES CXX)

# 3. Yêu cầu tiêu chuẩn C++17
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 4. Chỉ đường cho Compiler tìm kiếm file header (.hpp)
include_directories(src)

# 5. Khai báo các file mã nguồn thuật toán lõi
set(ALGO_SOURCES 
    src/solver_engine.cpp
    src/strategies/basic_strategies.cpp
    src/strategies/intersection_strategies.cpp
    src/strategies/fish_strategies.cpp
    src/strategies/wing_strategies.cpp
    src/utils/hint_formatter.cpp
)

# =========================================================
# PHẦN 1: BIÊN DỊCH BỘ KIỂM THỬ C++ ĐỘC LẬP (SUDOKU_TEST)
# =========================================================
add_executable(sudoku_test 
    src/tests/test_runner.cpp 
    ${ALGO_SOURCES}
)

# =========================================================
# PHẦN 2: BIÊN DỊCH MODULE PYTHON CẦU NỐI (PYBIND11)
# =========================================================

# Tự động tìm đường dẫn CMake của thư viện pybind11 đã cài trong môi trường Python hiện hành
execute_process(
    COMMAND python -c "import pybind11; print(pybind11.get_cmake_dir())"
    OUTPUT_VARIABLE pybind11_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
    ERROR_QUIET
)

if(pybind11_DIR)
    list(APPEND CMAKE_PREFIX_PATH "${pybind11_DIR}")
    
    set(PYBIND11_FINDPYTHON ON)
    find_package(pybind11 REQUIRED)
    
    pybind11_add_module(sudoku_solver_cpp
        src/bindings.cpp
        ${ALGO_SOURCES}
    )
    
    set_target_properties(sudoku_solver_cpp PROPERTIES
        PREFIX "${PYTHON_MODULE_PREFIX}"
        SUFFIX "${PYTHON_MODULE_EXTENSION}"
    )

    # =========================================================
    # CẤU HÌNH LIÊN KẾT TĨNH TRIỆT ĐỂ CHO COMPILER (MỚI BỔ SUNG)
    # =========================================================
    if(MINGW OR MSYS OR CMAKE_CXX_COMPILER_ID MATCHES "GNU" OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
        # Ép trình biên dịch nhúng tĩnh thư viện runtime của C++ (libstdc++-6.dll) và GCC (libgcc_s_seh-1.dll)
        target_link_options(sudoku_solver_cpp PRIVATE "-static-libgcc" "-static-libstdc++" "-static")
    endif()
    
else()
    message(WARNING "Không tìm thấy thư viện pybind11 trong môi trường Python.")
endif()