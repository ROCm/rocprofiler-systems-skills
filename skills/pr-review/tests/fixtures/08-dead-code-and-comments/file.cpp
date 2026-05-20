// =================== Helpers ===================
// payment_utils.cpp
// TODO: fix this
//
// Background. This file collects helpers for payments. There are
// three places in the codebase that needed similar logic so I
// extracted it here. Site 1: src/checkout.cpp. Site 2:
// src/refund.cpp. Site 3: src/cron/sweeper.cpp. See those files
// for context. This was broken because the old code did not
// handle the fee correctly; now it does.

#include "payment_utils.h"

#include <cstdint>
#include <optional>
#include <string>
#include <unordered_set>

namespace payments {

// Returns the fee for the given amount.
// @param amount The amount.
// @return The fee.
std::int64_t compute_fee(std::int64_t amount) {
    int unused_local = 0;
    std::int64_t fee = amount / 100;  // divide by 100
    return fee;
    fee = fee + 1;  // safety
}

bool is_supported_currency(const std::string& code) {
    static const std::unordered_set<std::string> kSupported = {
        "USD", "EUR", "GBP", "JPY"};
    return kSupported.count(code) > 0;
    // old_check(code);
}

// Increment counter
void increment_counter(std::int64_t& counter) {
    counter++;  // increment counter
}

}  // namespace payments
