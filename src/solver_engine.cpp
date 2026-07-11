#include "solver_engine.hpp"
#include "strategies/strategy_manager.hpp"
#include <iostream>

SolverEngine::SolverEngine() {}


//======================== THỰC HIỆN XÓA BỎ ĐỀ XUẤT SAU KHI ĐIỀN SỐ =========================

// Hàm nội bộ: Xóa 1 đề xuất và giảm biến đếm (Tương đương điều kiện phủ)
// Hàm con của PropagateConstraints
void SolverEngine::RemoveCandidate(int row, int col, int value) {
    if (grid.cells[row][col].value == 0 && grid.cells[row][col].candidates[value]) {
        grid.cells[row][col].candidates[value] = false;
        grid.cells[row][col].candidateCount--;
    }
}

// Hàm nội bộ: Xóa số vừa điền khỏi gợi ý trong Hàng, Cột và Block (Lan truyền ràng buộc)
void SolverEngine::PropagateConstraints(int row, int col, int value) {
    // Xóa số này khỏi mảng đề xuất của toàn bộ Hàng và Cột
    for (int i = 0; i < 9; ++i) {
        RemoveCandidate(row, i, value);
        RemoveCandidate(i, col, value);
    }

    // Xóa số này khỏi mảng đề xuất của Block 3x3 chứa nó
    int startRow = (row / 3) * 3;
    int startCol = (col / 3) * 3;
    for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) {
            RemoveCandidate(startRow + i, startCol + j, value);
        }
    }
}

// ======================== CÁC HÀM CHÍNH CỦA SOLVER ENGINE =========================

// Điền một số vào bảng (sau khi điền cần gọi PropagateConstraints để xóa các đề xuất liên quan)
bool SolverEngine::PlaceValue(int row, int col, int value) {
    if (grid.cells[row][col].value != 0) return false;

    grid.cells[row][col].value = value;
    grid.cells[row][col].candidateCount = 0;
    
    for (int i = 1; i <= 9; ++i) {
        grid.cells[row][col].candidates[i] = false;
    }

    grid.emptyCount--;
    PropagateConstraints(row, col, value);
    return true;
}

// Nhận dữ liệu ma trận đầu vào (Số 0 là ô trống), nếu ô đã có số thì gọi PlaceValue để điền và xóa các đề xuất liên quan
void SolverEngine::LoadGrid(const std::vector<std::vector<int>>& input) {
    for (int r = 0; r < 9; ++r) {
        for (int c = 0; c < 9; ++c) {
            if (input[r][c] != 0) {
                PlaceValue(r, c, input[r][c]);
            }
        }
    }
}

// In kết quả
void SolverEngine::PrintGrid() const {
    std::cout << "-----------------------\n";
    for (int r = 0; r < 9; ++r) {
        for (int c = 0; c < 9; ++c) {
            std::cout << grid.cells[r][c].value << " ";
            if (c == 2 || c == 5) std::cout << "| ";
        }
        std::cout << "\n";
        if (r == 2 || r == 5) std::cout << "-----------------------\n";
    }
    std::cout << "\n";
}

//======================== HÀM GỢI Ý BƯỚC TIẾP THEO VÀ GIẢI TOÁN BỘ =========================
// Vòng lặp gợi ý theo mô hình "Thác nước" (Waterfall Model) - Chưa có thuật toán nâng cao, chỉ dùng các thuật toán cơ bản
// Cần chỉnh sửa về sau 
HintResult SolverEngine::GetNextHint() {
    HintResult result;

    // Cấp 1: Tìm ô chỉ còn duy nhất 1 đề xuất
    result = FindNakedSingle(grid);
    if (result.found) return result;

    // Cấp 1: Tìm số chỉ có thể đứng ở 1 ô trong hàng/cột/block
    result = FindHiddenSingle(grid);
    if (result.found) return result;

    // TODO: Các cấp cao hơn (Naked Pairs, X-Wing) sẽ được gọi ở đây

    return result; // Trả về false nếu bế tắc
}

// Giải toàn bộ
void SolverEngine::SolveFull() {
    while (grid.emptyCount > 0) {
        HintResult hint = GetNextHint();
        if (hint.found) {
            std::cout << "[" << hint.strategyName << "] " << hint.explanation << "\n";
            PlaceValue(hint.row, hint.col, hint.value);
        } else {
            std::cout << "Bế tắc! Cần thêm thuật toán nâng cao.\n";
            break;
        }
    }
    PrintGrid();
}