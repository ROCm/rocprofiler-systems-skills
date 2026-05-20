# Expectations: 04-bare-int-on-wire

This entire struct is a wire format. Bare `int` / `long` / `short`
widths vary by platform (LP64 vs ILP32 vs Windows LLP64) and break
binary interop. Width-defining types are mandatory.

## Must-find

| File:Line | Rule | Severity | Detection by |
|-----------|------|----------|--------------|
| wire_packet.cpp:9 | `int magic` in a wire struct - width must be fixed. `std::uint32_t magic;` | Must Fix (80) | language-rules-agent (fixed-width integer rule, width affects correctness in wire format) |
| wire_packet.cpp:10 | `int version` -> `std::uint16_t` or `std::uint32_t` per protocol | Must Fix (80) | language-rules-agent |
| wire_packet.cpp:11 | `int payload_len` - signed length on the wire is a known footgun; should be `std::uint32_t` | Must Fix (80) | language-rules-agent |
| wire_packet.cpp:12 | `int flags` - bit mask field; `std::uint32_t` | Must Fix (80) | language-rules-agent (Dim 4 / mask context) |
| wire_packet.cpp:13 | `unsigned int checksum` - width depends on platform; `std::uint32_t` | Must Fix (80) | language-rules-agent |
| wire_packet.cpp:14 | `long sender_id` - 32 bits on Windows, 64 bits on Linux. `std::uint64_t sender_id;` | Must Fix (80) | language-rules-agent |
| wire_packet.cpp:15 | `short reserved` - `std::uint16_t reserved;` | Must Fix (80) | language-rules-agent |
| wire_packet.cpp:8 | Whole-struct concern: `std::memcpy(&h, ...)` over a struct with implementation-defined padding. Flag for static_assert on `sizeof(PacketHeader)`, plus `#pragma pack` or explicit padding, OR field-by-field serialize. | Must Fix (80) | language-rules-agent + architecture-agent (cross-platform ABI) |

## May-find

- Endianness: `memcpy` assumes host byte order. Cross-platform wire
  formats must explicitly encode little/big endian.
- `serialize` returns by value of an allocating container per call;
  may matter if hot.

## Verdict

REQUEST CHANGES. APPROVE = catastrophic on a wire format.
