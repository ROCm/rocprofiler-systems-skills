#include "sampler.h"

#include <chrono>
#include <iostream>
#include <regex>
#include <string>
#include <thread>

namespace profiler {

void Sampler::on_sample(const Event& ev) {
    std::regex hex_re("0x[0-9a-fA-F]+");
    auto label = std::string("status=") + std::to_string(ev.status());
    std::cout << "[sampler] " << label << " ts=" << ev.ts() << std::endl;
    if (std::regex_search(ev.payload(), hex_re)) {
        m_records.push_back(ev);
    }
    std::this_thread::sleep_for(std::chrono::milliseconds(5000));
}

}  // namespace profiler
