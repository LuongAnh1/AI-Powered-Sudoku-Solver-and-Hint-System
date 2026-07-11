#pragma once
#include <string>
#include <vector>

// Cấu trúc đại diện cho 1 ô trên bảng Sudoku (Thay thế cho struct SUDOKU của bạn)
struct Cell {
    int value = 0;              // 0 nghĩa là ô trống
    int candidateCount = 9;     // Số lượng đề xuất (tương đương biến 'sl')
    bool candidates[10];        // Mảng đề xuất từ 1-9 (tương đương biến 'kn')

    // Khởi tạo mặc định: Ô trống, tất cả các số 1-9 đều có khả năng
    Cell() {
        for (int i = 1; i <= 9; ++i) {
            candidates[i] = true;
        }
        candidates[0] = false;
    }
};

// Cấu trúc đại diện cho toàn bộ bảng Sudoku
struct SudokuGrid {
    Cell cells[9][9];
    int emptyCount = 81;        // Số ô trống mặc định
};

// Cấu trúc trả về khi hệ thống tìm được 1 gợi ý
struct HintResult {
    bool found = false;         // Có tìm được gợi ý nào không?
    int row = -1;
    int col = -1;
    int value = 0;              // Số cần điền (hoặc số bị xóa)
    std::string strategyName;   // Tên thuật toán đã dùng
    std::string explanation;    // Lời giải thích cho người dùng
};