#include "solver_engine.hpp"
#include "strategies/strategy_manager.hpp"
#include <iostream>

SolverEngine::SolverEngine() {}

//======================== THỰC HIỆN XÓA BỎ ĐỀ XUẤT SAU KHI ĐIỀN SỐ =========================

// Hàm nội bộ: Xóa 1 đề xuất và giảm biến đếm
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
    if (value <= 0) return false;
    if (row < 0 || row >= 9 || col < 0 || col >= 9) return false;
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

// Nhận dữ liệu ma trận đầu vào (Số 0 là ô trống)
void SolverEngine::LoadGrid(const std::vector<std::vector<int>>& input) {
    for (int r = 0; r < 9; ++r) {
        for (int c = 0; c < 9; ++c) {
            if (input[r][c] != 0) {
                PlaceValue(r, c, input[r][c]);
            }
        }
    }
}

// In kết quả ra console
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

// Xuất ma trận kết quả hiện tại ra dạng vector 2D phục vụ Python
std::vector<std::vector<int>> SolverEngine::GetGrid() const {
    std::vector<std::vector<int>> output(9, std::vector<int>(9, 0));
    for (int r = 0; r < 9; ++r) {
        for (int c = 0; c < 9; ++c) {
            output[r][c] = grid.cells[r][c].value;
        }
    }
    return output;
}

//======================== HÀM GỢI Ý BƯỚC TIẾP THEO VÀ GIẢI TOÀN BỘ =========================

// Vòng lặp gợi ý theo mô hình "Thác nước" (Waterfall Model)
HintResult SolverEngine::GetNextHint() {
    HintResult result;

    // Cấp 1: Các thuật toán điền số chắc chắn (Singles)
    result = FindNakedSingle(grid); if (result.found) return result;
    result = FindHiddenSingle(grid); if (result.found) return result;

    // Cấp 2: Các cặp trùng (Naked & Hidden Pairs)
    result = FindNakedPairs(grid); if (result.found) return result;
    result = FindHiddenPairs(grid); if (result.found) return result;

    // Cấp 2.5: Pointing (Chiến thuật giao lộ đầu tiên)
    result = FindPointing(grid); if (result.found) return result;

    // Cấp 3: Bộ ba (Naked & Hidden Triples)
    result = FindNakedTriples(grid); if (result.found) return result;
    result = FindHiddenTriples(grid); if (result.found) return result;

    // Cấp 3.5: Box/Line Reduction (Chiến thuật giao lộ nâng cao)
    result = FindBoxLineReduction(grid); if (result.found) return result;

    // Cấp 4: Bộ bốn (Naked & Hidden Quads)
    result = FindNakedQuads(grid); if (result.found) return result;
    result = FindHiddenQuads(grid); if (result.found) return result;

    // Cấp 5: Các chiến thuật nâng cao (Fish & Wings)
    result = FindXWing(grid); if (result.found) return result;
    result = FindSwordfish(grid); if (result.found) return result;
    result = FindJellyfish(grid); if (result.found) return result;
    result = FindXYWing(grid); if (result.found) return result;
    result = FindXYZWing(grid); if (result.found) return result;

    return result; 
}

// Giải toàn bộ bảng
void SolverEngine::SolveFull() {
    while (grid.emptyCount > 0) {
        HintResult hint = GetNextHint();
        if (hint.found) {
            std::cout << "[" << hint.strategyName << "] " << hint.explanation << "\n";
            
            // 1. Thực hiện điền số chính thức nếu có
            if (hint.fillValue > 0) {
                PlaceValue(hint.fillRow, hint.fillCol, hint.fillValue);
            } 
            
            // 2. Đồng thời áp dụng loại bỏ các ứng viên nhỏ khỏi lưới bộ nhớ để cập nhật trạng thái
            if (!hint.eliminations.empty()) {
                std::cout << "   -> Tien hanh loai bo " << hint.eliminations.size() << " ung vien nho.\n";
                for (const auto& elim : hint.eliminations) {
                    RemoveCandidate(elim.row, elim.col, elim.value);
                }
            }
        } else {
            std::cout << "Be tac! Can them thuat toan nang cao.\n";
            break;
        }
    }
    PrintGrid();
}

// Lấy danh sách ứng cử viên hiện có của một ô cụ thể
std::vector<int> SolverEngine::GetCellCandidates(int row, int col) const {
    std::vector<int> activeCandidates;
    if (row < 0 || row >= 9 || col < 0 || col >= 9) return activeCandidates;
    
    // Nếu ô đã điền số thì không còn ứng cử viên nháp nào cả
    if (grid.cells[row][col].value != 0) return activeCandidates;

    for (int i = 1; i <= 9; ++i) {
        if (grid.cells[row][col].candidates[i]) {
            activeCandidates.push_back(i);
        }
    }
    return activeCandidates;
}

// Lấy toàn bộ ứng cử viên nháp của 81 ô dưới dạng mảng 3 chiều (phù hợp đổ lên GUI một lần duy nhất)
std::vector<std::vector<std::vector<int>>> SolverEngine::GetGridCandidates() const {
    std::vector<std::vector<std::vector<int>>> allCandidates(9, std::vector<std::vector<int>>(9));
    for (int r = 0; r < 9; ++r) {
        for (int c = 0; c < 9; ++c) {
            if (grid.cells[r][c].value == 0) {
                for (int i = 1; i <= 9; ++i) {
                    if (grid.cells[r][c].candidates[i]) {
                        allCandidates[r][c].push_back(i);
                    }
                }
            }
        }
    }
    return allCandidates;
}