---
name: library-amd-smi
description: AMD SMI C++ library for GPU/CPU/NIC monitoring and management. Use when working with AMD hardware monitoring, GPU temperature, power, memory, clocks, PCIe, XGMI, AINIC (AI NIC) network interfaces, or any amdsmi.h functions.
---

# AMD SMI C++ Library

AMD System Management Interface library for monitoring and managing AMD GPUs, CPUs, and AI NICs.

## Header and Linking

```cpp
#include "amd_smi/amdsmi.h"
```

```bash
# Build
g++ -I/opt/rocm/include source.cc -L/opt/rocm/lib -lamd_smi -o output

# Or set LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/opt/rocm/lib:$LD_LIBRARY_PATH
```

## Initialization Pattern

Every AMD SMI application must initialize and shut down properly:

```cpp
amdsmi_status_t ret;

// Initialize for GPUs only
ret = amdsmi_init(AMDSMI_INIT_AMD_GPUS);

// Or for CPUs only
ret = amdsmi_init(AMDSMI_INIT_AMD_CPUS);

// Or for AI NICs only
ret = amdsmi_init(AMDSMI_INIT_AMD_NICS);

// Or for all processors
ret = amdsmi_init(AMDSMI_INIT_ALL_PROCESSORS);

// ... use the library ...

// Clean up - MUST be called
ret = amdsmi_shut_down();
```

## Core Concepts

### Handles Hierarchy

```
Socket → Processor (GPU/CPU/NIC) → Core (for CPUs)
```

- **Socket handle**: Physical hardware socket
- **Processor handle**: GPU, CPU, or NIC within a socket (may change between app restarts)
- **Device handles are NOT persistent** across processes

### Getting Handles

```cpp
// Get socket count and handles
uint32_t socket_count = 0;
amdsmi_get_socket_handles(&socket_count, nullptr);  // Get count
std::vector<amdsmi_socket_handle> sockets(socket_count);
amdsmi_get_socket_handles(&socket_count, sockets.data());

// Get processor handles for a socket
uint32_t device_count = 0;
amdsmi_get_processor_handles(sockets[0], &device_count, nullptr);
std::vector<amdsmi_processor_handle> processors(device_count);
amdsmi_get_processor_handles(sockets[0], &device_count, processors.data());

// Get processors by type
processor_type_t type = AMDSMI_PROCESSOR_TYPE_AMD_GPU;
amdsmi_get_processor_handles_by_type(socket, type, nullptr, &count);
```

### Processor Types

- `AMDSMI_PROCESSOR_TYPE_AMD_GPU` - AMD GPU
- `AMDSMI_PROCESSOR_TYPE_AMD_CPU` - AMD CPU
- `AMDSMI_PROCESSOR_TYPE_AMD_CPU_CORE` - CPU core
- `AMDSMI_PROCESSOR_TYPE_AMD_APU` - AMD APU
- `AMDSMI_PROCESSOR_TYPE_AMD_NIC` - AI Network Interface Card

## Common GPU Queries

### Temperature

```cpp
int64_t temp;
amdsmi_get_temp_metric(processor, AMDSMI_TEMPERATURE_TYPE_EDGE,
                       AMDSMI_TEMP_CURRENT, &temp);

// Temperature types: EDGE, JUNCTION, HOTSPOT, VRAM, HBM_0-3, PLX
// Metrics: CURRENT, MAX, MIN, CRITICAL, EMERGENCY, SHUTDOWN
```

### Power

```cpp
amdsmi_power_info_t power_info;
amdsmi_get_power_info(processor, &power_info);
// power_info.current_socket_power, average_socket_power, etc.

// Power cap
amdsmi_power_cap_info_t cap_info;
amdsmi_get_power_cap_info(processor, 0, &cap_info);
```

### Memory

```cpp
// Total memory
uint64_t total;
amdsmi_get_gpu_memory_total(processor, AMDSMI_MEM_TYPE_VRAM, &total);

// Memory usage
uint64_t used;
amdsmi_get_gpu_memory_usage(processor, AMDSMI_MEM_TYPE_VRAM, &used);

// Memory types: VRAM, VIS_VRAM, GTT
```

### Clocks

```cpp
amdsmi_clk_info_t clk_info;
amdsmi_get_clock_info(processor, AMDSMI_CLK_TYPE_GFX, &clk_info);
// clk_info.clk (current), max_clk, min_clk

// Clock types: GFX, MEM, SOC, SYS, DF, DCEF, VCLK0/1, DCLK0/1, PCIE
```

### GPU Activity/Utilization

```cpp
amdsmi_engine_usage_t usage;
amdsmi_get_gpu_activity(processor, &usage);
// usage.gfx_activity, umc_activity, mm_activity (percentages)

uint32_t busy_percent;
amdsmi_get_gpu_busy_percent(processor, &busy_percent);
```

### Device Info

```cpp
// Board info (product name, serial, etc.)
amdsmi_board_info_t board_info;
amdsmi_get_gpu_board_info(processor, &board_info);

// ASIC info
amdsmi_asic_info_t asic_info;
amdsmi_get_gpu_asic_info(processor, &asic_info);

// VRAM info
amdsmi_vram_info_t vram_info;
amdsmi_get_gpu_vram_info(processor, &vram_info);

// UUID
char uuid[AMDSMI_GPU_UUID_SIZE];
amdsmi_get_gpu_device_uuid(processor, nullptr, uuid);

// BDF (Bus:Device.Function)
amdsmi_bdf_t bdf;
amdsmi_get_gpu_device_bdf(processor, &bdf);
```

### PCIe Info

```cpp
amdsmi_pcie_info_t pcie_info;
amdsmi_get_pcie_info(processor, &pcie_info);
// pcie_info.pcie_static (slot_type, max_width, max_speed)
// pcie_info.pcie_metric (current width, speed, bandwidth)

// PCIe throughput
uint64_t sent, received, max_pkt_sz;
amdsmi_get_gpu_pci_throughput(processor, &sent, &received, &max_pkt_sz);
```

### Fan Speed

```cpp
int64_t speed;
amdsmi_get_gpu_fan_speed(processor, 0, &speed);

int64_t max_speed;
amdsmi_get_gpu_fan_speed_max(processor, 0, &max_speed);

int64_t rpm;
amdsmi_get_gpu_fan_rpms(processor, 0, &rpm);
```

### Firmware Info

```cpp
amdsmi_fw_info_t fw_info;
amdsmi_get_fw_info(processor, &fw_info);
// fw_info.fw_list[i].fw_id, fw_version
```

## Common CPU Queries

```cpp
// CPU socket power
uint32_t power;
amdsmi_get_cpu_socket_power(processor, &power);  // milliwatts

// CPU temperature
uint32_t temp;
amdsmi_get_cpu_socket_temperature(processor, &temp);

// CPU energy
uint64_t energy;
amdsmi_get_cpu_socket_energy(processor, &energy);

// Core boost limit
uint32_t boost;
amdsmi_get_cpu_core_boostlimit(core_processor, &boost);
```

## AI NIC (Network Interface Card) Functions

### NIC Discovery

```cpp
// Initialize with NIC support
amdsmi_init(AMDSMI_INIT_AMD_NICS);

// Get socket handles
uint32_t socket_count = 0;
amdsmi_get_socket_handles(&socket_count, nullptr);
std::vector<amdsmi_socket_handle> sockets(socket_count);
amdsmi_get_socket_handles(&socket_count, sockets.data());

// Get NIC processor handles (two-call pattern)
uint32_t nic_count = 0;
amdsmi_get_processor_handles_by_type(sockets[0],
                                     AMDSMI_PROCESSOR_TYPE_AMD_NIC,
                                     nullptr, &nic_count);
std::vector<amdsmi_processor_handle> nics(nic_count);
amdsmi_get_processor_handles_by_type(sockets[0],
                                     AMDSMI_PROCESSOR_TYPE_AMD_NIC,
                                     nics.data(), &nic_count);
```

### NIC Data Structures

```cpp
// NIC Link Type (affinity to GPUs/CPUs)
typedef enum {
    AMDSMI_NIC_LINK_TYPE_UNKNOWN,   // Unknown connection type
    AMDSMI_NIC_LINK_TYPE_PCIE,      // Same PCIe root complex
    AMDSMI_NIC_LINK_TYPE_NUMA,      // Different PCIe but same CPU/NUMA
    AMDSMI_NIC_LINK_TYPE_X_NUMA     // Different CPUs/NUMA nodes
} amdsmi_nic_link_type_t;

// NIC Statistic Entry
typedef struct {
    char name[AMDSMI_MAX_STRING_LENGTH];  // e.g., "rx_rdma_ucast_bytes"
    uint64_t value;                        // Counter value
} amdsmi_nic_stat_t;

// NIC ASIC Information
typedef struct {
    uint16_t vendor_id;
    uint16_t subvendor_id;
    uint16_t device_id;
    uint16_t subsystem_id;
    uint8_t revision;
    char permanent_address[AMDSMI_MAX_STRING_LENGTH];
    char product_name[AMDSMI_MAX_STRING_LENGTH];
    char part_number[AMDSMI_MAX_STRING_LENGTH];
    char serial_number[AMDSMI_MAX_STRING_LENGTH];
    char vendor_name[AMDSMI_MAX_STRING_LENGTH];
} amdsmi_nic_asic_info_t;

// NIC Bus Information
typedef struct {
    amdsmi_bdf_t bdf;                     // PCI Bus:Device.Function
    uint8_t max_pcie_width;               // Maximum PCIe lanes
    uint32_t max_pcie_speed;              // Maximum speed in GT/s
    char pcie_interface_version[AMDSMI_MAX_STRING_LENGTH];
    char slot_type[AMDSMI_MAX_STRING_LENGTH];
} amdsmi_nic_bus_info_t;

// NIC NUMA Information
typedef struct {
    uint8_t node;                         // NUMA node number
    char affinity[AMDSMI_MAX_STRING_LENGTH];  // CPU affinity mask
} amdsmi_nic_numa_info_t;

// NIC Firmware Information
typedef struct {
    char name[AMDSMI_MAX_STRING_LENGTH];
    char version[AMDSMI_MAX_STRING_LENGTH];
} amdsmi_nic_fw_t;

typedef struct {
    uint32_t num_fw;
    amdsmi_nic_fw_t fw[AMDSMI_MAX_NIC_FW];  // Up to 16 firmware components
} amdsmi_nic_fw_info_t;

// NIC Port Information
typedef struct {
    amdsmi_bdf_t bdf;
    uint32_t port_num;
    char type[AMDSMI_MAX_STRING_LENGTH];
    char flavour[AMDSMI_MAX_STRING_LENGTH];
    char netdev[AMDSMI_MAX_STRING_LENGTH];    // e.g., "enp226s0"
    uint8_t ifindex;
    char mac_address[AMDSMI_MAX_STRING_LENGTH];
    uint8_t carrier;                          // Link status (0=down, 1=up)
    uint16_t mtu;                             // Maximum transmission unit
    char link_state[AMDSMI_MAX_STRING_LENGTH];
    uint32_t link_speed;                      // Link speed in Mbps
    uint32_t active_fec;                      // FEC modes bitmask
    char autoneg[AMDSMI_MAX_STRING_LENGTH];
    char pause_autoneg[AMDSMI_MAX_STRING_LENGTH];
    char pause_rx[AMDSMI_MAX_STRING_LENGTH];
    char pause_tx[AMDSMI_MAX_STRING_LENGTH];
} amdsmi_nic_port_t;

typedef struct {
    uint32_t num_ports;
    amdsmi_nic_port_t ports[AMDSMI_MAX_NIC_PORTS];  // Up to 32 ports
} amdsmi_nic_port_info_t;

// NIC Driver Information
typedef struct {
    char name[AMDSMI_MAX_STRING_LENGTH];
    char version[AMDSMI_MAX_STRING_LENGTH];
} amdsmi_nic_driver_info_t;

// NIC RDMA Port Information
typedef struct {
    char netdev[AMDSMI_MAX_STRING_LENGTH];    // Network device name
    char state[AMDSMI_MAX_STRING_LENGTH];     // "ACTIVE", "DOWN", etc.
    uint8_t rdma_port;                        // RDMA port number
    uint16_t max_mtu;
    uint16_t active_mtu;
} amdsmi_nic_rdma_port_info_t;

// NIC RDMA Device Information
typedef struct {
    char rdma_dev[AMDSMI_MAX_STRING_LENGTH];  // e.g., "rdma0"
    char node_guid[AMDSMI_MAX_STRING_LENGTH]; // Global Unique Identifier
    char node_type[AMDSMI_MAX_STRING_LENGTH]; // "CA", "Switch", etc.
    char sys_image_guid[AMDSMI_MAX_STRING_LENGTH];
    char fw_ver[AMDSMI_MAX_STRING_LENGTH];
    uint8_t num_rdma_ports;
    amdsmi_nic_rdma_port_info_t rdma_port_info[AMDSMI_MAX_NIC_PORTS];
} amdsmi_nic_rdma_dev_info_t;

typedef struct {
    uint8_t num_rdma_dev;
    amdsmi_nic_rdma_dev_info_t rdma_dev_info[AMDSMI_MAX_NIC_RDMA_DEV];
} amdsmi_nic_rdma_devices_info_t;
```

### NIC Query Functions

```cpp
// Get NIC driver information
amdsmi_nic_driver_info_t driver_info;
amdsmi_get_nic_driver_info(nic_handle, &driver_info);
// driver_info.name, driver_info.version

// Get NIC ASIC info (vendor, product, serial)
amdsmi_nic_asic_info_t asic_info;
amdsmi_get_nic_asic_info(nic_handle, &asic_info);
// asic_info.vendor_id, device_id, product_name, serial_number

// Get NIC bus info (PCIe configuration)
amdsmi_nic_bus_info_t bus_info;
amdsmi_get_nic_bus_info(nic_handle, &bus_info);
// bus_info.bdf, max_pcie_width, max_pcie_speed

// Get NIC NUMA affinity
amdsmi_nic_numa_info_t numa_info;
amdsmi_get_nic_numa_info(nic_handle, &numa_info);
// numa_info.node, numa_info.affinity

// Get NIC port information (MAC, link state, speed)
amdsmi_nic_port_info_t port_info;
amdsmi_get_nic_port_info(nic_handle, &port_info);
// port_info.num_ports, port_info.ports[i].mac_address, carrier, link_speed

// Get NIC RDMA device information
amdsmi_nic_rdma_devices_info_t rdma_info;
amdsmi_get_nic_rdma_dev_info(nic_handle, &rdma_info);
// rdma_info.num_rdma_dev, rdma_info.rdma_dev_info[i].rdma_dev
```

### NIC RDMA Port Statistics

The statistics API uses a two-call pattern:

```cpp
// First call: Get count of available statistics
uint32_t num_stats = 0;
amdsmi_get_nic_rdma_port_statistics(nic_handle, rdma_port_idx,
                                    &num_stats, nullptr);

// Second call: Allocate and retrieve statistics
std::vector<amdsmi_nic_stat_t> stats(num_stats);
amdsmi_get_nic_rdma_port_statistics(nic_handle, rdma_port_idx,
                                    &num_stats, stats.data());

// Process statistics
for (uint32_t i = 0; i < num_stats; i++) {
    std::cout << stats[i].name << ": " << stats[i].value << std::endl;
}
```

### Common NIC Statistics

RDMA port statistics typically include:

| Statistic Name | Description |
|----------------|-------------|
| `rx_rdma_ucast_bytes` | Unicast bytes received |
| `rx_rdma_ucast_pkts` | Unicast packets received |
| `tx_rdma_ucast_bytes` | Unicast bytes transmitted |
| `tx_rdma_ucast_pkts` | Unicast packets transmitted |
| `rx_rdma_cnp_pkts` | Congestion Notification Protocol packets received |
| `tx_rdma_cnp_pkts` | Congestion Notification Protocol packets transmitted |

### NIC Constants

```cpp
#define AMDSMI_MAX_NIC_PORTS        32   // Maximum NIC ports per device
#define AMDSMI_MAX_NIC_RDMA_DEV     32   // Maximum RDMA devices per NIC
#define AMDSMI_MAX_NIC_FW           16   // Maximum firmware components
#define AMDSMI_MAX_STRING_LENGTH    64   // String field length
```

### Complete NIC Example

```cpp
#include <iostream>
#include <vector>
#include "amd_smi/amdsmi.h"

int main() {
    // Initialize with NIC support
    amdsmi_status_t ret = amdsmi_init(AMDSMI_INIT_AMD_NICS);
    if (ret != AMDSMI_STATUS_SUCCESS) return 1;

    // Get sockets
    uint32_t socket_count = 0;
    amdsmi_get_socket_handles(&socket_count, nullptr);
    std::vector<amdsmi_socket_handle> sockets(socket_count);
    amdsmi_get_socket_handles(&socket_count, sockets.data());

    // Get NIC handles
    for (uint32_t s = 0; s < socket_count; s++) {
        uint32_t nic_count = 0;
        amdsmi_get_processor_handles_by_type(sockets[s],
                                             AMDSMI_PROCESSOR_TYPE_AMD_NIC,
                                             nullptr, &nic_count);
        std::vector<amdsmi_processor_handle> nics(nic_count);
        amdsmi_get_processor_handles_by_type(sockets[s],
                                             AMDSMI_PROCESSOR_TYPE_AMD_NIC,
                                             nics.data(), &nic_count);

        // Query each NIC
        for (uint32_t i = 0; i < nic_count; i++) {
            // Get ASIC info
            amdsmi_nic_asic_info_t asic_info;
            amdsmi_get_nic_asic_info(nics[i], &asic_info);
            std::cout << "NIC: " << asic_info.product_name << std::endl;

            // Get port info
            amdsmi_nic_port_info_t port_info;
            amdsmi_get_nic_port_info(nics[i], &port_info);
            std::cout << "Ports: " << port_info.num_ports << std::endl;

            for (uint32_t p = 0; p < port_info.num_ports; p++) {
                std::cout << "  Port " << p << ": "
                          << port_info.ports[p].netdev
                          << " MAC: " << port_info.ports[p].mac_address
                          << " Speed: " << port_info.ports[p].link_speed << "Mbps"
                          << " State: " << (port_info.ports[p].carrier ? "UP" : "DOWN")
                          << std::endl;
            }

            // Get RDMA devices
            amdsmi_nic_rdma_devices_info_t rdma_info;
            amdsmi_get_nic_rdma_dev_info(nics[i], &rdma_info);

            for (uint32_t r = 0; r < rdma_info.num_rdma_dev; r++) {
                auto& dev = rdma_info.rdma_dev_info[r];
                std::cout << "  RDMA Device: " << dev.rdma_dev << std::endl;

                // Get statistics for each RDMA port
                for (uint32_t rp = 0; rp < dev.num_rdma_ports; rp++) {
                    uint32_t num_stats = 0;
                    amdsmi_get_nic_rdma_port_statistics(nics[i], rp,
                                                        &num_stats, nullptr);

                    std::vector<amdsmi_nic_stat_t> stats(num_stats);
                    amdsmi_get_nic_rdma_port_statistics(nics[i], rp,
                                                        &num_stats, stats.data());

                    std::cout << "    Port " << rp << " Statistics:" << std::endl;
                    for (uint32_t st = 0; st < num_stats; st++) {
                        std::cout << "      " << stats[st].name
                                  << ": " << stats[st].value << std::endl;
                    }
                }
            }
        }
    }

    amdsmi_shut_down();
    return 0;
}
```

## GPU Control Functions

```cpp
// Set power cap (in microwatts)
amdsmi_set_power_cap(processor, 0, power_cap_uw);

// Set fan speed (0-255 or use AMDSMI_MAX_FAN_SPEED)
amdsmi_set_gpu_fan_speed(processor, 0, speed);
amdsmi_reset_gpu_fan(processor, 0);  // Return to auto

// Set performance level
amdsmi_set_gpu_perf_level(processor, AMDSMI_DEV_PERF_LEVEL_AUTO);

// Set clock frequency
amdsmi_set_clk_freq(processor, AMDSMI_CLK_TYPE_GFX, freq_bitmask);
```

## Topology Functions

```cpp
// Get link type between two GPUs
amdsmi_io_link_type_t link_type;
uint64_t hops;
amdsmi_topo_get_link_type(processor1, processor2, &hops, &link_type);

// Check P2P accessibility
bool accessible;
amdsmi_is_P2P_accessible(processor1, processor2, &accessible);

// Get NUMA node
uint32_t numa_node;
amdsmi_topo_get_numa_node_number(processor, &numa_node);
```

## GPU Metrics Structure (amdsmi_gpu_metrics_t)

The `amdsmi_gpu_metrics_t` structure provides comprehensive GPU telemetry in a single read. This is the most efficient way to get multiple metrics at once.

### Reading GPU Metrics

```cpp
amdsmi_gpu_metrics_t metrics;
amdsmi_status_t ret = amdsmi_get_gpu_metrics_info(processor, &metrics);
if (ret == AMDSMI_STATUS_SUCCESS) {
    // Check version first
    uint16_t version = metrics.common_header.format_revision;

    // Access metrics fields
    uint16_t temp = metrics.temperature_edge;      // Temperature in C
    uint16_t gfx_activity = metrics.average_gfx_activity;  // GFX utilization %
    uint16_t power = metrics.average_socket_power; // Power in W
}
```

### Metrics Table Versions

The structure evolved across versions. Check `common_header.format_revision`:

| Version | Key Additions |
|---------|---------------|
| v1.0    | Base: temps, activity, power, clocks, fan, PCIe |
| v1.1    | temperature_hbm[], gfx/mem_activity_acc |
| v1.3    | voltage_soc/gfx/mem, indep_throttle_status |
| v1.4    | vcn_activity[], multi-value clocks (arrays) |
| v1.5    | jpeg_activity[], pcie_nak counters |
| v1.6    | xcp_stats[] (partition metrics), throttle residencies |
| v1.7    | vram_max_bandwidth, gfx_below_host_limit_acc |
| v1.8    | Extended xcp_stats fields |

### Detecting Unsupported Values

**Critical**: When a metric is not supported by the hardware/firmware, it returns the maximum value for its type:

```cpp
// Unsupported value markers
constexpr uint16_t UNSUPPORTED_16 = 0xFFFF;      // 65535
constexpr uint32_t UNSUPPORTED_32 = 0xFFFFFFFF;  // 4294967295
constexpr uint64_t UNSUPPORTED_64 = 0xFFFFFFFFFFFFFFFF;

// Helper to check if value is valid
template<typename T>
bool is_metric_supported(T value) {
    return value != std::numeric_limits<T>::max();
}

// Usage example
if (is_metric_supported(metrics.average_gfx_activity)) {
    std::cout << "GFX activity: " << metrics.average_gfx_activity << "%" << std::endl;
} else {
    std::cout << "GFX activity: N/A" << std::endl;
}
```

### XCP Stats vs VCN Activity

The `xcp_stats[]` array provides per-partition metrics for multi-partition GPUs (MI300X, etc.). However, **it may not be supported on all platforms**.

```cpp
// xcp_stats structure (per partition)
struct amdsmi_gpu_xcp_metrics_t {
    uint32_t gfx_busy_inst[AMDSMI_MAX_NUM_XCC];  // GFX utilization per XCC
    uint16_t jpeg_busy[AMDSMI_MAX_NUM_JPEG_ENG_V1];  // JPEG engine %
    uint16_t vcn_busy[AMDSMI_MAX_NUM_VCN];   // VCN (decoder) utilization %
    uint64_t gfx_busy_acc[AMDSMI_MAX_NUM_XCC];  // Accumulated GFX activity
    // v1.7+ additions
    uint64_t gfx_below_host_limit_acc[AMDSMI_MAX_NUM_XCC];
    // v1.8+ additions
    uint64_t gfx_below_host_limit_ppt_acc[AMDSMI_MAX_NUM_XCC];
    uint64_t gfx_below_host_limit_thm_acc[AMDSMI_MAX_NUM_XCC];
};
```

**Important**: Both `xcp_stats[].vcn_busy[]` and `vcn_activity[]` can return `0xFFFF` when unsupported. The same applies to `jpeg_busy[]` and `gfx_busy_inst[]` (returns `0xFFFFFFFF`).

**Fallback strategy** - try `xcp_stats.vcn_busy` first, fall back to `vcn_activity`:

```cpp
// Helper to get VCN activity with fallback
uint16_t get_vcn_activity(const amdsmi_gpu_metrics_t& metrics,
                          uint16_t partition, uint16_t vcn_idx) {
    // Try xcp_stats.vcn_busy first (per-partition, more detailed)
    if (partition < metrics.num_partition) {
        uint16_t vcn_busy = metrics.xcp_stats[partition].vcn_busy[vcn_idx];
        if (is_metric_supported(vcn_busy)) {
            return vcn_busy;
        }
    }

    // Fallback to global vcn_activity
    if (vcn_idx < AMDSMI_MAX_NUM_VCN) {
        uint16_t vcn_act = metrics.vcn_activity[vcn_idx];
        if (is_metric_supported(vcn_act)) {
            return vcn_act;
        }
    }

    return UINT16_MAX;  // Not available
}

// Usage
for (uint16_t p = 0; p < std::max<uint16_t>(metrics.num_partition, 1); p++) {
    for (int v = 0; v < AMDSMI_MAX_NUM_VCN; v++) {
        uint16_t activity = get_vcn_activity(metrics, p, v);
        if (is_metric_supported(activity)) {
            std::cout << "VCN" << v << " activity: " << activity << "%" << std::endl;
        }
    }
}
```

**Same pattern applies to GFX activity**:

```cpp
// xcp_stats.gfx_busy_inst[] (uint32_t) - per XCC, per partition
// Falls back to average_gfx_activity (uint16_t) - global average

uint32_t get_gfx_activity(const amdsmi_gpu_metrics_t& metrics,
                          uint16_t partition, uint16_t xcc_idx) {
    if (partition < metrics.num_partition) {
        uint32_t gfx = metrics.xcp_stats[partition].gfx_busy_inst[xcc_idx];
        if (is_metric_supported(gfx)) {
            return gfx;
        }
    }
    // Fallback to global average
    if (is_metric_supported(metrics.average_gfx_activity)) {
        return metrics.average_gfx_activity;
    }
    return UINT32_MAX;
}
```

### Key Metrics Fields

| Field | Type | Description |
|-------|------|-------------|
| `temperature_edge` | uint16_t | Edge temperature (C) |
| `temperature_hotspot` | uint16_t | Hotspot/junction temp (C) |
| `temperature_mem` | uint16_t | Memory temperature (C) |
| `temperature_hbm[]` | uint16_t[4] | HBM temperatures (C) |
| `average_gfx_activity` | uint16_t | GFX engine utilization (%) |
| `average_umc_activity` | uint16_t | Memory controller utilization (%) |
| `average_mm_activity` | uint16_t | Multimedia (UVD/VCN) utilization (%) |
| `vcn_activity[]` | uint16_t[4] | Per-VCN utilization (%) |
| `jpeg_activity[]` | uint16_t[32] | Per-JPEG engine utilization (%) |
| `average_socket_power` | uint16_t | Average power (W) |
| `current_socket_power` | uint16_t | Instantaneous power (W) |
| `energy_accumulator` | uint64_t | Energy counter (15.259uJ per tick) |
| `current_gfxclk` | uint16_t | Current GFX clock (MHz) |
| `current_gfxclks[]` | uint16_t[8] | Per-XCC GFX clocks (v1.4+) |
| `current_uclk` | uint16_t | Current memory clock (MHz) |
| `throttle_status` | uint32_t | Throttle reason bitmask |
| `pcie_link_width` | uint16_t | PCIe lanes in use |
| `pcie_link_speed` | uint16_t | PCIe speed (0.1 GT/s units) |
| `xgmi_link_width` | uint16_t | XGMI width (GB/s) |
| `num_partition` | uint16_t | Number of active partitions |
| `xcp_stats[]` | struct[8] | Per-partition metrics (v1.6+) |

## Error Handling

```cpp
amdsmi_status_t ret = amdsmi_some_function(...);
if (ret != AMDSMI_STATUS_SUCCESS) {
    const char* err_str;
    amdsmi_status_code_to_string(ret, &err_str);
    std::cerr << "Error: " << err_str << std::endl;
}
```

### Common Status Codes

- `AMDSMI_STATUS_SUCCESS` - Operation successful
- `AMDSMI_STATUS_NOT_SUPPORTED` - Feature not supported
- `AMDSMI_STATUS_NOT_INIT` - Library not initialized
- `AMDSMI_STATUS_INVAL` - Invalid arguments
- `AMDSMI_STATUS_NO_PERM` - Permission denied
- `AMDSMI_STATUS_NOT_FOUND` - Device/resource not found

## Environment Variables

- `AMDSMI_GPU_METRICS_CACHE_MS` - GPU metrics cache duration (default: 1ms, 0 to disable)
- `AMDSMI_ASIC_INFO_CACHE_MS` - ASIC info cache duration (default: 10000ms)

## Complete Example (GPU + CPU + NIC)

```cpp
#include <iostream>
#include <vector>
#include "amd_smi/amdsmi.h"

int main() {
    // Initialize all processor types
    amdsmi_status_t ret = amdsmi_init(AMDSMI_INIT_ALL_PROCESSORS);
    if (ret != AMDSMI_STATUS_SUCCESS) return 1;

    uint32_t socket_count = 0;
    amdsmi_get_socket_handles(&socket_count, nullptr);
    std::vector<amdsmi_socket_handle> sockets(socket_count);
    amdsmi_get_socket_handles(&socket_count, sockets.data());

    for (uint32_t i = 0; i < socket_count; i++) {
        std::cout << "=== Socket " << i << " ===" << std::endl;

        // Query GPUs
        uint32_t gpu_count = 0;
        amdsmi_get_processor_handles_by_type(sockets[i],
                                             AMDSMI_PROCESSOR_TYPE_AMD_GPU,
                                             nullptr, &gpu_count);
        std::vector<amdsmi_processor_handle> gpus(gpu_count);
        amdsmi_get_processor_handles_by_type(sockets[i],
                                             AMDSMI_PROCESSOR_TYPE_AMD_GPU,
                                             gpus.data(), &gpu_count);

        for (uint32_t j = 0; j < gpu_count; j++) {
            amdsmi_board_info_t board_info;
            amdsmi_get_gpu_board_info(gpus[j], &board_info);
            std::cout << "GPU: " << board_info.product_name << std::endl;

            int64_t temp;
            amdsmi_get_temp_metric(gpus[j], AMDSMI_TEMPERATURE_TYPE_EDGE,
                                   AMDSMI_TEMP_CURRENT, &temp);
            std::cout << "  Temperature: " << temp << "C" << std::endl;

            uint64_t vram_used, vram_total;
            amdsmi_get_gpu_memory_total(gpus[j], AMDSMI_MEM_TYPE_VRAM, &vram_total);
            amdsmi_get_gpu_memory_usage(gpus[j], AMDSMI_MEM_TYPE_VRAM, &vram_used);
            std::cout << "  VRAM: " << vram_used / (1024*1024) << "/"
                      << vram_total / (1024*1024) << " MB" << std::endl;
        }

        // Query NICs
        uint32_t nic_count = 0;
        amdsmi_get_processor_handles_by_type(sockets[i],
                                             AMDSMI_PROCESSOR_TYPE_AMD_NIC,
                                             nullptr, &nic_count);
        std::vector<amdsmi_processor_handle> nics(nic_count);
        amdsmi_get_processor_handles_by_type(sockets[i],
                                             AMDSMI_PROCESSOR_TYPE_AMD_NIC,
                                             nics.data(), &nic_count);

        for (uint32_t j = 0; j < nic_count; j++) {
            amdsmi_nic_asic_info_t nic_info;
            amdsmi_get_nic_asic_info(nics[j], &nic_info);
            std::cout << "NIC: " << nic_info.product_name << std::endl;

            amdsmi_nic_port_info_t port_info;
            amdsmi_get_nic_port_info(nics[j], &port_info);
            std::cout << "  Ports: " << port_info.num_ports << std::endl;
        }
    }

    amdsmi_shut_down();
    return 0;
}
```

## API Reference Links

- [C++ API Reference](https://rocm.docs.amd.com/projects/amdsmi/en/latest/reference/amdsmi-cpp-api.html)
- [Usage Examples](https://rocm.docs.amd.com/projects/amdsmi/en/latest/how-to/amdsmi-cpp-lib.html)
- [Source Code](https://github.com/ROCm/rocm-systems/tree/develop/projects/amdsmi)
- [AINIC PR #2798](https://github.com/ROCm/rocm-systems/pull/2798)
