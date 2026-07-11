#include "strategy_manager.hpp"
#include <sstream>
#include <iostream>

//==== CÁC THUẬT TOÁN ĐIỀN Ô TRỐNG CƠ BẢN (Basic Strategies) ====

// Thuật toán Naked Single: Ô chỉ còn duy nhất 1 sự lựa chọn
HintResult FindNakedSingle(SudokuGrid& grid) {
    HintResult result;
    for (int r = 0; r < 9; ++r) {
        for (int c = 0; c < 9; ++c) {
            if (grid.cells[r][c].value == 0 && grid.cells[r][c].candidateCount == 1) {
                // Tìm xem số đó là số mấy
                for (int v = 1; v <= 9; ++v) {
                    if (grid.cells[r][c].candidates[v]) {
                        result.found = true;
                        result.row = r;
                        result.col = c;
                        result.value = v;
                        result.strategyName = "Naked Single";
                        result.explanation = "O (" + std::to_string(r) + "," + std::to_string(c) + 
                                             ") chi con duy nhat de xuat " + std::to_string(v);
                        return result;
                    }
                }
            }
        }
    }
    return result;
}

// Thuật toán Hidden Single: Số chỉ có thể đứng ở 1 ô trong hàng/cột/block
HintResult FindHiddenSingle(SudokuGrid& grid) {
    HintResult result;
    
    for (int v = 1; v <= 9; ++v) {
        // Quét từng Block 3x3
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
                            targetR = r; targetC = c;
                        }
                    }
                }
                
                if (possibleCount == 1) {
                    result.found = true;
                    result.row = targetR;
                    result.col = targetC;
                    result.value = v;
                    result.strategyName = "Hidden Single (Block)";
                    result.explanation = "Trong Block nay, so " + std::to_string(v) + 
                                         " chi co the dien vao o (" + std::to_string(targetR) + "," + std::to_string(targetC) + ")";
                    return result;
                }
            }
        }
        // TODO: Viết thêm vòng lặp tương tự để quét theo Hàng và theo Cột ở đây
    }
    return result;
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

    // Hàm tổng quát tìm Naked Subset (N = 2, 3, hoặc 4)
    HintResult FindNakedSubset(SudokuGrid& grid, int N, const std::string& strategyName) {
        // regionType: 0 = Hàng, 1 = Cột, 2 = Block 3x3
        for (int regionType = 0; regionType < 3; ++regionType) {
            for (int regionIdx = 0; regionIdx < 9; ++regionIdx) {
                
                // 1. Thu thập tọa độ các ô trống trong khu vực đang xét
                std::vector<std::pair<int, int>> emptyCells;
                for (int i = 0; i < 9; ++i) {
                    int r, c;
                    if (regionType == 0) { r = regionIdx; c = i; }       // Duyệt hàng
                    else if (regionType == 1) { r = i; c = regionIdx; }  // Duyệt cột
                    else { r = (regionIdx / 3) * 3 + (i / 3); c = (regionIdx % 3) * 3 + (i % 3); } // Duyệt block

                    if (grid.cells[r][c].value == 0) {
                        emptyCells.push_back({r, c});
                    }
                }

                // Nếu số ô trống ít hơn kích thước nhóm (N), bỏ qua
                int numEmpty = emptyCells.size();
                if (numEmpty <= N) continue;

                // 2. Tìm tất cả các tổ hợp (combinations) chập N của các ô trống
                // Sử dụng vòng lặp từ 1 đến 2^numEmpty để duyệt mọi tổ hợp (Brute-force nhẹ)
                for (int mask = 1; mask < (1 << numEmpty); ++mask) {
                    if (countBits(mask) == N) { // Chỉ lấy tổ hợp có đúng N ô
                        
                        int candidateUnion = 0;
                        std::vector<std::pair<int, int>> subsetCells;

                        // Gộp đề xuất của N ô này lại bằng phép OR (|)
                        for (int i = 0; i < numEmpty; ++i) {
                            if ((mask >> i) & 1) {
                                subsetCells.push_back(emptyCells[i]);
                                candidateUnion |= getCandidateMask(grid.cells[emptyCells[i].first][emptyCells[i].second]);
                            }
                        }

                        // 3. NẾU TỔNG ĐỀ XUẤT CỦA N Ô ĐÚNG BẰNG N -> PHÁT HIỆN NAKED SUBSET!
                        if (countBits(candidateUnion) == N) {
                            
                            bool hasEliminated = false; // Cờ kiểm tra xem có thực sự xóa được đề xuất nào không

                            // 4. Quét các ô trống CÒN LẠI trong khu vực để xóa các số thuộc Subset
                            for (int i = 0; i < numEmpty; ++i) {
                                int r = emptyCells[i].first;
                                int c = emptyCells[i].second;
                                if (((mask >> i) & 1) == 0) { // Ô KHÔNG nằm trong Subset
                                    // int r = emptyCells[i].first;
                                    // int c = emptyCells[i].second;
                                    for (int val = 1; val <= 9; ++val) {
                                        // Nếu số val nằm trong Subset VÀ ô này đang có đề xuất val
                                        if (((candidateUnion >> val) & 1) && grid.cells[r][c].candidates[val]) {
                                            // ĐẶT ĐOẠN CODE DIAGNOSTIC VÀO ĐÂY (Phía dưới dòng IF kiểm tra):
                                            if (r == 0 && c == 1) {
                                                std::cout << "[DIAGNOSTIC] O (0,1) bi xoa de xuat " << val 
                                                        << " boi chien thuat: " << strategyName 
                                                        << ", RegionType: " << regionType 
                                                        << ", RegionIdx: " << regionIdx << "\n";
                                            }

                                            grid.cells[r][c].candidates[val] = false;
                                            grid.cells[r][c].candidateCount--;
                                            hasEliminated = true;
                                        }
                                    }
                                }
                            }

                            // Chỉ trả về kết quả nếu thuật toán THỰC SỰ ĐÃ XÓA được ít nhất 1 đề xuất
                            // (Tránh bị kẹt trong vòng lặp vô hạn nếu cứ tìm lại subset cũ)
                            if (hasEliminated) {
                                HintResult res;
                                res.found = true;
                                res.row = subsetCells[0].first;  // Trỏ tọa độ vào ô đầu tiên của bộ
                                res.col = subsetCells[0].second;
                                res.value = 0;                   // BẰNG 0 VÌ ĐÂY LÀ THUẬT TOÁN LOẠI TRỪ, KHÔNG PHẢI ĐIỀN SỐ
                                res.strategyName = strategyName;

                                // Xây dựng chuỗi giải thích cho con người
                                std::stringstream ss;
                                ss << "Tim thay " << strategyName << " gom {";
                                bool first = true;
                                for (int v = 1; v <= 9; ++v) {
                                    if ((candidateUnion >> v) & 1) {
                                        if (!first) ss << ", ";
                                        ss << v;
                                        first = false;
                                    }
                                }
                                ss << "} tai cac o ";
                                for (const auto& cell : subsetCells) {
                                    ss << "(" << cell.first << "," << cell.second << ") ";
                                }
                                ss << "-> Da loai tru chung khoi cac o khac trong ";
                                if (regionType == 0) ss << "Hang " << regionIdx;
                                else if (regionType == 1) ss << "Cot " << regionIdx;
                                else ss << "Block";
                                res.explanation = ss.str();

                                return res;
                            }
                        }
                    }
                }
            }
        }
        return HintResult{}; // Không tìm thấy
    }
} // Kết thúc anonymous namespace

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