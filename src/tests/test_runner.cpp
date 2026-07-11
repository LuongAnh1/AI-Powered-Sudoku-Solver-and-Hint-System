#include "../solver_engine.hpp"
#include <iostream>
#include <vector>
#include <string>

// Hàm tiện ích để chạy một ca kiểm thử cụ thể
void RunTestCase(const std::string& testName, const std::vector<std::vector<int>>& inputGrid) {
    std::cout << "\n==================================================\n";
    std::cout << " CHAY KIEM THU: " << testName << "\n";
    std::cout << "==================================================\n";
    
    SolverEngine engine;
    engine.LoadGrid(inputGrid);
    
    std::cout << "Bang Sudoku ban dau:\n";
    engine.PrintGrid();
    
    std::cout << "Qua trinh giai:\n";
    engine.SolveFull();
}

int main() {

    // ----------------------------------------------------------------
    // CA KIỂM THỬ 4: Đề bài yêu cầu Naked Quad (Bộ 4 lộ diện)
    // ----------------------------------------------------------------
    std::vector<std::vector<int>> imageTestGrid = {
        {0, 0, 0,  0, 0, 4,  8, 1, 7},
        {6, 0, 0,  0, 0, 8,  0, 2, 4},
        {4, 2, 8,  7, 0, 0,  0, 9, 6},
        
        {8, 0, 0,  1, 0, 3,  2, 4, 9},
        {0, 9, 0,  8, 0, 0,  7, 6, 3},
        {0, 0, 0,  0, 7, 0,  1, 5, 8},
        
        {0, 0, 2,  0, 0, 0,  0, 7, 5},
        {0, 0, 0,  0, 0, 7,  0, 3, 2},
        {7, 0, 5,  3, 0, 0,  9, 8, 1}
    };

    // Thực thi các ca kiểm thử
    RunTestCase("TEST 4 - NAKED QUAD REQUIRED", imageTestGrid);

    return 0;
}