#include "strategy_manager.hpp"
#include <vector>
#include <string>
#include <sstream>

namespace {
    // Hàm nội bộ trợ giúp tính nhanh chỉ số Block từ tọa độ (r, c)
    int GetBlockIndex(int r, int c) {
        return (r / 3) * 3 + (c / 3);
    }
}

// ========================================================================
// 1. THUẬT TOÁN: POINTING PAIRS/TRIPLES (CHỈ ĐIỂM)
// ========================================================================
HintResult FindPointing(SudokuGrid& grid) {
    // Duyệt qua 9 Block (0 đến 8)
    for (int blockIdx = 0; blockIdx < 9; ++blockIdx) {
        int startRow = (blockIdx / 3) * 3;
        int startCol = (blockIdx % 3) * 3;

        // Quét từng chữ số từ 1 đến 9
        for (int v = 1; v <= 9; ++v) {
            std::vector<std::pair<int, int>> cellsWithCand;

            // Tìm vị trí các ô trống trong Block hiện tại có chứa ứng viên v
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
            // Pointing chỉ xét khi ứng viên v xuất hiện trong đúng 2 hoặc 3 ô
            if (count < 2 || count > 3) continue;

            // TRƯỜNG HỢP A: Tất cả các ô này cùng nằm trên một Hàng (Row)
            bool sameRow = true;
            int targetRow = cellsWithCand[0].first;
            for (int i = 1; i < count; ++i) {
                if (cellsWithCand[i].first != targetRow) {
                    sameRow = false;
                    break;
                }
            }

            if (sameRow) {
                bool hasEliminated = false;
                // Loại trừ ứng viên v khỏi các ô khác thuộc Hàng này nằm NGOÀI Block hiện tại
                for (int col = 0; col < 9; ++col) {
                    if (GetBlockIndex(targetRow, col) != blockIdx) {
                        if (grid.cells[targetRow][col].value == 0 && grid.cells[targetRow][col].candidates[v]) {
                            grid.cells[targetRow][col].candidates[v] = false;
                            grid.cells[targetRow][col].candidateCount--;
                            hasEliminated = true;
                        }
                    }
                }

                if (hasEliminated) {
                    HintResult res;
                    res.found = true;
                    res.row = cellsWithCand[0].first;
                    res.col = cellsWithCand[0].second;
                    res.value = 0;
                    res.strategyName = "Pointing Row";

                    std::stringstream ss;
                    ss << "Trong Block " << blockIdx 
                       << ", so " << v << " chi co the nam tren Hang " << targetRow 
                       << " -> Da loai bo " << v << " khoi cac o khac tren hang nay ngoai Block.";
                    res.explanation = ss.str();
                    return res;
                }
            }

            // TRƯỜNG HỢP B: Tất cả các ô này cùng nằm trên một Cột (Column)
            bool sameCol = true;
            int targetCol = cellsWithCand[0].second;
            for (int i = 1; i < count; ++i) {
                if (cellsWithCand[i].second != targetCol) {
                    sameCol = false;
                    break;
                }
            }

            if (sameCol) {
                bool hasEliminated = false;
                // Loại trừ ứng viên v khỏi các ô khác thuộc Cột này nằm NGOÀI Block hiện tại
                for (int row = 0; row < 9; ++row) {
                    if (GetBlockIndex(row, targetCol) != blockIdx) {
                        if (grid.cells[row][targetCol].value == 0 && grid.cells[row][targetCol].candidates[v]) {
                            grid.cells[row][targetCol].candidates[v] = false;
                            grid.cells[row][targetCol].candidateCount--;
                            hasEliminated = true;
                        }
                    }
                }

                if (hasEliminated) {
                    HintResult res;
                    res.found = true;
                    res.row = cellsWithCand[0].first;
                    res.col = cellsWithCand[0].second;
                    res.value = 0;
                    res.strategyName = "Pointing Col";

                    std::stringstream ss;
                    ss << "[Pointing Col] Trong Block " << blockIdx 
                       << ", so " << v << " chi co the nam tren Cot " << targetCol 
                       << " -> Da loai bo " << v << " khoi cac o khac tren cot nay ngoai Block.";
                    res.explanation = ss.str();
                    return res;
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
            std::vector<int> colsWithCand;
            for (int c = 0; c < 9; ++c) {
                if (grid.cells[r][c].value == 0 && grid.cells[r][c].candidates[v]) {
                    colsWithCand.push_back(c);
                }
            }

            int count = colsWithCand.size();
            if (count < 2 || count > 3) continue;

            // Kiểm tra xem tất cả các ô chứa v của hàng r có cùng thuộc về một Block không
            int targetBlock = GetBlockIndex(r, colsWithCand[0]);
            bool sameBlock = true;
            for (int i = 1; i < count; ++i) {
                if (GetBlockIndex(r, colsWithCand[i]) != targetBlock) {
                    sameBlock = false;
                    break;
                }
            }

            if (sameBlock) {
                bool hasEliminated = false;
                int startRow = (targetBlock / 3) * 3;
                int startCol = (targetBlock % 3) * 3;

                // Xóa ứng viên v khỏi các hàng KHÁC nằm bên trong Block đó
                for (int i = 0; i < 3; ++i) {
                    for (int j = 0; j < 3; ++j) {
                        int br = startRow + i;
                        int bc = startCol + j;
                        if (br != r) { // Bỏ qua hàng r hiện tại
                            if (grid.cells[br][bc].value == 0 && grid.cells[br][bc].candidates[v]) {
                                grid.cells[br][bc].candidates[v] = false;
                                grid.cells[br][bc].candidateCount--;
                                hasEliminated = true;
                            }
                        }
                    }
                }

                if (hasEliminated) {
                    HintResult res;
                    res.found = true;
                    res.row = r;
                    res.col = colsWithCand[0];
                    res.value = 0;
                    res.strategyName = "Box/Line Reduction (Row)";

                    std::stringstream ss;
                    ss << "Tren Hang " << r << ", so " << v 
                       << " bat buoc phai nam trong Block " << targetBlock 
                       << " -> Da loai bo " << v << " khoi cac o khác cua Block nay.";
                    res.explanation = ss.str();
                    return res;
                }
            }
        }
    }

    // TRƯỜNG HỢP B: Quét từng CỘT để tìm sự hội tụ vào một BLOCK
    for (int c = 0; c < 9; ++c) {
        for (int v = 1; v <= 9; ++v) {
            std::vector<int> rowsWithCand;
            for (int r = 0; r < 9; ++r) {
                if (grid.cells[r][c].value == 0 && grid.cells[r][c].candidates[v]) {
                    rowsWithCand.push_back(r);
                }
            }

            int count = rowsWithCand.size();
            if (count < 2 || count > 3) continue;

            int targetBlock = GetBlockIndex(rowsWithCand[0], c);
            bool sameBlock = true;
            for (int i = 1; i < count; ++i) {
                if (GetBlockIndex(rowsWithCand[i], c) != targetBlock) {
                    sameBlock = false;
                    break;
                }
            }

            if (sameBlock) {
                bool hasEliminated = false;
                int startRow = (targetBlock / 3) * 3;
                int startCol = (targetBlock % 3) * 3;

                // Xóa ứng viên v khỏi các cột KHÁC nằm bên trong Block đó
                for (int i = 0; i < 3; ++i) {
                    for (int j = 0; j < 3; ++j) {
                        int br = startRow + i;
                        int bc = startCol + j;
                        if (bc != c) { // Bỏ qua cột c hiện tại
                            if (grid.cells[br][bc].value == 0 && grid.cells[br][bc].candidates[v]) {
                                grid.cells[br][bc].candidates[v] = false;
                                grid.cells[br][bc].candidateCount--;
                                hasEliminated = true;
                            }
                        }
                    }
                }

                if (hasEliminated) {
                    HintResult res;
                    res.found = true;
                    res.row = rowsWithCand[0];
                    res.col = c;
                    res.value = 0;
                    res.strategyName = "Box/Line Reduction (Col)";

                    std::stringstream ss;
                    ss << "[Box/Line Col] Tren Cot " << c << ", so " << v 
                       << " bat buoc phai nam trong Block " << targetBlock 
                       << " -> Da loai bo " << v << " khoi cac o khác cua Block nay.";
                    res.explanation = ss.str();
                    return res;
                }
            }
        }
    }

    return HintResult{};
}