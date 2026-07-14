#include "strategy_manager.hpp"
#include <vector>
#include <set>

namespace {
    // Hàm đệ quy sinh tổ hợp (Combinations) chập K của mảng arr
    void getCombinations(const std::vector<std::pair<int, std::vector<int>>>& arr, int k, int start, 
                         std::vector<std::pair<int, std::vector<int>>>& current, 
                         std::vector<std::vector<std::pair<int, std::vector<int>>>>& result) {
        if (current.size() == k) {
            result.push_back(current);
            return;
        }
        for (size_t i = start; i < arr.size(); ++i) {
            current.push_back(arr[i]);
            getCombinations(arr, k, i + 1, current, result);
            current.pop_back();
        }
    }

    // Hàm tổng quát tìm nhóm Fish (X-Wing N=2, Swordfish N=3, Jellyfish N=4)
    HintResult FindFishOfSize(SudokuGrid& grid, int N, const std::string& fishName) {
        for (int v = 1; v <= 9; ++v) {
            
            // -------------------------------------------------------------
            // TRƯỜNG HỢP A: FISH THEO HÀNG (ROW-BASED)
            // -------------------------------------------------------------
            std::vector<std::pair<int, std::vector<int>>> rowsWithCand;
            for (int r = 0; r < 9; ++r) {
                std::vector<int> cols;
                for (int c = 0; c < 9; ++c) {
                    if (grid.cells[r][c].value == 0 && grid.cells[r][c].candidates[v]) cols.push_back(c);
                }
                if (cols.size() >= 2 && cols.size() <= N) rowsWithCand.push_back({r, cols});
            }

            if (rowsWithCand.size() >= N) {
                std::vector<std::vector<std::pair<int, std::vector<int>>>> combinations;
                std::vector<std::pair<int, std::vector<int>>> current;
                getCombinations(rowsWithCand, N, 0, current, combinations); // Sinh mọi tổ hợp chập N

                for (const auto& combo : combinations) {
                    std::set<int> colUnion;
                    std::vector<int> baseRows;
                    std::vector<std::pair<int, int>> patternCells; // Thu thập ô highlight

                    for (const auto& item : combo) {
                        baseRows.push_back(item.first);
                        for (int c : item.second) {
                            colUnion.insert(c);
                            patternCells.push_back({item.first, c});
                        }
                    }

                    if (colUnion.size() == N) {
                        std::vector<int> crossCols(colUnion.begin(), colUnion.end());
                        std::vector<CandidateElimination> elims;

                        // Xóa v khỏi các hàng khác trên các cột giao
                        for (int r = 0; r < 9; ++r) {
                            bool isBaseRow = false;
                            for (int br : baseRows) if (r == br) isBaseRow = true;
                            
                            if (!isBaseRow) {
                                for (int c : crossCols) {
                                    if (grid.cells[r][c].value == 0 && grid.cells[r][c].candidates[v]) {
                                        elims.push_back({r, c, v});
                                    }
                                }
                            }
                        }

                        if (!elims.empty()) {
                            std::string msg = HintFormatter::FishStrategy(fishName + " (Row)", v, RegionType::ROW, baseRows, crossCols);
                            return HintResult::CreateEliminateHint(fishName, patternCells, elims, msg);
                        }
                    }
                }
            }

            // -------------------------------------------------------------
            // TRƯỜNG HỢP B: FISH THEO CỘT (COLUMN-BASED)
            // -------------------------------------------------------------
            std::vector<std::pair<int, std::vector<int>>> colsWithCand;
            for (int c = 0; c < 9; ++c) {
                std::vector<int> rows;
                for (int r = 0; r < 9; ++r) {
                    if (grid.cells[r][c].value == 0 && grid.cells[r][c].candidates[v]) rows.push_back(r);
                }
                if (rows.size() >= 2 && rows.size() <= N) colsWithCand.push_back({c, rows});
            }

            if (colsWithCand.size() >= N) {
                std::vector<std::vector<std::pair<int, std::vector<int>>>> combinations;
                std::vector<std::pair<int, std::vector<int>>> current;
                getCombinations(colsWithCand, N, 0, current, combinations);

                for (const auto& combo : combinations) {
                    std::set<int> rowUnion;
                    std::vector<int> baseCols;
                    std::vector<std::pair<int, int>> patternCells;

                    for (const auto& item : combo) {
                        baseCols.push_back(item.first);
                        for (int r : item.second) {
                            rowUnion.insert(r);
                            patternCells.push_back({r, item.first});
                        }
                    }

                    if (rowUnion.size() == N) {
                        std::vector<int> crossRows(rowUnion.begin(), rowUnion.end());
                        std::vector<CandidateElimination> elims;

                        for (int c = 0; c < 9; ++c) {
                            bool isBaseCol = false;
                            for (int bc : baseCols) if (c == bc) isBaseCol = true;

                            if (!isBaseCol) {
                                for (int r : crossRows) {
                                    if (grid.cells[r][c].value == 0 && grid.cells[r][c].candidates[v]) {
                                        elims.push_back({r, c, v});
                                    }
                                }
                            }
                        }

                        if (!elims.empty()) {
                            std::string msg = HintFormatter::FishStrategy(fishName + " (Col)", v, RegionType::COLUMN, baseCols, crossRows);
                            return HintResult::CreateEliminateHint(fishName, patternCells, elims, msg);
                        }
                    }
                }
            }
        }
        return HintResult{};
    }
} // End anonymous namespace

// ========================================================================
// CÁC HÀM GỌI RA BÊN NGOÀI
// ========================================================================
HintResult FindXWing(SudokuGrid& grid) { return FindFishOfSize(grid, 2, "X-Wing"); }
HintResult FindSwordfish(SudokuGrid& grid) { return FindFishOfSize(grid, 3, "Swordfish"); }
HintResult FindJellyfish(SudokuGrid& grid) { return FindFishOfSize(grid, 4, "Jellyfish"); }