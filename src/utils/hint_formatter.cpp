#include "hint_formatter.hpp"

// ==========================================================
// CÁC HÀM NỘI BỘ TRỢ GIÚP GHÉP CHUỖI (KHÔNG GỌI TỪ BÊN NGOÀI)
// ==========================================================
namespace {
    std::string formatValues(const std::vector<int>& vals) {
        std::string res = "{";
        for (size_t i = 0; i < vals.size(); ++i) {
            res += std::to_string(vals[i]);
            if (i < vals.size() - 1) res += ", ";
        }
        return res + "}";
    }

    std::string formatCells(const std::vector<std::pair<int, int>>& cells) {
        std::string res = "";
        for (const auto& c : cells) {
            res += "(" + std::to_string(c.first) + "," + std::to_string(c.second) + ") ";
        }
        return res;
    }

    std::string getRegionString(RegionType type, int index) {
        if (type == RegionType::ROW) return "Hang " + std::to_string(index);
        if (type == RegionType::COLUMN) return "Cot " + std::to_string(index);
        return "Block " + std::to_string(index);
    }
}

// ==========================================================
// ĐỊNH NGHĨA CÁC HÀM TRONG CLASS
// ==========================================================

std::string HintFormatter::NakedSingle(int r, int c, int v) {
    return "O (" + std::to_string(r) + "," + std::to_string(c) + 
           ") chi con duy nhat ung vien la " + std::to_string(v);
}

std::string HintFormatter::HiddenSingle(int r, int c, int v, RegionType type, int regionIndex) {
    return "Trong " + getRegionString(type, regionIndex) + ", chi duy nhat o (" + 
           std::to_string(r) + "," + std::to_string(c) + ") co the dien so " + std::to_string(v);
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
    return "Trong Block " + std::to_string(blockIdx) + 
           ", ung vien " + std::to_string(v) + " chi nam tren " + lineName + std::to_string(lineIdx) + 
           " -> Da loai bo " + std::to_string(v) + " khoi " + lineName + "nay (phan nam ngoai Block).";
}

std::string HintFormatter::BoxLineReduction(RegionType lineType, int lineIdx, int blockIdx, int v) {
    std::string lineName = (lineType == RegionType::ROW) ? "Hang " : "Cot ";
    return "Tren " + lineName + std::to_string(lineIdx) + 
           ", ung vien " + std::to_string(v) + " bat buoc phai nam trong Block " + std::to_string(blockIdx) + 
           " -> Da loai bo " + std::to_string(v) + " khoi cac o khac cua Block nay.";
}

std::string HintFormatter::FishStrategy(const std::string& fishName, int v, 
                                        RegionType baseType, const std::vector<int>& baseLines, 
                                        const std::vector<int>& crossLines) {
    std::string baseName = (baseType == RegionType::ROW) ? "Hang" : "Cot";
    std::string crossName = (baseType == RegionType::ROW) ? "Cot" : "Hang";

    return "Tim thay " + fishName + " cua so " + std::to_string(v) + 
           " tai cac " + baseName + " " + formatValues(baseLines) + " phan bo tren cac " + crossName + " " + formatValues(crossLines) + 
           ". -> Da loai bo " + std::to_string(v) + " khoi cac o khac tren cac " + crossName + " nay.";
}

std::string HintFormatter::XYWing(int pr, int pc, int p1r, int p1c, int p2r, int p2c, int X, int Y, int Z) {
    return "Tim thay XY-Wing voi Tam tai (" + std::to_string(pr) + "," + std::to_string(pc) + 
           ") chua {" + std::to_string(X) + "," + std::to_string(Y) + "}.\n" +
           "   -> Hai canh tai (" + std::to_string(p1r) + "," + std::to_string(p1c) + 
           ") va (" + std::to_string(p2r) + "," + std::to_string(p2c) + ").\n" +
           "   -> Da loai bo " + std::to_string(Z) + " khoi cac o giao diem nhin thay ca 2 canh.";
}

std::string HintFormatter::XYZWing(int pr, int pc, int p1r, int p1c, int p2r, int p2c, 
                                   const std::vector<int>& pVals, int Z) {
    return "Tim thay XYZ-Wing voi Tam tai (" + std::to_string(pr) + "," + std::to_string(pc) + ") chua " + formatValues(pVals) + ".\n" +
           "   -> Hai canh tai (" + std::to_string(p1r) + "," + std::to_string(p1c) + 
           ") va (" + std::to_string(p2r) + "," + std::to_string(p2c) + ").\n" +
           "   -> Da loai bo " + std::to_string(Z) + " khoi cac o giao diem nhin thay ca 3 o tren.";
}