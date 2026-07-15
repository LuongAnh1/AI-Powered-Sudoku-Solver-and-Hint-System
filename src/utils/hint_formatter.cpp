#include "hint_formatter.hpp"

// ==========================================================
// CÁC HÀM NỘI BỘ TRỢ GIÚP GHÉP CHUỖI (KHÔNG GỌI TỪ BÊN NGOÀI)
// ==========================================================
namespace {
    // Định dạng các giá trị số Sudoku thực tế (1-9) - Giữ nguyên không cộng thêm 1
    std::string formatValues(const std::vector<int>& vals) {
        std::string res = "{";
        for (size_t i = 0; i < vals.size(); ++i) {
            res += std::to_string(vals[i]);
            if (i < vals.size() - 1) res += ", ";
        }
        return res + "}";
    }

    // Định dạng các chỉ mục Hàng hoặc Cột (0-8) - Cộng thêm 1 để chuyển sang hệ (1-9)
    std::string formatIndices(const std::vector<int>& indices) {
        std::string res = "{";
        for (size_t i = 0; i < indices.size(); ++i) {
            res += std::to_string(indices[i] + 1);
            if (i < indices.size() - 1) res += ", ";
        }
        return res + "}";
    }

    // Định dạng tọa độ ô (Row, Col) - Cộng thêm 1 để chuyển sang hệ (1-9)
    std::string formatCells(const std::vector<std::pair<int, int>>& cells) {
        std::string res = "";
        for (const auto& c : cells) {
            res += "(" + std::to_string(c.first + 1) + "," + std::to_string(c.second + 1) + ") ";
        }
        return res;
    }

    // Định dạng tên vùng (Row, Col, Block) - Cộng thêm 1 để chuyển sang hệ (1-9)
    std::string getRegionString(RegionType type, int index) {
        if (type == RegionType::ROW) return "Hang " + std::to_string(index + 1);
        if (type == RegionType::COLUMN) return "Cot " + std::to_string(index + 1);
        return "Block " + std::to_string(index + 1);
    }
}

// ==========================================================
// ĐỊNH NGHĨA CÁC HÀM TRONG CLASS
// ==========================================================

std::string HintFormatter::NakedSingle(int r, int c, int v) {
    return "O (" + std::to_string(r + 1) + "," + std::to_string(c + 1) + 
           ") chi con duy nhat ung vien la " + std::to_string(v);
}

std::string HintFormatter::HiddenSingle(int r, int c, int v, RegionType type, int regionIndex) {
    return "Trong " + getRegionString(type, regionIndex) + ", chi duy nhat o (" + 
           std::to_string(r + 1) + "," + std::to_string(c + 1) + ") co the dien so " + std::to_string(v);
}

std::string HintFormatter::NakedSubset(const std::string& strategy, const std::vector<int>& values, 
                                       const std::vector<std::pair<int, int>>& cells, RegionType type, int regionIndex) {
    return "Tim thay " + strategy + " gom " + formatValues(values) + 
           " tai cac o " + formatCells(cells) + "-> Da loai tru chung khoi cac o khac trong " + getRegionString(type, regionIndex);
}

std::string HintFormatter::HiddenSubset(const std::string& strategy, const std::vector<int>& values, 
                                        const std::vector<std::pair<int, int>>& cells, RegionType type, int regionIndex) {
    return "Tim thay " + strategy + " gom cac so " + formatValues(values) + 
           " an minh tai cac o " + formatCells(cells) + "trong " + getRegionString(type, regionIndex) + 
           " -> Da loai bo cac ung vien khac khoi cac o nay.";
}

std::string HintFormatter::Pointing(int blockIdx, RegionType lineType, int lineIdx, int v) {
    std::string lineName = (lineType == RegionType::ROW) ? "Hang " : "Cot ";
    return "Trong Block " + std::to_string(blockIdx + 1) + 
           ", ung vien " + std::to_string(v) + " chi nam tren " + lineName + std::to_string(lineIdx + 1) + 
           " -> Da loai bo " + std::to_string(v) + " khoi " + lineName + "nay (phan nam ngoai Block).";
}

std::string HintFormatter::BoxLineReduction(RegionType lineType, int lineIdx, int blockIdx, int v) {
    std::string lineName = (lineType == RegionType::ROW) ? "Hang " : "Cot ";
    return "Tren " + lineName + std::to_string(lineIdx + 1) + 
           ", ung vien " + std::to_string(v) + " bat buoc phai nam trong Block " + std::to_string(blockIdx + 1) + 
           " -> Da loai bo " + std::to_string(v) + " khoi cac o khac cua Block nay.";
}

std::string HintFormatter::FishStrategy(const std::string& fishName, int v, 
                                        RegionType baseType, const std::vector<int>& baseLines, 
                                        const std::vector<int>& crossLines) {
    std::string baseName = (baseType == RegionType::ROW) ? "Hang" : "Cot";
    std::string crossName = (baseType == RegionType::ROW) ? "Cot" : "Hang";

    return "Tim thay " + fishName + " cua so " + std::to_string(v) + 
           " tai cac " + baseName + " " + formatIndices(baseLines) + " phan bo tren cac " + crossName + " " + formatIndices(crossLines) + 
           ". -> Da loai bo " + std::to_string(v) + " khoi cac o khac tren cac " + crossName + " nay.";
}

std::string HintFormatter::XYWing(int pr, int pc, int p1r, int p1c, int p2r, int p2c, int X, int Y, int Z) {
    return "Tim thay XY-Wing voi Tam tai (" + std::to_string(pr + 1) + "," + std::to_string(pc + 1) + 
           ") chua {" + std::to_string(X) + "," + std::to_string(Y) + "}.\n" +
           "   -> Hai canh tai (" + std::to_string(p1r + 1) + "," + std::to_string(p1c + 1) + 
           ") va (" + std::to_string(p2r + 1) + "," + std::to_string(p2c + 1) + ").\n" +
           "   -> Da loai bo " + std::to_string(Z) + " khoi cac o giao diem nhin thay ca 2 canh.";
}

std::string HintFormatter::XYZWing(int pr, int pc, int p1r, int p1c, int p2r, int p2c, 
                                   const std::vector<int>& pVals, int Z) {
    return "Tim thay XYZ-Wing voi Tam tai (" + std::to_string(pr + 1) + "," + std::to_string(pc + 1) + ") chua " + formatValues(pVals) + ".\n" +
           "   -> Hai canh tai (" + std::to_string(p1r + 1) + "," + std::to_string(p1c + 1) + 
           ") va (" + std::to_string(p2r + 1) + "," + std::to_string(p2c + 1) + ").\n" +
           "   -> Da loai bo " + std::to_string(Z) + " khoi cac o giao diem nhin thay ca 3 o tren.";
}