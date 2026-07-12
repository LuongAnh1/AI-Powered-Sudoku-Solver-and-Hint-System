#include "strategy_manager.hpp"
#include <vector>
#include <string>
#include <sstream>

// ========================================================================
// 1. THUẬT TOÁN: X-WING (NHÓM FISH CẤP ĐỘ 1)
// ========================================================================
HintResult FindXWing(SudokuGrid& grid) {
    // Quét từng ứng viên từ 1 đến 9
    for (int v = 1; v <= 9; ++v) {
        
        // -------------------------------------------------------------
        // TRƯỜNG HỢP A: X-WING THEO HÀNG (ROW-BASED)
        // Tìm 2 hàng mà ứng viên v chỉ xuất hiện ở đúng 2 cột GIỐNG NHAU
        // -------------------------------------------------------------
        std::vector<std::pair<int, std::vector<int>>> rowsWithTwo;
        
        for (int r = 0; r < 9; ++r) {
            std::vector<int> cols;
            for (int c = 0; c < 9; ++c) {
                if (grid.cells[r][c].value == 0 && grid.cells[r][c].candidates[v]) {
                    cols.push_back(c);
                }
            }
            if (cols.size() == 2) {
                rowsWithTwo.push_back({r, cols});
            }
        }

        // Bắt cặp các hàng thỏa mãn điều kiện
        for (size_t i = 0; i < rowsWithTwo.size(); ++i) {
            for (size_t j = i + 1; j < rowsWithTwo.size(); ++j) {
                int r1 = rowsWithTwo[i].first;
                int r2 = rowsWithTwo[j].first;
                std::vector<int> cols1 = rowsWithTwo[i].second;
                std::vector<int> cols2 = rowsWithTwo[j].second;

                // Nếu 2 hàng này có ứng viên v nằm ở đúng 2 cột giống hệt nhau
                if (cols1[0] == cols2[0] && cols1[1] == cols2[1]) {
                    int c1 = cols1[0];
                    int c2 = cols1[1];
                    bool hasEliminated = false;

                    // Tiến hành loại trừ v khỏi các Hàng KHÁC trên 2 Cột này
                    for (int r = 0; r < 9; ++r) {
                        if (r != r1 && r != r2) {
                            if (grid.cells[r][c1].value == 0 && grid.cells[r][c1].candidates[v]) {
                                grid.cells[r][c1].candidates[v] = false;
                                grid.cells[r][c1].candidateCount--;
                                hasEliminated = true;
                            }
                            if (grid.cells[r][c2].value == 0 && grid.cells[r][c2].candidates[v]) {
                                grid.cells[r][c2].candidates[v] = false;
                                grid.cells[r][c2].candidateCount--;
                                hasEliminated = true;
                            }
                        }
                    }

                    if (hasEliminated) {
                        HintResult res;
                        res.found = true;
                        res.row = r1; // Chỉ định vị trí gốc để UI highlight (nếu cần)
                        res.col = c1;
                        res.value = 0;
                        res.strategyName = "X-Wing (Row)";

                        std::stringstream ss;
                        ss << "Tim thay X-Wing cua so " << v 
                           << " tai cac Hang " << r1 << " & " << r2 
                           << ", nam tren Cot " << c1 << " & " << c2 << ".\n"
                           << "   -> Da loai bo " << v << " khoi cac o khac tren 2 Cot nay.";
                        res.explanation = ss.str();
                        return res;
                    }
                }
            }
        }

        // -------------------------------------------------------------
        // TRƯỜNG HỢP B: X-WING THEO CỘT (COLUMN-BASED)
        // Tìm 2 cột mà ứng viên v chỉ xuất hiện ở đúng 2 hàng GIỐNG NHAU
        // -------------------------------------------------------------
        std::vector<std::pair<int, std::vector<int>>> colsWithTwo;

        for (int c = 0; c < 9; ++c) {
            std::vector<int> rows;
            for (int r = 0; r < 9; ++r) {
                if (grid.cells[r][c].value == 0 && grid.cells[r][c].candidates[v]) {
                    rows.push_back(r);
                }
            }
            if (rows.size() == 2) {
                colsWithTwo.push_back({c, rows});
            }
        }

        for (size_t i = 0; i < colsWithTwo.size(); ++i) {
            for (size_t j = i + 1; j < colsWithTwo.size(); ++j) {
                int c1 = colsWithTwo[i].first;
                int c2 = colsWithTwo[j].first;
                std::vector<int> rows1 = colsWithTwo[i].second;
                std::vector<int> rows2 = colsWithTwo[j].second;

                if (rows1[0] == rows2[0] && rows1[1] == rows2[1]) {
                    int r1 = rows1[0];
                    int r2 = rows1[1];
                    bool hasEliminated = false;

                    // Tiến hành loại trừ v khỏi các Cột KHÁC trên 2 Hàng này
                    for (int c = 0; c < 9; ++c) {
                        if (c != c1 && c != c2) {
                            if (grid.cells[r1][c].value == 0 && grid.cells[r1][c].candidates[v]) {
                                grid.cells[r1][c].candidates[v] = false;
                                grid.cells[r1][c].candidateCount--;
                                hasEliminated = true;
                            }
                            if (grid.cells[r2][c].value == 0 && grid.cells[r2][c].candidates[v]) {
                                grid.cells[r2][c].candidates[v] = false;
                                grid.cells[r2][c].candidateCount--;
                                hasEliminated = true;
                            }
                        }
                    }

                    if (hasEliminated) {
                        HintResult res;
                        res.found = true;
                        res.row = r1;
                        res.col = c1;
                        res.value = 0;
                        res.strategyName = "X-Wing (Col)";

                        std::stringstream ss;
                        ss << "Tim thay X-Wing cua so " << v 
                           << " tai cac Cot " << c1 << " & " << c2 
                           << ", nam tren Hang " << r1 << " & " << r2 << ".\n"
                           << "   -> Da loai bo " << v << " khoi cac o khac tren 2 Hang nay.";
                        res.explanation = ss.str();
                        return res;
                    }
                }
            }
        }
    }
    return HintResult{};
}