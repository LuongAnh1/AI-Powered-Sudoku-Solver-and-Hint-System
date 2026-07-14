#include "strategy_manager.hpp"
#include <sstream>
#include <iostream>

//==== CÁC THUẬT TOÁN ĐIỀN Ô TRỐNG CƠ BẢN (Basic Strategies) ====

// Thuật toán Naked Single: Ô chỉ còn duy nhất 1 sự lựa chọn
HintResult FindNakedSingle(SudokuGrid& grid) {
    for (int r = 0; r < 9; ++r) {
        for (int c = 0; c < 9; ++c) {
            if (grid.cells[r][c].value == 0 && grid.cells[r][c].candidateCount == 1) {
                for (int v = 1; v <= 9; ++v) {
                    if (grid.cells[r][c].candidates[v]) {
                        
                        // 1. Nhờ Formatter tạo câu giải thích
                        std::string msg = HintFormatter::NakedSingle(r, c, v);

                        // 2. Trả về kết quả thông qua Factory
                        return HintResult::CreateFillHint("Naked Single", r, c, v, msg);

                    }
                }
            }
        }
    }
    return HintResult();
}

// Thuật toán Hidden Single: Số chỉ có thể đứng ở 1 ô trong hàng/cột/block
HintResult FindHiddenSingle(SudokuGrid& grid) {
    for (int v = 1; v <= 9; ++v) {
        
        // 1. Quét theo HÀNG
        for (int r = 0; r < 9; ++r) {
            int possibleCount = 0;
            int targetC = -1;
            for (int c = 0; c < 9; ++c) {
                if (grid.cells[r][c].value == 0 && grid.cells[r][c].candidates[v]) {
                    possibleCount++;
                    targetC = c;
                }
            }
            if (possibleCount == 1) {
                // Chỉ truyền Enum ROW và chỉ số r
                std::string msg = HintFormatter::HiddenSingle(r, targetC, v, RegionType::ROW, r);
                return HintResult::CreateFillHint("Hidden Single (Row)", r, targetC, v, msg);
            }
        }

        // 2. Quét theo CỘT
        for (int c = 0; c < 9; ++c) {
            int possibleCount = 0;
            int targetR = -1;
            for (int r = 0; r < 9; ++r) {
                if (grid.cells[r][c].value == 0 && grid.cells[r][c].candidates[v]) {
                    possibleCount++;
                    targetR = r;
                }
            }
            if (possibleCount == 1) {
                // Chỉ truyền Enum COLUMN và chỉ số c
                std::string msg = HintFormatter::HiddenSingle(targetR, c, v, RegionType::COLUMN, c);
                return HintResult::CreateFillHint("Hidden Single (Column)", targetR, c, v, msg);
            }
        }

        // 3. Quét theo BLOCK 3x3
        for (int blockRow = 0; blockRow < 3; ++blockRow) {
            for (int blockCol = 0; blockCol < 3; ++blockCol) {
                int possibleCount = 0;
                int targetR = -1, targetC = -1;
                
                for (int i = 0; i < 3; ++i) {
                    for (int j = 0; j < 3; ++j) {
                        int r = blockRow * 3 + i;
                        int c = blockCol * 3 + j;
                        if (grid.cells[r][c].value == 0 && grid.cells[r][c].candidates[v]) {
                            possibleCount++;
                            targetR = r; 
                            targetC = c;
                        }
                    }
                }
                
                if (possibleCount == 1) {
                    int blockIndex = blockRow * 3 + blockCol;
                    // Chỉ truyền Enum BLOCK và chỉ số blockIndex
                    std::string msg = HintFormatter::HiddenSingle(targetR, targetC, v, RegionType::BLOCK, blockIndex);
                    return HintResult::CreateFillHint("Hidden Single (Block)", targetR, targetC, v, msg);
                }
            }
        }
    }
    
    return HintResult();
}

//==== CÁC THUẬT TOÁN LOẠI TRỪ ỨNG VIÊN - CẤP ĐỘ 1 ====

// sử dụng kỹ thuật Bitmask (Mặt nạ bit).
// Kỹ thuật này hoạt động bằng cách nhóm các ứng viên (từ 1 đến 9) thành một dãy bit. 
// Nếu xét 2 ô (Naked Pair), 3 ô (Naked Triple) hoặc 4 ô (Naked Quad) mà tổng số lượng bit ứng viên 
// gộp lại bằng đúng kích thước nhóm (2, 3 hoặc 4), 
// thì ta đã tìm ra mẫu logic 
// và tiến hành xóa các bit đó khỏi các ô trống khác trong cùng khu vực (Hàng/Cột/Block).

// Sử dụng namespace ẩn (anonymous namespace) để chứa các hàm nội bộ tiện ích
namespace {
    // Hàm chuyển mảng đề xuất thành dạng Bitmask
    // VD: Ô có đề xuất {2, 5} -> Bitmask: 000010010 (Nhị phân)
    int getCandidateMask(const Cell& cell) {
        int mask = 0;
        for (int i = 1; i <= 9; ++i) {
            if (cell.candidates[i]) mask |= (1 << i);
        }
        return mask;
    }

    // Đếm số lượng bit 1 trong Mask (Đếm số lượng ứng viên)
    int countBits(int mask) {
        int count = 0;
        while (mask) {
            count += (mask & 1);
            mask >>= 1;
        }
        return count;
    }

     // Hàm chuyển đổi integer 0,1,2 sang Enum
    RegionType getRegionType(int rt) {
        if (rt == 0) return RegionType::ROW;
        if (rt == 1) return RegionType::COLUMN;
        return RegionType::BLOCK;
    }

    // ========================================================================
    // TÌM NAKED SUBSETS (N = 2, 3, hoặc 4)
    // ========================================================================
    HintResult FindNakedSubset(SudokuGrid& grid, int N, const std::string& strategyName) {
        for (int regionType = 0; regionType < 3; ++regionType) {
            for (int regionIdx = 0; regionIdx < 9; ++regionIdx) {
                
                std::vector<std::pair<int, int>> emptyCells;
                for (int i = 0; i < 9; ++i) {
                    int r = (regionType == 0) ? regionIdx : (regionType == 1 ? i : (regionIdx / 3) * 3 + (i / 3));
                    int c = (regionType == 0) ? i : (regionType == 1 ? regionIdx : (regionIdx % 3) * 3 + (i % 3));
                    if (grid.cells[r][c].value == 0) emptyCells.push_back({r, c});
                }

                int numEmpty = emptyCells.size();
                if (numEmpty <= N) continue;

                for (int mask = 1; mask < (1 << numEmpty); ++mask) {
                    if (countBits(mask) == N) { 
                        
                        int candidateUnion = 0;
                        std::vector<std::pair<int, int>> subsetCells;

                        for (int i = 0; i < numEmpty; ++i) {
                            if ((mask >> i) & 1) {
                                subsetCells.push_back(emptyCells[i]);
                                candidateUnion |= getCandidateMask(grid.cells[emptyCells[i].first][emptyCells[i].second]);
                            }
                        }

                        if (countBits(candidateUnion) == N) {
                            // THAY VÌ SỬA GRID TRỰC TIẾP, TA THU THẬP DANH SÁCH CẦN XÓA
                            std::vector<CandidateElimination> elims;

                            for (int i = 0; i < numEmpty; ++i) {
                                if (((mask >> i) & 1) == 0) { // Ô KHÔNG nằm trong Subset
                                    int r = emptyCells[i].first;
                                    int c = emptyCells[i].second;
                                    for (int val = 1; val <= 9; ++val) {
                                        if (((candidateUnion >> val) & 1) && grid.cells[r][c].candidates[val]) {
                                            // Ghi nhận cần xóa số 'val' tại ô (r,c)
                                            elims.push_back({r, c, val}); 
                                        }
                                    }
                                }
                            }

                            // Chỉ trả về khi thực sự có ít nhất 1 ứng viên bị dọn dẹp
                            if (!elims.empty()) {
                                std::vector<int> subsetVals;
                                for (int v = 1; v <= 9; ++v) {
                                    if ((candidateUnion >> v) & 1) subsetVals.push_back(v);
                                }

                                std::string msg = HintFormatter::NakedSubset(strategyName, subsetVals, subsetCells, getRegionType(regionType), regionIdx);
                                return HintResult::CreateEliminateHint(strategyName, subsetCells, elims, msg);
                            }
                        }
                    }
                }
            }
        }
        return HintResult{};
    }

    // ========================================================================
    // TÌM HIDDEN SUBSETS (N = 2, 3, hoặc 4)
    // ========================================================================
    HintResult FindHiddenSubset(SudokuGrid& grid, int N, const std::string& strategyName) {
        for (int regionType = 0; regionType < 3; ++regionType) {
            for (int regionIdx = 0; regionIdx < 9; ++regionIdx) {
                
                int candPositions[10] = {0}; 
                std::pair<int, int> cellCoords[9]; 

                for (int i = 0; i < 9; ++i) {
                    int r = (regionType == 0) ? regionIdx : (regionType == 1 ? i : (regionIdx / 3) * 3 + (i / 3));
                    int c = (regionType == 0) ? i : (regionType == 1 ? regionIdx : (regionIdx % 3) * 3 + (i % 3));
                    cellCoords[i] = {r, c};

                    if (grid.cells[r][c].value == 0) {
                        for (int v = 1; v <= 9; ++v) {
                            if (grid.cells[r][c].candidates[v]) candPositions[v] |= (1 << i);
                        }
                    }
                }

                for (int digitMask = 2; digitMask < (1 << 10); digitMask += 2) {
                    if (countBits(digitMask) == N) { 
                        int positionUnion = 0; 
                        bool validCombination = true;

                        for (int v = 1; v <= 9; ++v) {
                            if ((digitMask >> v) & 1) {
                                if (candPositions[v] == 0) { validCombination = false; break; }
                                positionUnion |= candPositions[v];
                            }
                        }

                        if (!validCombination) continue;

                        if (countBits(positionUnion) == N) {
                            // THU THẬP DANH SÁCH CẦN XÓA
                            std::vector<CandidateElimination> elims;
                            std::vector<std::pair<int, int>> subsetCells;

                            for (int i = 0; i < 9; ++i) {
                                if ((positionUnion >> i) & 1) { 
                                    int r = cellCoords[i].first;
                                    int c = cellCoords[i].second;
                                    subsetCells.push_back({r, c});

                                    for (int v = 1; v <= 9; ++v) {
                                        if (grid.cells[r][c].candidates[v] && !((digitMask >> v) & 1)) {
                                            // Ghi nhận cần xóa ứng viên 'v' (không thuộc bộ ẩn)
                                            elims.push_back({r, c, v}); 
                                        }
                                    }
                                }
                            }

                            if (!elims.empty()) {
                                std::vector<int> subsetVals;
                                for (int v = 1; v <= 9; ++v) {
                                    if ((digitMask >> v) & 1) subsetVals.push_back(v);
                                }

                                std::string msg = HintFormatter::HiddenSubset(strategyName, subsetVals, subsetCells, getRegionType(regionType), regionIdx);
                                return HintResult::CreateEliminateHint(strategyName, subsetCells, elims, msg);
                            }
                        }
                    }
                }
            }
        }
        return HintResult{};
    }
} // Kết thúc anonymous namespace

// ========================================================================
// ĐỊNH NGHĨA CÁC HÀM GỌI NAKED SUBSETS
// ========================================================================

// Naked Pairs (Cặp bài trùng)
HintResult FindNakedPairs(SudokuGrid& grid) {
    return FindNakedSubset(grid, 2, "Naked Pair");
}

// Naked Triples (Bộ 3 lộ diện)
HintResult FindNakedTriples(SudokuGrid& grid) {
    return FindNakedSubset(grid, 3, "Naked Triple");
}

// Naked Quads (Bộ 4 lộ diện)
HintResult FindNakedQuads(SudokuGrid& grid) {
    return FindNakedSubset(grid, 4, "Naked Quad");
}

// ========================================================================
// ĐỊNH NGHĨA CÁC HÀM GỌI HIDDEN SUBSETS
// ========================================================================

// Hidden Pairs (Cặp ẩn)
HintResult FindHiddenPairs(SudokuGrid& grid) { return FindHiddenSubset(grid, 2, "Hidden Pair"); }

// Hidden Triples (Bộ 3 ẩn)
HintResult FindHiddenTriples(SudokuGrid& grid) { return FindHiddenSubset(grid, 3, "Hidden Triple"); }

// Hidden Quads (Bộ 4 ẩn)
HintResult FindHiddenQuads(SudokuGrid& grid) { return FindHiddenSubset(grid, 4, "Hidden Quad"); }