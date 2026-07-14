#include "strategy_manager.hpp"
#include <vector>

namespace {
    // Hàm nội bộ trợ giúp tính nhanh chỉ số Block từ tọa độ (r, c)
    int GetBlockIndex(int r, int c) {
        return (r / 3) * 3 + (c / 3);
    }
}

// ========================================================================
// 1. THUẬT TOÁN: POINTING (CHỈ ĐIỂM)
// ========================================================================
HintResult FindPointing(SudokuGrid& grid) {
    for (int blockIdx = 0; blockIdx < 9; ++blockIdx) {
        int startRow = (blockIdx / 3) * 3;
        int startCol = (blockIdx % 3) * 3;

        for (int v = 1; v <= 9; ++v) {
            std::vector<std::pair<int, int>> cellsWithCand; // Các ô dùng để highlight

            for (int i = 0; i < 3; ++i) {
                for (int j = 0; j < 3; ++j) {
                    int r = startRow + i;
                    int c = startCol + j;
                    if (grid.cells[r][c].value == 0 && grid.cells[r][c].candidates[v]) {
                        cellsWithCand.push_back({r, c});
                    }
                }
            }

            int count = cellsWithCand.size();
            if (count < 2 || count > 3) continue;

            // TRƯỜNG HỢP A: Tất cả các ô cùng nằm trên một HÀNG
            bool sameRow = true;
            int targetRow = cellsWithCand[0].first;
            for (int i = 1; i < count; ++i) {
                if (cellsWithCand[i].first != targetRow) { sameRow = false; break; }
            }

            if (sameRow) {
                std::vector<CandidateElimination> elims; // Mảng thu thập ứng viên bị xóa
                for (int col = 0; col < 9; ++col) {
                    if (GetBlockIndex(targetRow, col) != blockIdx) { // Nằm ngoài Block hiện tại
                        if (grid.cells[targetRow][col].value == 0 && grid.cells[targetRow][col].candidates[v]) {
                            elims.push_back({targetRow, col, v}); // Ghi nhận cần xóa
                        }
                    }
                }

                if (!elims.empty()) { // Nếu thực sự có ô bị xóa
                    std::string msg = HintFormatter::Pointing(blockIdx, RegionType::ROW, targetRow, v);
                    return HintResult::CreateEliminateHint("Pointing (Row)", cellsWithCand, elims, msg);
                }
            }

            // TRƯỜNG HỢP B: Tất cả các ô cùng nằm trên một CỘT
            bool sameCol = true;
            int targetCol = cellsWithCand[0].second;
            for (int i = 1; i < count; ++i) {
                if (cellsWithCand[i].second != targetCol) { sameCol = false; break; }
            }

            if (sameCol) {
                std::vector<CandidateElimination> elims;
                for (int row = 0; row < 9; ++row) {
                    if (GetBlockIndex(row, targetCol) != blockIdx) {
                        if (grid.cells[row][targetCol].value == 0 && grid.cells[row][targetCol].candidates[v]) {
                            elims.push_back({row, targetCol, v});
                        }
                    }
                }

                if (!elims.empty()) {
                    std::string msg = HintFormatter::Pointing(blockIdx, RegionType::COLUMN, targetCol, v);
                    return HintResult::CreateEliminateHint("Pointing (Col)", cellsWithCand, elims, msg);
                }
            }
        }
    }
    return HintResult{};
}

// ========================================================================
// 2. THUẬT TOÁN: BOX/LINE REDUCTION (THU GỌN KHỐI/ĐƯỜNG)
// ========================================================================
HintResult FindBoxLineReduction(SudokuGrid& grid) {
    
    // TRƯỜNG HỢP A: Quét từng HÀNG để tìm sự hội tụ vào một BLOCK
    for (int r = 0; r < 9; ++r) {
        for (int v = 1; v <= 9; ++v) {
            std::vector<std::pair<int, int>> cellsWithCand; // Highlight giao diện
            for (int c = 0; c < 9; ++c) {
                if (grid.cells[r][c].value == 0 && grid.cells[r][c].candidates[v]) {
                    cellsWithCand.push_back({r, c});
                }
            }

            int count = cellsWithCand.size();
            if (count < 2 || count > 3) continue;

            int targetBlock = GetBlockIndex(r, cellsWithCand[0].second);
            bool sameBlock = true;
            for (int i = 1; i < count; ++i) {
                if (GetBlockIndex(r, cellsWithCand[i].second) != targetBlock) { sameBlock = false; break; }
            }

            if (sameBlock) {
                std::vector<CandidateElimination> elims;
                int startRow = (targetBlock / 3) * 3;
                int startCol = (targetBlock % 3) * 3;

                // Xóa ứng viên v khỏi các hàng KHÁC nằm bên trong Block đó
                for (int i = 0; i < 3; ++i) {
                    for (int j = 0; j < 3; ++j) {
                        int br = startRow + i;
                        int bc = startCol + j;
                        if (br != r) { // Bỏ qua hàng r hiện tại
                            if (grid.cells[br][bc].value == 0 && grid.cells[br][bc].candidates[v]) {
                                elims.push_back({br, bc, v});
                            }
                        }
                    }
                }

                if (!elims.empty()) {
                    std::string msg = HintFormatter::BoxLineReduction(RegionType::ROW, r, targetBlock, v);
                    return HintResult::CreateEliminateHint("Box/Line Reduction (Row)", cellsWithCand, elims, msg);
                }
            }
        }
    }

    // TRƯỜNG HỢP B: Quét từng CỘT để tìm sự hội tụ vào một BLOCK
    for (int c = 0; c < 9; ++c) {
        for (int v = 1; v <= 9; ++v) {
            std::vector<std::pair<int, int>> cellsWithCand;
            for (int r = 0; r < 9; ++r) {
                if (grid.cells[r][c].value == 0 && grid.cells[r][c].candidates[v]) {
                    cellsWithCand.push_back({r, c});
                }
            }

            int count = cellsWithCand.size();
            if (count < 2 || count > 3) continue;

            int targetBlock = GetBlockIndex(cellsWithCand[0].first, c);
            bool sameBlock = true;
            for (int i = 1; i < count; ++i) {
                if (GetBlockIndex(cellsWithCand[i].first, c) != targetBlock) { sameBlock = false; break; }
            }

            if (sameBlock) {
                std::vector<CandidateElimination> elims;
                int startRow = (targetBlock / 3) * 3;
                int startCol = (targetBlock % 3) * 3;

                for (int i = 0; i < 3; ++i) {
                    for (int j = 0; j < 3; ++j) {
                        int br = startRow + i;
                        int bc = startCol + j;
                        if (bc != c) { // Bỏ qua cột c hiện tại
                            if (grid.cells[br][bc].value == 0 && grid.cells[br][bc].candidates[v]) {
                                elims.push_back({br, bc, v});
                            }
                        }
                    }
                }

                if (!elims.empty()) {
                    std::string msg = HintFormatter::BoxLineReduction(RegionType::COLUMN, c, targetBlock, v);
                    return HintResult::CreateEliminateHint("Box/Line Reduction (Col)", cellsWithCand, elims, msg);
                }
            }
        }
    }

    return HintResult{};
}