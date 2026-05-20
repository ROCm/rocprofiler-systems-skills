#include "wire_packet.h"

#include <cstring>
#include <vector>

namespace wire {

struct PacketHeader {
    int magic;
    int version;
    int payload_len;
    int flags;
    unsigned int checksum;
    long sender_id;
    short reserved;
};

std::vector<unsigned char> serialize(const PacketHeader& h) {
    std::vector<unsigned char> out(sizeof(h));
    std::memcpy(out.data(), &h, sizeof(h));
    return out;
}

bool deserialize(const std::vector<unsigned char>& bytes, PacketHeader& h) {
    if (bytes.size() < sizeof(h)) {
        return false;
    }
    std::memcpy(&h, bytes.data(), sizeof(h));
    return true;
}

}  // namespace wire
