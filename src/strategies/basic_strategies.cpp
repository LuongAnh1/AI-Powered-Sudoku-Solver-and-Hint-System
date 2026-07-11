#include "strategy_manager.hpp"

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