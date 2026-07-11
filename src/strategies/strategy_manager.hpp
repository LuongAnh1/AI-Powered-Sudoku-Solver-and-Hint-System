#pragma once
#include "../types.hpp"

// ========================================================
// NHÓM 1: CÁC THUẬT TOÁN CƠ BẢN (Basic Strategies)
// ========================================================

//==== CÁC THUẬT TOÁN ĐIỀN Ô TRỐNG CƠ BẢN (Basic Strategies) ====

// Thuật toán Naked Single: Ô chỉ còn duy nhất 1 sự lựa chọn
HintResult FindNakedSingle(SudokuGrid& grid);
// Thuật toán Hidden Single: Số chỉ có thể đứng ở 1 ô trong hàng/cột/block
HintResult FindHiddenSingle(SudokuGrid& grid);

//==== CÁC THUẬT TOÁN LOẠI TRỪ ỨNG VIÊN - CẤP ĐỘ 1 ====

// Naked Pairs (Cặp bài trùng) - trong ô 3x3 hoặc hàng hoặc cột 
// chỉ có 2 ứng cử viên giống hệt nhau 
// => Tất cả ô trong cùng hàng/cột/block khác sẽ loại bỏ 2 ứng cử viên này
HintResult FindNakedPairs(SudokuGrid& grid);

// Naked Triples (Bộ 3 lộ diện) - 3 ô trong cùng hàng/cột/block
// tạo thành tổ hợp 3 ứng cử viên duy nhất
// => Tất cả ô trong cùng hàng/cột/block khác sẽ loại bỏ 3 ứng cử viên này
HintResult FindNakedTriples(SudokuGrid& grid);

// Naked Quads (Bộ 4 lộ diện) - 4 ô trong cùng hàng/cột/block
// tạo thành tổ hợp 4 ứng cử viên duy nhất
// => Tất cả ô trong cùng hàng/cột/block khác sẽ loại bỏ 4 ứng cử viên này
HintResult FindNakedQuads(SudokuGrid& grid);

