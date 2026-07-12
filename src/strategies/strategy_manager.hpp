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

// ===========================================================
// NHÓM 3: KỸ THUẬT CÁ (Fish Techniques)
// ===========================================================

// X-Wing (Cá X) - Tìm 2 Hàng hoặc 2 Cột mà ứng viên của 1 số chỉ xuất hiện ở đúng 2 Cột hoặc 2 Hàng giống nhau
// tức là tạo thành 1 hình chữ nhật, các ô khác trên 2 Cột hoặc 2 Hàng này sẽ loại bỏ ứng viên này
// => Tất cả các ô khác trên 2 Cột hoặc 2 Hàng này sẽ loại bỏ ứng viên này
HintResult FindXWing(SudokuGrid& grid);

// SWORDFISH (Cá Kiếm) - Nâng cấp của X-WING thành 3 hàng hoặc 3 cột, CẤP ĐỘ 2
HintResult FindSwordfish(SudokuGrid& grid);

// JELLYFISH (Cá Sứa) - Nâng cấp của SWORDFISH thành 4 hàng hoặc 4 cột, CẤP ĐỘ 3
HintResult FindJellyfish(SudokuGrid& grid);

// ===========================================================
// NHÓM 3: KỸ THUẬT CÁNH (Wing Techniques) - XY-Wing, XYZ-Wing
// ===========================================================

// XY-Wing (Cá XY) - Tìm 3 ô chỉ có 2 ứng viên
// Giả sử có 3 ô A, B, C với các ứng viên {X,Y}, {X,Z}, {Y,Z} (X,Y,Z là 3 số khác nhau)
// Với điều kiện A nhìn thấy B, A nhìn thấy C, B và C không nhìn thấy nhau
// => Tất cả các ô nhìn thấy cả B và C sẽ loại bỏ ứng viên Z
// Nhìn thấy nghĩa là 2 ô nằm trên cùng 1 Hàng, Cột hoặc Block 3x3 
HintResult FindXYWing(SudokuGrid& grid);

// XYZ-Wing (Cá XYZ) - Tìm 3 ô, trong đó 1 ô có 3 ứng viên {X,Y,Z} và 2 ô còn lại có 2 ứng viên {X,Z} và {Y,Z}
// Với điều kiện ô có 3 ứng viên nhìn thấy cả 2 ô còn lại, 2 ô còn lại không nhìn thấy nhau
// => Tất cả các ô nhìn thấy cả 2 ô còn lại sẽ loại bỏ ứng viên Z
HintResult FindXYZWing(SudokuGrid& grid);

