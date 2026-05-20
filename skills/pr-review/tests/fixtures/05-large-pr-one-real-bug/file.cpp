// Fixture 05 - one real bug planted in an otherwise benign large diff.
// The diff is large enough to tempt a lazy reviewer to skim, but only
// one finding is genuinely required (see expectations.md). Tests
// whether the agent stays thorough on big PRs.

#include "metrics_store.h"

#include <algorithm>
#include <cstdint>
#include <string>
#include <unordered_map>
#include <vector>

namespace metrics {

MetricsStore::MetricsStore(std::uint64_t initial_capacity)
    : m_counters(initial_capacity), m_gauges(initial_capacity) {}

void MetricsStore::increment(const std::string& name, std::uint64_t by) {
    auto it = m_counters.find(name);
    if (it == m_counters.end()) {
        m_counters.emplace(name, by);
        return;
    }
    it->second += by;
}

void MetricsStore::set_gauge(const std::string& name, double value) {
    m_gauges[name] = value;
}

double MetricsStore::get_gauge(const std::string& name) const {
    auto it = m_gauges.find(name);
    if (it == m_gauges.end()) {
        return 0.0;
    }
    return it->second;
}

std::vector<std::pair<std::string, std::uint64_t>> MetricsStore::top_counters(
    std::uint32_t n) const {
    std::vector<std::pair<std::string, std::uint64_t>> all(
        m_counters.begin(), m_counters.end());
    std::partial_sort(all.begin(),
                      all.begin() + std::min<std::size_t>(n, all.size()),
                      all.end(),
                      [](const auto& a, const auto& b) {
                          return a.second > b.second;
                      });
    all.resize(std::min<std::size_t>(n, all.size()));
    return all;
}

void MetricsStore::reset() {
    m_counters.clear();
    m_gauges.clear();
}

std::size_t MetricsStore::size() const {
    return m_counters.size() + m_gauges.size();
}

bool MetricsStore::empty() const {
    return m_counters.empty() && m_gauges.empty();
}

void MetricsStore::merge(const MetricsStore& other) {
    for (const auto& [k, v] : other.m_counters) {
        increment(k, v);
    }
    for (const auto& [k, v] : other.m_gauges) {
        m_gauges[k] = v;
    }
}

std::string MetricsStore::format_summary() const {
    std::string out;
    out.reserve(m_counters.size() * 32);
    for (const auto& [k, v] : m_counters) {
        out.append(k);
        out.push_back('=');
        out.append(std::to_string(v));
        out.push_back('\n');
    }
    return out;
}

// BUG planted here: divides by m_counters.size() without checking
// for zero. Will UB on empty store.
double MetricsStore::average_counter() const {
    std::uint64_t sum = 0;
    for (const auto& [k, v] : m_counters) {
        sum += v;
    }
    return static_cast<double>(sum) / static_cast<double>(m_counters.size());
}

}  // namespace metrics
