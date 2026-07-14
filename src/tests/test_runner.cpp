#include <iostream>
#include <vector>
#include "../solver_engine.hpp"

int main() {
    std::cout << "=== KHOI DONG SUDOKU ENGINE TEST ===\n";

    // Một đề Sudoku mức độ Khó (Cần dùng đến Cấp 2 và Cấp 3 để giải)
    std::vector<std::vector<int>> hard_grid = {
        {0, 0, 0, 0, 0, 0, 0, 1, 2},
        {0, 0, 0, 0, 3, 5, 0, 0, 0},
        {0, 0, 0, 6, 0, 0, 0, 7, 0},
        {7, 0, 0, 0, 0, 0, 3, 0, 0},
        {0, 0, 0, 4, 0, 0, 8, 0, 0},
        {1, 0, 0, 0, 0, 0, 0, 0, 0},
        {0, 0, 0, 1, 2, 0, 0, 0, 0},
        {0, 8, 0, 0, 0, 0, 0, 4, 0},
        {0, 5, 0, 0, 0, 0, 6, 0, 0}
    };

    SolverEngine engine;
    
    std::cout << "1. Dang nap ma tran vao Engine...\n";
    engine.LoadGrid(hard_grid);
    
    std::cout << "2. Trang thai bang ban dau:\n";
    engine.PrintGrid();

    std::cout << "3. Bat dau giai tu dong (SolveFull)...\n";
    std::cout << "=====================================\n";
    engine.SolveFull();
    std::cout << "=====================================\n";

    std::cout << "HOAN TAT KIEM THU.\n";
    return 0;
}