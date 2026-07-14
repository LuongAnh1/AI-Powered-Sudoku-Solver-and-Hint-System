#pragma once
#include <string>
#include <vector>
#include <utility>
#include "../types.hpp" // Rất quan trọng để C++ biết RegionType là gì

class HintFormatter {
public:
    // Cấp 1
    static std::string NakedSingle(int r, int c, int v);
    static std::string HiddenSingle(int r, int c, int v, RegionType type, int regionIndex);

    // Cấp 2: Naked/Hidden Subsets (Dùng chung cho Pairs, Triples, Quads)
    static std::string NakedSubset(const std::string& strategy, const std::vector<int>& values, 
                                   const std::vector<std::pair<int, int>>& cells, RegionType type, int regionIndex);
    static std::string HiddenSubset(const std::string& strategy, const std::vector<int>& values, 
                                    const std::vector<std::pair<int, int>>& cells, RegionType type, int regionIndex);

    // Cấp 2.5 & 3.5: Intersection (Giao lộ)
    static std::string Pointing(int blockIdx, RegionType lineType, int lineIdx, int v);
    static std::string BoxLineReduction(RegionType lineType, int lineIdx, int blockIdx, int v);

    // Cấp 3: Fish Strategies (X-Wing, Swordfish, Jellyfish)
    static std::string FishStrategy(const std::string& fishName, int v, 
                                    RegionType baseType, const std::vector<int>& baseLines, 
                                    const std::vector<int>& crossLines);

    // Cấp 4: Wing Strategies
    static std::string XYWing(int pr, int pc, int p1r, int p1c, int p2r, int p2c, int X, int Y, int Z);
    static std::string XYZWing(int pr, int pc, int p1r, int p1c, int p2r, int p2c, 
                               const std::vector<int>& pVals, int Z);
};