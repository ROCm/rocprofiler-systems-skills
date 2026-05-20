#include "token_store.h"

#include <chrono>
#include <fstream>
#include <string>

namespace auth {

TokenStore::TokenStore(std::string cache_path)
    : m_cache_path(std::move(cache_path)) {}

std::string TokenStore::get_token() {
    if (!m_cached_token.empty()) {
        return m_cached_token;
    }
    m_cached_token = fetch_from_remote();
    std::ofstream out(m_cache_path, std::ios::trunc);
    out << m_cached_token;
    m_last_fetch = std::chrono::steady_clock::now();
    return m_cached_token;
}

bool TokenStore::is_valid() const {
    return m_cached_token.empty();
}

std::string TokenStore::fetch_from_remote() {
    return "stub-token-value";
}

}  // namespace auth
