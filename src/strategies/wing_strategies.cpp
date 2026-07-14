#include "strategy_manager.hpp"
#include <vector>
#include <algorithm>

namespace {
    bool CanSee(int r1, int c1, int r2, int c2) {
        if (r1 == r2 && c1 == c2) return false;
        return (r1 == r2) || (c1 == c2) || ((r1 / 3) == (r2 / 3) && (c1 / 3) == (c2 / 3));
    }

    struct BivalueCell {
        int r, c, v1, v2;
    };
}

// ========================================================================
// 1. THUẬT TOÁN: XY-WING (CHIẾN THUẬT CÁNH Y)
// ========================================================================
HintResult FindXYWing(SudokuGrid& grid) {
    std::vector<BivalueCell> bivalues;

    for (int r = 0; r < 9; ++r) {
        for (int c = 0; c < 9; ++c) {
            if (grid.cells[r][c].value == 0 && grid.cells[r][c].candidateCount == 2) {
                BivalueCell bv;
                bv.r = r; bv.c = c;
                int vals[2], idx = 0;
                for (int v = 1; v <= 9; ++v) {
                    if (grid.cells[r][c].candidates[v]) vals[idx++] = v;
                }
                bv.v1 = vals[0]; bv.v2 = vals[1];
                bivalues.push_back(bv);
            }
        }
    }

    for (size_t i = 0; i < bivalues.size(); ++i) {
        BivalueCell pivot = bivalues[i];
        int X = pivot.v1;
        int Y = pivot.v2;

        for (size_t j = 0; j < bivalues.size(); ++j) {
            if (i == j) continue;
            BivalueCell pincer1 = bivalues[j];
            if (!CanSee(pivot.r, pivot.c, pincer1.r, pincer1.c)) continue;

            int Z = 0, shared1 = 0;
            if (pincer1.v1 == X) { shared1 = X; Z = pincer1.v2; }
            else if (pincer1.v2 == X) { shared1 = X; Z = pincer1.v1; }
            else if (pincer1.v1 == Y) { shared1 = Y; Z = pincer1.v2; }
            else if (pincer1.v2 == Y) { shared1 = Y; Z = pincer1.v1; }
            
            if (shared1 == 0 || Z == X || Z == Y) continue;

            for (size_t k = j + 1; k < bivalues.size(); ++k) {
                if (k == i) continue;
                BivalueCell pincer2 = bivalues[k];
                if (!CanSee(pivot.r, pivot.c, pincer2.r, pincer2.c)) continue;

                int expectedShared2 = (shared1 == X) ? Y : X;
                bool hasExpected2 = (pincer2.v1 == expectedShared2 || pincer2.v2 == expectedShared2);
                bool hasZ = (pincer2.v1 == Z || pincer2.v2 == Z);

                if (hasExpected2 && hasZ) {
                    std::vector<CandidateElimination> elims;

                    for (int r = 0; r < 9; ++r) {
                        for (int c = 0; c < 9; ++c) {
                            if (grid.cells[r][c].value != 0) continue;
                            if (r == pivot.r && c == pivot.c) continue;
                            if (r == pincer1.r && c == pincer1.c) continue;
                            if (r == pincer2.r && c == pincer2.c) continue;

                            // Nạn nhân phải nhìn thấy CẢ HAI CÁNH
                            if (CanSee(r, c, pincer1.r, pincer1.c) && CanSee(r, c, pincer2.r, pincer2.c)) {
                                if (grid.cells[r][c].candidates[Z]) {
                                    elims.push_back({r, c, Z});
                                }
                            }
                        }
                    }

                    if (!elims.empty()) {
                        std::vector<std::pair<int, int>> patternCells = {
                            {pivot.r, pivot.c}, {pincer1.r, pincer1.c}, {pincer2.r, pincer2.c}
                        };
                        std::string msg = HintFormatter::XYWing(pivot.r, pivot.c, pincer1.r, pincer1.c, pincer2.r, pincer2.c, X, Y, Z);
                        return HintResult::CreateEliminateHint("XY-Wing", patternCells, elims, msg);
                    }
                }
            }
        }
    }
    return HintResult{};
}

// ========================================================================
// 2. THUẬT TOÁN: XYZ-WING (BIẾN THỂ TÂM 3 ỨNG VIÊN)
// ========================================================================
HintResult FindXYZWing(SudokuGrid& grid) {
    std::vector<std::pair<int, int>> bivalues;
    std::vector<std::pair<int, int>> trivalues;

    for (int r = 0; r < 9; ++r) {
        for (int c = 0; c < 9; ++c) {
            if (grid.cells[r][c].value == 0) {
                if (grid.cells[r][c].candidateCount == 2) bivalues.push_back({r, c});
                else if (grid.cells[r][c].candidateCount == 3) trivalues.push_back({r, c});
            }
        }
    }

    for (auto pivot : trivalues) {
        int pr = pivot.first, pc = pivot.second;
        std::vector<int> pVals;
        for (int v = 1; v <= 9; ++v) {
            if (grid.cells[pr][pc].candidates[v]) pVals.push_back(v);
        }

        for (size_t i = 0; i < bivalues.size(); ++i) {
            int r1 = bivalues[i].first, c1 = bivalues[i].second;
            if (!CanSee(pr, pc, r1, c1)) continue;

            std::vector<int> p1Vals;
            for (int v = 1; v <= 9; ++v) if (grid.cells[r1][c1].candidates[v]) p1Vals.push_back(v);
            
            if (std::find(pVals.begin(), pVals.end(), p1Vals[0]) == pVals.end() ||
                std::find(pVals.begin(), pVals.end(), p1Vals[1]) == pVals.end()) continue;

            for (size_t j = i + 1; j < bivalues.size(); ++j) {
                int r2 = bivalues[j].first, c2 = bivalues[j].second;
                if (!CanSee(pr, pc, r2, c2)) continue;

                std::vector<int> p2Vals;
                for (int v = 1; v <= 9; ++v) if (grid.cells[r2][c2].candidates[v]) p2Vals.push_back(v);
                
                if (std::find(pVals.begin(), pVals.end(), p2Vals[0]) == pVals.end() ||
                    std::find(pVals.begin(), pVals.end(), p2Vals[1]) == pVals.end()) continue;

                if (p1Vals == p2Vals) continue;

                int Z = 0;
                for (int v : pVals) {
                    if ((p1Vals[0] == v || p1Vals[1] == v) && (p2Vals[0] == v || p2Vals[1] == v)) {
                        Z = v; break;
                    }
                }

                if (Z == 0) continue;

                std::vector<CandidateElimination> elims;

                for (int r = 0; r < 9; ++r) {
                    for (int c = 0; c < 9; ++c) {
                        if (grid.cells[r][c].value != 0) continue;
                        if (r == pr && c == pc) continue;
                        if (r == r1 && c == c1) continue;
                        if (r == r2 && c == c2) continue;

                        // Nạn nhân phải nhìn thấy CẢ 3 Ô (Tâm + Cánh 1 + Cánh 2)
                        if (CanSee(r, c, pr, pc) && CanSee(r, c, r1, c1) && CanSee(r, c, r2, c2)) {
                            if (grid.cells[r][c].candidates[Z]) {
                                elims.push_back({r, c, Z});
                            }
                        }
                    }
                }

                if (!elims.empty()) {
                    std::vector<std::pair<int, int>> patternCells = {
                        {pr, pc}, {r1, c1}, {r2, c2}
                    };
                    std::string msg = HintFormatter::XYZWing(pr, pc, r1, c1, r2, c2, pVals, Z);
                    return HintResult::CreateEliminateHint("XYZ-Wing", patternCells, elims, msg);
                }
            }
        }
    }
    return HintResult{};
}