#include "solver_engine.hpp"
#include <iostream>
#include <vector>

int main() {
    // Đề bài mẫu (Số 0 là ô trống)
    std::vector<std::vector<int>> input = {
        {5, 3, 0, 0, 7, 0, 0, 0, 0},
        {6, 0, 0, 1, 9, 5, 0, 0, 0},
        {0, 9, 8, 0, 0, 0, 0, 6, 0},
        {8, 0, 0, 0, 6, 0, 0, 0, 3},
        {4, 0, 0, 8, 0, 3, 0, 0, 1},
        {7, 0, 0, 0, 2, 0, 0, 0, 6},
        {0, 6, 0, 0, 0, 0, 2, 8, 0},
        {0, 0, 0, 4, 1, 9, 0, 0, 5},
        {0, 0, 0, 0, 8, 0, 0, 7, 9}
    };

    SolverEngine engine;
    std::cout << "BANG SUDOKU BAN DAU:\n";
    engine.LoadGrid(input);
    engine.PrintGrid();

    std::cout << "\nBAT DAU GIAI:\n";
    engine.SolveFull();

    return 0;
}