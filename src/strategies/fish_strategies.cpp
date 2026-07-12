#include "strategy_manager.hpp"
#include <vector>
#include <string>
#include <sstream>
#include <set>

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

// ========================================================================
// 2. THUẬT TOÁN: SWORDFISH (Nâng cấp của X-WING, CẤP ĐỘ 2)
// ========================================================================
HintResult FindSwordfish(SudokuGrid& grid) {
    for (int v = 1; v <= 9; ++v) {
        
        // -------------------------------------------------------------
        // TRƯỜNG HỢP A: SWORDFISH THEO HÀNG (ROW-BASED)
        // Tìm 3 hàng có ứng viên v nằm gom cụm trong đúng 3 cột chung
        // -------------------------------------------------------------
        std::vector<std::pair<int, std::vector<int>>> rowsWithCand;
        for (int r = 0; r < 9; ++r) {
            std::vector<int> cols;
            for (int c = 0; c < 9; ++c) {
                if (grid.cells[r][c].value == 0 && grid.cells[r][c].candidates[v]) {
                    cols.push_back(c);
                }
            }
            // Một hàng hợp lệ cho Swordfish phải chứa đúng 2 hoặc 3 ứng viên v
            if (cols.size() == 2 || cols.size() == 3) {
                rowsWithCand.push_back({r, cols});
            }
        }

        if (rowsWithCand.size() >= 3) {
            // Duyệt mọi tổ hợp chập 3 của các Hàng thỏa mãn
            for (size_t i = 0; i < rowsWithCand.size(); ++i) {
                for (size_t j = i + 1; j < rowsWithCand.size(); ++j) {
                    for (size_t k = j + 1; k < rowsWithCand.size(); ++k) {
                        
                        // Lấy hợp (Union) các cột của 3 hàng này
                        std::set<int> colUnion;
                        for (int c : rowsWithCand[i].second) colUnion.insert(c);
                        for (int c : rowsWithCand[j].second) colUnion.insert(c);
                        for (int c : rowsWithCand[k].second) colUnion.insert(c);

                        // Nếu tổng số cột xuất hiện của cả 3 hàng này đúng bằng 3
                        if (colUnion.size() == 3) {
                            std::vector<int> cols(colUnion.begin(), colUnion.end());
                            int r1 = rowsWithCand[i].first;
                            int r2 = rowsWithCand[j].first;
                            int r3 = rowsWithCand[k].first;

                            bool hasEliminated = false;
                            // Loại bỏ v khỏi 3 cột này ở các hàng khác
                            for (int r = 0; r < 9; ++r) {
                                if (r != r1 && r != r2 && r != r3) {
                                    for (int c : cols) {
                                        if (grid.cells[r][c].value == 0 && grid.cells[r][c].candidates[v]) {
                                            grid.cells[r][c].candidates[v] = false;
                                            grid.cells[r][c].candidateCount--;
                                            hasEliminated = true;
                                        }
                                    }
                                }
                            }

                            if (hasEliminated) {
                                HintResult res;
                                res.found = true;
                                res.row = r1;
                                res.col = cols[0];
                                res.value = 0;
                                res.strategyName = "Swordfish (Row)";

                                std::stringstream ss;
                                ss << "Tim thay Swordfish cua so " << v 
                                   << " tai cac Hang {" << r1 << ", " << r2 << ", " << r3 << "}"
                                   << " va phan bo tren các Cot {" << cols[0] << ", " << cols[1] << ", " << cols[2] << "}.\n"
                                   << "   -> Da loai bo " << v << " khoi cac o khac tren 3 Cot nay.";
                                res.explanation = ss.str();
                                return res;
                            }
                        }
                    }
                }
            }
        }

        // -------------------------------------------------------------
        // TRƯỜNG HỢP B: SWORDFISH THEO CỘT (COLUMN-BASED)
        // Tìm 3 cột có ứng viên v nằm gom cụm trong đúng 3 hàng chung
        // -------------------------------------------------------------
        std::vector<std::pair<int, std::vector<int>>> colsWithCand;
        for (int c = 0; c < 9; ++c) {
            std::vector<int> rows;
            for (int r = 0; r < 9; ++r) {
                if (grid.cells[r][c].value == 0 && grid.cells[r][c].candidates[v]) {
                    rows.push_back(r);
                }
            }
            if (rows.size() == 2 || rows.size() == 3) {
                colsWithCand.push_back({c, rows});
            }
        }

        if (colsWithCand.size() >= 3) {
            for (size_t i = 0; i < colsWithCand.size(); ++i) {
                for (size_t j = i + 1; j < colsWithCand.size(); ++j) {
                    for (size_t k = j + 1; k < colsWithCand.size(); ++k) {
                        
                        std::set<int> rowUnion;
                        for (int r : colsWithCand[i].second) rowUnion.insert(r);
                        for (int r : colsWithCand[j].second) rowUnion.insert(r);
                        for (int r : colsWithCand[k].second) rowUnion.insert(r);

                        if (rowUnion.size() == 3) {
                            std::vector<int> rows(rowUnion.begin(), rowUnion.end());
                            int c1 = colsWithCand[i].first;
                            int c2 = colsWithCand[j].first;
                            int c3 = colsWithCand[k].first;

                            bool hasEliminated = false;
                            for (int c = 0; c < 9; ++c) {
                                if (c != c1 && c != c2 && c != c3) {
                                    for (int r : rows) {
                                        if (grid.cells[r][c].value == 0 && grid.cells[r][c].candidates[v]) {
                                            grid.cells[r][c].candidates[v] = false;
                                            grid.cells[r][c].candidateCount--;
                                            hasEliminated = true;
                                        }
                                    }
                                }
                            }

                            if (hasEliminated) {
                                HintResult res;
                                res.found = true;
                                res.row = rows[0];
                                res.col = c1;
                                res.value = 0;
                                res.strategyName = "Swordfish (Col)";

                                std::stringstream ss;
                                ss << "Tim thay Swordfish cua so " << v 
                                   << " tai cac Cot {" << c1 << ", " << c2 << ", " << c3 << "}"
                                   << " va phan bo tren các Hang {" << rows[0] << ", " << rows[1] << ", " << rows[2] << "}.\n"
                                   << "   -> Da loai bo " << v << " khoi cac o khac tren 3 Hang nay.";
                                res.explanation = ss.str();
                                return res;
                            }
                        }
                    }
                }
            }
        }
    }
    return HintResult{};
}

// ========================================================================
// 3. THUẬT TOÁN: JELLYFISH (NHÓM FISH CẤP ĐỘ 3 - SỨA BIỂN)
// ========================================================================
HintResult FindJellyfish(SudokuGrid& grid) {
    for (int v = 1; v <= 9; ++v) {
        
        // -------------------------------------------------------------
        // TRƯỜNG HỢP A: JELLYFISH THEO HÀNG (ROW-BASED)
        // Tìm 4 hàng có ứng viên v nằm gom cụm trong đúng 4 cột chung
        // -------------------------------------------------------------
        std::vector<std::pair<int, std::vector<int>>> rowsWithCand;
        for (int r = 0; r < 9; ++r) {
            std::vector<int> cols;
            for (int c = 0; c < 9; ++c) {
                if (grid.cells[r][c].value == 0 && grid.cells[r][c].candidates[v]) {
                    cols.push_back(c);
                }
            }
            // Một hàng hợp lệ cho Jellyfish phải chứa từ 2 đến 4 ứng viên v
            if (cols.size() >= 2 && cols.size() <= 4) {
                rowsWithCand.push_back({r, cols});
            }
        }

        if (rowsWithCand.size() >= 4) {
            // Duyệt mọi tổ hợp chập 4 của các Hàng thỏa mãn (i, j, k, l)
            for (size_t i = 0; i < rowsWithCand.size(); ++i) {
                for (size_t j = i + 1; j < rowsWithCand.size(); ++j) {
                    for (size_t k = j + 1; k < rowsWithCand.size(); ++k) {
                        for (size_t l = k + 1; l < rowsWithCand.size(); ++l) {
                            
                            // Lấy hợp (Union) các cột của 4 hàng này
                            std::set<int> colUnion;
                            for (int c : rowsWithCand[i].second) colUnion.insert(c);
                            for (int c : rowsWithCand[j].second) colUnion.insert(c);
                            for (int c : rowsWithCand[k].second) colUnion.insert(c);
                            for (int c : rowsWithCand[l].second) colUnion.insert(c);

                            // Nếu tổng số cột xuất hiện của cả 4 hàng này đúng bằng 4
                            if (colUnion.size() == 4) {
                                std::vector<int> cols(colUnion.begin(), colUnion.end());
                                int r1 = rowsWithCand[i].first;
                                int r2 = rowsWithCand[j].first;
                                int r3 = rowsWithCand[k].first;
                                int r4 = rowsWithCand[l].first;

                                bool hasEliminated = false;
                                // Loại bỏ v khỏi 4 cột này ở các hàng khác nằm ngoài Jellyfish
                                for (int r = 0; r < 9; ++r) {
                                    if (r != r1 && r != r2 && r != r3 && r != r4) {
                                        for (int c : cols) {
                                            if (grid.cells[r][c].value == 0 && grid.cells[r][c].candidates[v]) {
                                                grid.cells[r][c].candidates[v] = false;
                                                grid.cells[r][c].candidateCount--;
                                                hasEliminated = true;
                                            }
                                        }
                                    }
                                }

                                if (hasEliminated) {
                                    HintResult res;
                                    res.found = true;
                                    res.row = r1;
                                    res.col = cols[0];
                                    res.value = 0;
                                    res.strategyName = "Jellyfish (Row)";

                                    std::stringstream ss;
                                    ss << "Tim thay Jellyfish cua so " << v 
                                       << " tai cac Hang {" << r1 << ", " << r2 << ", " << r3 << ", " << r4 << "}"
                                       << " phan bo tren cac Cot {" << cols[0] << ", " << cols[1] << ", " << cols[2] << ", " << cols[3] << "}.\n"
                                       << "   -> Da loai bo " << v << " khoi cac o khac tren 4 Cot nay.";
                                    res.explanation = ss.str();
                                    return res;
                                }
                            }
                        }
                    }
                }
            }
        }

        // -------------------------------------------------------------
        // TRƯỜNG HỢP B: JELLYFISH THEO CỘT (COLUMN-BASED)
        // Tìm 4 cột có ứng viên v nằm gom cụm trong đúng 4 hàng chung
        // -------------------------------------------------------------
        std::vector<std::pair<int, std::vector<int>>> colsWithCand;
        for (int c = 0; c < 9; ++c) {
            std::vector<int> rows;
            for (int r = 0; r < 9; ++r) {
                if (grid.cells[r][c].value == 0 && grid.cells[r][c].candidates[v]) {
                    rows.push_back(r);
                }
            }
            if (rows.size() >= 2 && rows.size() <= 4) {
                colsWithCand.push_back({c, rows});
            }
        }

        if (colsWithCand.size() >= 4) {
            for (size_t i = 0; i < colsWithCand.size(); ++i) {
                for (size_t j = i + 1; j < colsWithCand.size(); ++j) {
                    for (size_t k = j + 1; k < colsWithCand.size(); ++k) {
                        for (size_t l = k + 1; l < colsWithCand.size(); ++l) {
                            
                            std::set<int> rowUnion;
                            for (int r : colsWithCand[i].second) rowUnion.insert(r);
                            for (int r : colsWithCand[j].second) rowUnion.insert(r);
                            for (int r : colsWithCand[k].second) rowUnion.insert(r);
                            for (int r : colsWithCand[l].second) rowUnion.insert(r);

                            if (rowUnion.size() == 4) {
                                std::vector<int> rows(rowUnion.begin(), rowUnion.end());
                                int c1 = colsWithCand[i].first;
                                int c2 = colsWithCand[j].first;
                                int c3 = colsWithCand[k].first;
                                int c4 = colsWithCand[l].first;

                                bool hasEliminated = false;
                                for (int c = 0; c < 9; ++c) {
                                    if (c != c1 && c != c2 && c != c3 && c != c4) {
                                        for (int r : rows) {
                                            if (grid.cells[r][c].value == 0 && grid.cells[r][c].candidates[v]) {
                                                grid.cells[r][c].candidates[v] = false;
                                                grid.cells[r][c].candidateCount--;
                                                hasEliminated = true;
                                            }
                                        }
                                    }
                                }

                                if (hasEliminated) {
                                    HintResult res;
                                    res.found = true;
                                    res.row = rows[0];
                                    res.col = c1;
                                    res.value = 0;
                                    res.strategyName = "Jellyfish (Col)";

                                    std::stringstream ss;
                                    ss << "Tim thay Jellyfish cua so " << v 
                                       << " tai cac Cot {" << c1 << ", " << c2 << ", " << c3 << ", " << c4 << "}"
                                       << " phan bo tren cac Hang {" << rows[0] << ", " << rows[1] << ", " << rows[2] << ", " << rows[3] << "}.\n"
                                       << "   -> Da loai bo " << v << " khoi cac o khac tren 4 Hang nay.";
                                    res.explanation = ss.str();
                                    return res;
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    return HintResult{};
}