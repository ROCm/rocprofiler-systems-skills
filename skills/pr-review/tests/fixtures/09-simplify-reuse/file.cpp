#include "csv_loader.h"

#include <algorithm>
#include <cstdint>
#include <fstream>
#include <string>
#include <vector>

namespace csv {

std::vector<std::string> split_line(const std::string& line) {
    std::vector<std::string> out;
    std::string current;
    for (std::size_t i = 0; i < line.size(); i++) {
        if (line[i] == ',') {
            out.push_back(current);
            current = "";
        } else {
            current += line[i];
        }
    }
    out.push_back(current);
    return out;
}

std::int32_t count_non_empty(const std::vector<std::string>& rows) {
    std::int32_t count = 0;
    for (std::size_t i = 0; i < rows.size(); i++) {
        if (rows[i].size() > 0) {
            count = count + 1;
        }
    }
    return count;
}

std::vector<std::string> uppercase_all(const std::vector<std::string>& rows) {
    std::vector<std::string> out;
    for (std::size_t i = 0; i < rows.size(); i++) {
        std::string r = rows[i];
        for (std::size_t j = 0; j < r.size(); j++) {
            if (r[j] >= 'a' && r[j] <= 'z') {
                r[j] = r[j] - 'a' + 'A';
            }
        }
        out.push_back(r);
    }
    return out;
}

bool contains(const std::vector<std::string>& rows, const std::string& needle) {
    for (std::size_t i = 0; i < rows.size(); i++) {
        if (rows[i] == needle) {
            return true;
        }
    }
    return false;
}

}  // namespace csv
