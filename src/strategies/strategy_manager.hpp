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

//==== CÁC THUẬT TOÁN LOẠI TRỪ ỨNG VIÊN KIỂU 1 - NAKED SUBSETS ====

// Naked Pairs (Cặp bài trùng) - trong ô 3x3 hoặc hàng hoặc cột 
// chỉ có 2 ứng cử viên giống hệt nhau 
// => Tất cả ô trong cùng hàng/cột/block khác sẽ loại bỏ 2 ứng cử viên này
HintResult FindNakedPairs(SudokuGrid& grid);

// Naked Triples (Bộ 3 lộ diện) - tương tự như Naked Pairs, nhưng với 3 ô và 3 ứng viên
HintResult FindNakedTriples(SudokuGrid& grid);

// Naked Quads (Bộ 4 lộ diện) - tương tự như Naked Triples, nhưng với 4 ô và 4 ứng viên
HintResult FindNakedQuads(SudokuGrid& grid);

//==== CÁC THUẬT TOÁN LOẠI TRỪ ỨNG VIÊN KIỂU 2 - HIDDEN SUBSETS ====

// Hidden Pairs (Cặp ẩn) - trong ô 3x3 hoặc hàng hoặc cột
// chỉ có 2 ứng cử viên xuất hiện trong 2 ô, có cả các ứng viên khác trong 2 ô này
// => Tất cả các ứng viên khác trong 2 ô này sẽ bị loại bỏ
HintResult FindHiddenPairs(SudokuGrid& grid);

// Hidden Triples (Bộ 3 ẩn) - tương tự như Hidden Pairs, nhưng với 3 ô và 3 ứng viên    
HintResult FindHiddenTriples(SudokuGrid& grid);

// Hidden Quads (Bộ 4 ẩn) - tương tự như Hidden Pairs, nhưng với 4 ô và 4 ứng viên
HintResult FindHiddenQuads(SudokuGrid& grid);

// ========================================================
// NHÓM 2: CÁC THUẬT TOÁN GIAO NHAU (Intersection Strategies)
// ========================================================

// Pointing Pairs/Triples (Chỉ điểm) - nếu trong 1 Block, các ứng viên của 1 số chỉ nằm trên cùng 1 Hàng hoặc Cột
// => Tất cả các ô khác trên Hàng hoặc Cột đó sẽ loại bỏ ứng viên này
HintResult FindPointing(SudokuGrid& grid);

// Box/Line Reduction (Thu gọn khối/đường) - nếu trong 1 Hàng hoặc Cột, các ứng viên của 1 số chỉ nằm trong cùng 1 Block
// => Tất cả các ô khác trong Block đó sẽ loại bỏ ứng viên này
HintResult FindBoxLineReduction(SudokuGrid& grid);