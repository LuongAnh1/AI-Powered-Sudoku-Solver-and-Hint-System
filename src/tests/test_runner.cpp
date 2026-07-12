#include "../solver_engine.hpp"
#include <iostream>
#include <vector>
#include <string>

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
    // Đề bài thực tế trích xuất từ hình ảnh của bạn
    // std::vector<std::vector<int>> realWorldGrid = {
    //     {1, 7, 9,  4, 0, 0,  0, 3, 0},
    //     {6, 5, 0,  0, 1, 0,  7, 0, 0}, // <--- Đã sửa số 7 về đúng cột 6 [1][6]
    //     {8, 2, 0,  0, 0, 7,  6, 0, 0},
        
    //     {5, 6, 0,  0, 0, 0,  8, 7, 0},
    //     {4, 3, 8,  6, 7, 2,  0, 0, 0},
    //     {7, 9, 0,  0, 0, 0,  0, 0, 0},
        
    //     {0, 8, 7,  0, 0, 9,  0, 5, 0},
    //     {9, 0, 5,  0, 8, 0,  3, 0, 7},
    //     {0, 0, 6,  7, 5, 0,  9, 0, 0}
    // };
    std::vector<std::vector<int>> realWorldGrid = {
        {9, 0, 0,  0, 0, 0,  5, 6, 1},
        {0, 0, 6,  0, 1, 0,  7, 9, 3}, 
        {7, 1, 0,  0, 9, 6,  2, 4, 8},
        
        {6, 0, 0,  0, 2, 1,  4, 7, 9},
        {0, 0, 0,  0, 0, 0,  0, 0, 5},
        {0, 0, 0,  0, 4, 0,  0, 0, 6},
        
        {4, 2, 0,  0, 5, 8,  6, 1, 7},
        {5, 0, 7,  1, 0, 2,  0, 0, 4},
        {0, 0, 1,  0, 0, 0,  0, 5, 2}
    };


    RunTestCase("DE BAI THUC TE TU ANH CHUP", realWorldGrid);

    return 0;
}