#pragma once
#include "types.hpp"
#include <vector>

class SolverEngine {
private:
    SudokuGrid grid;

    // Hàm nội bộ: Xóa 1 đề xuất và giảm biến đếm (Tương đương điều kiện phủ)
    void RemoveCandidate(int row, int col, int value);
    
    // Hàm nội bộ: Xóa số vừa điền khỏi gợi ý trong Hàng, Cột và Block (Lan truyền ràng buộc)
    void PropagateConstraints(int row, int col, int value);

public:
    SolverEngine();
    
    // Nhận dữ liệu đầu vào 
    void LoadGrid(const std::vector<std::vector<int>>& input);

    // Xuất ma trận kết quả ra ngoài
    std::vector<std::vector<int>> GetGrid() const;
    
    // In kết quả ra màn hình 
    void PrintGrid() const;
    
    // Điền một số vào bảng 
    bool PlaceValue(int row, int col, int value);

    // Chạy các thuật toán để lấy 1 bước gợi ý
    HintResult GetNextHint();
    
    // In ra các đề xuất của một ô cụ thể (dùng để debug)
    // void PrintCellCandidates(int r, int c) const; 

    // Giải toàn bộ 
    void SolveFull();
};