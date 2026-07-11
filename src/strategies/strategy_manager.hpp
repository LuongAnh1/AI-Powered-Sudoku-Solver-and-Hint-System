#pragma once
#include "../types.hpp"

//==================================================================================== 
//========================== CÁC THUẬT TOÁN CƠ BẢN (NHÓM 1) ==========================
//====================================================================================

// Hidden Single / Naked Single (Điền ô duy nhất)

// Naked Single: Ô chỉ còn duy nhất 1 sự lựa chọn
HintResult FindNakedSingle(SudokuGrid& grid);
// Hidden Single: Số chỉ có thể đứng ở 1 ô trong hàng/cột/block
HintResult FindHiddenSingle(SudokuGrid& grid);

// Naked Pairs / Triples / Quads (Cặp 2, bộ 3, bộ 4 bài trùng - Lộ diện)

