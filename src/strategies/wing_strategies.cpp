#include "strategy_manager.hpp"
#include <vector>
#include <string>
#include <sstream>
#include <algorithm> 

// Thêm hàm nội bộ để kiểm tra xem 2 ô có "nhìn thấy" nhau không
namespace {
    bool CanSee(int r1, int c1, int r2, int c2) {
        // Bỏ qua nếu là cùng một ô
        if (r1 == r2 && c1 == c2) return false;
        // Cùng hàng, cùng cột, hoặc cùng khối 3x3
        return (r1 == r2) || (c1 == c2) || ((r1 / 3) == (r2 / 3) && (c1 / 3) == (c2 / 3));
    }

    // Cấu trúc tạm để lưu trữ các ô Song trị (2 ứng viên)
    struct BivalueCell {
        int r, c;
        int v1, v2;
    };
}

// ========================================================================
// 1. THUẬT TOÁN: XY-WING (CHIẾN THUẬT CÁNH NÂNG CAO)
// ========================================================================
HintResult FindXYWing(SudokuGrid& grid) {
    std::vector<BivalueCell> bivalues;

    // Bước 1: Thu thập tất cả các ô trên bảng chỉ có ĐÚNG 2 ỨNG VIÊN
    for (int r = 0; r < 9; ++r) {
        for (int c = 0; c < 9; ++c) {
            if (grid.cells[r][c].value == 0 && grid.cells[r][c].candidateCount == 2) {
                BivalueCell bv;
                bv.r = r; bv.c = c;
                int vals[2], idx = 0;
                for (int v = 1; v <= 9; ++v) {
                    if (grid.cells[r][c].candidates[v]) vals[idx++] = v;
                }
                bv.v1 = vals[0];
                bv.v2 = vals[1];
                bivalues.push_back(bv);
            }
        }
    }

    // Bước 2: Duyệt từng ô làm Ô TÂM (Pivot) {X, Y}
    for (size_t i = 0; i < bivalues.size(); ++i) {
        BivalueCell pivot = bivalues[i];
        int X = pivot.v1;
        int Y = pivot.v2;

        // Tìm Ô CÁNH 1 (Pincer 1)
        for (size_t j = 0; j < bivalues.size(); ++j) {
            if (i == j) continue;
            BivalueCell pincer1 = bivalues[j];
            
            // Cánh 1 phải nhìn thấy Tâm
            if (!CanSee(pivot.r, pivot.c, pincer1.r, pincer1.c)) continue;

            // Xác định ứng viên chung giữa Tâm và Cánh 1 (X hoặc Y), và ứng viên còn lại (Z)
            int Z = 0;
            int shared1 = 0;
            if (pincer1.v1 == X) { shared1 = X; Z = pincer1.v2; }
            else if (pincer1.v2 == X) { shared1 = X; Z = pincer1.v1; }
            else if (pincer1.v1 == Y) { shared1 = Y; Z = pincer1.v2; }
            else if (pincer1.v2 == Y) { shared1 = Y; Z = pincer1.v1; }
            
            // Nếu không có ứng viên chung, hoặc Z trùng với X, Y -> Loại
            if (shared1 == 0 || Z == X || Z == Y) continue;

            // Tìm Ô CÁNH 2 (Pincer 2)
            for (size_t k = j + 1; k < bivalues.size(); ++k) {
                if (k == i) continue;
                BivalueCell pincer2 = bivalues[k];
                
                // Cánh 2 phải nhìn thấy Tâm
                if (!CanSee(pivot.r, pivot.c, pincer2.r, pincer2.c)) continue;

                // Cánh 2 phải chia sẻ ứng viên CÒN LẠI của Tâm, VÀ có chứa ứng viên Z
                int expectedShared2 = (shared1 == X) ? Y : X;
                bool hasExpected2 = (pincer2.v1 == expectedShared2 || pincer2.v2 == expectedShared2);
                bool hasZ = (pincer2.v1 == Z || pincer2.v2 == Z);

                if (hasExpected2 && hasZ) {
                    // TÌM THẤY MÔ HÌNH XY-WING HOÀN CHỈNH!
                    // Bước 3: Tìm các ô nạn nhân nhìn thấy CẢ HAI CÁNH
                    bool hasEliminated = false;
                    std::vector<std::pair<int, int>> victims;

                    for (int r = 0; r < 9; ++r) {
                        for (int c = 0; c < 9; ++c) {
                            if (grid.cells[r][c].value != 0) continue;
                            if (r == pivot.r && c == pivot.c) continue;
                            if (r == pincer1.r && c == pincer1.c) continue;
                            if (r == pincer2.r && c == pincer2.c) continue;

                            // Nếu ô này nhìn thấy cả Cánh 1 và Cánh 2
                            if (CanSee(r, c, pincer1.r, pincer1.c) && CanSee(r, c, pincer2.r, pincer2.c)) {
                                if (grid.cells[r][c].candidates[Z]) {
                                    grid.cells[r][c].candidates[Z] = false;
                                    grid.cells[r][c].candidateCount--;
                                    hasEliminated = true;
                                    victims.push_back({r, c});
                                }
                            }
                        }
                    }

                    // Nếu có loại bỏ được ứng viên Z, trả về Gợi ý
                    if (hasEliminated) {
                        HintResult res;
                        res.found = true;
                        res.row = pivot.r;
                        res.col = pivot.c;
                        res.value = 0;
                        res.strategyName = "XY-Wing";
                        
                        std::stringstream ss;
                        ss << "Tim thay XY-Wing voi Tam tai (" << pivot.r << "," << pivot.c << ") chua {" << X << "," << Y << "}.\n";
                        ss << "   -> Hai canh tai (" << pincer1.r << "," << pincer1.c << ") va (" << pincer2.r << "," << pincer2.c << ").\n";
                        ss << "   -> Bat buoc phai co it nhat mot canh la so " << Z << ".\n";
                        ss << "   -> Da loai bo " << Z << " khoi cac o giao diem: ";
                        for (const auto& v : victims) {
                            ss << "(" << v.first << "," << v.second << ") ";
                        }
                        res.explanation = ss.str();
                        return res;
                    }
                }
            }
        }
    }
    return HintResult{};
}

// ========================================================================
// 2. THUẬT TOÁN: XYZ-WING (BIẾN THỂ NÂNG CAO CỦA XY-WING)
// ========================================================================
HintResult FindXYZWing(SudokuGrid& grid) {
    std::vector<std::pair<int, int>> bivalues;   // Ô có 2 ứng viên
    std::vector<std::pair<int, int>> trivalues;  // Ô có 3 ứng viên

    // Phân loại các ô
    for (int r = 0; r < 9; ++r) {
        for (int c = 0; c < 9; ++c) {
            if (grid.cells[r][c].value == 0) {
                if (grid.cells[r][c].candidateCount == 2) bivalues.push_back({r, c});
                else if (grid.cells[r][c].candidateCount == 3) trivalues.push_back({r, c});
            }
        }
    }

    // Duyệt qua từng ô có 3 ứng viên để làm TÂM {X, Y, Z}
    for (auto pivot : trivalues) {
        int pr = pivot.first, pc = pivot.second;
        std::vector<int> pVals;
        for (int v = 1; v <= 9; ++v) {
            if (grid.cells[pr][pc].candidates[v]) pVals.push_back(v);
        }

        // Duyệt tìm CÁNH 1 {X, Z} hoặc {Y, Z}
        for (size_t i = 0; i < bivalues.size(); ++i) {
            int r1 = bivalues[i].first, c1 = bivalues[i].second;
            if (!CanSee(pr, pc, r1, c1)) continue;

            std::vector<int> p1Vals;
            for (int v = 1; v <= 9; ++v) {
                if (grid.cells[r1][c1].candidates[v]) p1Vals.push_back(v);
            }
            // Cánh 1 phải là tập con của Tâm
            if (std::find(pVals.begin(), pVals.end(), p1Vals[0]) == pVals.end() ||
                std::find(pVals.begin(), pVals.end(), p1Vals[1]) == pVals.end()) continue;

            // Duyệt tìm CÁNH 2
            for (size_t j = i + 1; j < bivalues.size(); ++j) {
                int r2 = bivalues[j].first, c2 = bivalues[j].second;
                if (!CanSee(pr, pc, r2, c2)) continue;

                std::vector<int> p2Vals;
                for (int v = 1; v <= 9; ++v) {
                    if (grid.cells[r2][c2].candidates[v]) p2Vals.push_back(v);
                }
                // Cánh 2 phải là tập con của Tâm
                if (std::find(pVals.begin(), pVals.end(), p2Vals[0]) == pVals.end() ||
                    std::find(pVals.begin(), pVals.end(), p2Vals[1]) == pVals.end()) continue;

                // Hai Cánh không được giống hệt nhau
                if (p1Vals == p2Vals) continue;

                // Tìm ỨNG VIÊN Z (Số chung xuất hiện ở cả Tâm, Cánh 1, và Cánh 2)
                int Z = 0;
                for (int v : pVals) {
                    if ((p1Vals[0] == v || p1Vals[1] == v) && (p2Vals[0] == v || p2Vals[1] == v)) {
                        Z = v; break;
                    }
                }

                if (Z == 0) continue;

                // TÌM NẠN NHÂN: Phải nhìn thấy cả TÂM, CÁNH 1, VÀ CÁNH 2
                bool hasEliminated = false;
                std::vector<std::pair<int, int>> victims;

                for (int r = 0; r < 9; ++r) {
                    for (int c = 0; c < 9; ++c) {
                        if (grid.cells[r][c].value != 0) continue;
                        if (r == pr && c == pc) continue;
                        if (r == r1 && c == c1) continue;
                        if (r == r2 && c == c2) continue;

                        if (CanSee(r, c, pr, pc) && CanSee(r, c, r1, c1) && CanSee(r, c, r2, c2)) {
                            if (grid.cells[r][c].candidates[Z]) {
                                grid.cells[r][c].candidates[Z] = false;
                                grid.cells[r][c].candidateCount--;
                                hasEliminated = true;
                                victims.push_back({r, c});
                            }
                        }
                    }
                }

                if (hasEliminated) {
                    HintResult res;
                    res.found = true;
                    res.row = pr;
                    res.col = pc;
                    res.value = 0;
                    res.strategyName = "XYZ-Wing";
                    
                    std::stringstream ss;
                    ss << "Tim thay XYZ-Wing voi Tam tai (" << pr << "," << pc << ") chua {" << pVals[0] << "," << pVals[1] << "," << pVals[2] << "}.\n";
                    ss << "   -> Hai canh tai (" << r1 << "," << c1 << ") va (" << r2 << "," << c2 << ").\n";
                    ss << "   -> Da loai bo " << Z << " khoi cac o giao diem nhin thay ca 3 o nay: ";
                    for (const auto& v : victims) {
                        ss << "(" << v.first << "," << v.second << ") ";
                    }
                    res.explanation = ss.str();
                    return res;
                }
            }
        }
    }
    return HintResult{};
}