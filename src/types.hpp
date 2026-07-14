#pragma once
#include <string>
#include <vector>
#include <utility> // Hỗ trợ std::pair

// Thêm vào đầu file src/types.hpp
enum class RegionType {
    ROW,
    COLUMN,
    BLOCK
};

// Cấu trúc đại diện cho 1 ô trên bảng Sudoku
struct Cell {
    int value = 0;              // 0 nghĩa là ô trống
    int candidateCount = 9;     // Số lượng ứng viên hiện tại (tương đương biến 'sl')
    bool candidates[10];        // Mảng ứng viên từ 1-9 (tương đương biến 'kn')

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

// Cấu trúc mô tả hành động xóa số đề xuất tại tọa độ cụ thể
struct CandidateElimination {
    int row = -1;
    int col = -1;
    int value = 0;              // Giá trị ứng viên nhỏ bị loại bỏ (1-9)
};

// Cấu trúc trả về chi tiết khi hệ thống tìm được 1 gợi ý (Phục vụ UI/UX Step-by-Step)
struct HintResult {
    bool found = false;
    std::string strategyName;
    std::string explanation;

    int fillRow = -1;
    int fillCol = -1;
    int fillValue = 0;
    std::vector<std::pair<int, int>> patternCells;
    std::vector<CandidateElimination> eliminations;

    // =========================================================================
    // CÁC HÀM FACTORY ĐỂ ĐÓNG GÓI LOGIC TẠO GỢI Ý (Tránh lặp code)
    // =========================================================================

    // 1. Hàm tạo gợi ý cho nhóm thuật toán Điền Số (Naked Single, Hidden Single)
        // Factory method bây giờ rất thuần túy, chỉ gán dữ liệu
    static HintResult CreateFillHint(const std::string& strategy, int r, int c, int val, const std::string& explanationText) {
        HintResult res;
        res.found = true;
        res.strategyName = strategy;
        res.fillRow = r;
        res.fillCol = c;
        res.fillValue = val;
        res.patternCells.push_back({r, c});
        res.explanation = explanationText; // Nhận chuỗi giải thích đã được format sẵn
        return res;
    }

    // 2. Hàm tạo gợi ý cho nhóm thuật toán Xóa Ứng Viên (Pairs, Triples, X-Wing...)
    static HintResult CreateEliminateHint(const std::string& strategy, 
                                          const std::vector<std::pair<int, int>>& pattern,
                                          const std::vector<CandidateElimination>& elims,
                                          const std::string& explanationText) {
        HintResult res;
        res.found = true;
        res.strategyName = strategy;
        res.patternCells = pattern;
        res.eliminations = elims;
        res.explanation = explanationText; // Với thuật toán phức tạp, text sẽ truyền từ ngoài vào
        return res;
    }
};