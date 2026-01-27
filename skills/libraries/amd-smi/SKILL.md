---
name: amd-smi-library
description: AMD SMI C++ library for GPU/CPU monitoring and management. Use when working with AMD hardware monitoring, GPU temperature, power, memory, clocks, PCIe, XGMI, or any amdsmi.h functions.
---

# AMD SMI C++ Library

AMD System Management Interface library for monitoring and managing AMD GPUs and CPUs.

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

// Or for all processors
ret = amdsmi_init(AMDSMI_INIT_ALL_PROCESSORS);

// ... use the library ...

// Clean up - MUST be called
ret = amdsmi_shut_down();
```

## Core Concepts

### Handles Hierarchy

```
Socket → Processor (GPU/CPU) → Core (for CPUs)
```

- **Socket handle**: Physical hardware socket
- **Processor handle**: GPU or CPU within a socket (may change between app restarts)
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

## Complete Example

```cpp
#include <iostream>
#include <vector>
#include "amd_smi/amdsmi.h"

int main() {
    amdsmi_status_t ret = amdsmi_init(AMDSMI_INIT_AMD_GPUS);
    if (ret != AMDSMI_STATUS_SUCCESS) return 1;

    uint32_t socket_count = 0;
    amdsmi_get_socket_handles(&socket_count, nullptr);
    std::vector<amdsmi_socket_handle> sockets(socket_count);
    amdsmi_get_socket_handles(&socket_count, sockets.data());

    for (uint32_t i = 0; i < socket_count; i++) {
        uint32_t device_count = 0;
        amdsmi_get_processor_handles(sockets[i], &device_count, nullptr);
        std::vector<amdsmi_processor_handle> devices(device_count);
        amdsmi_get_processor_handles(sockets[i], &device_count, devices.data());

        for (uint32_t j = 0; j < device_count; j++) {
            amdsmi_board_info_t board_info;
            amdsmi_get_gpu_board_info(devices[j], &board_info);
            std::cout << "GPU: " << board_info.product_name << std::endl;

            int64_t temp;
            amdsmi_get_temp_metric(devices[j], AMDSMI_TEMPERATURE_TYPE_EDGE,
                                   AMDSMI_TEMP_CURRENT, &temp);
            std::cout << "Temperature: " << temp << "C" << std::endl;

            uint64_t vram_used, vram_total;
            amdsmi_get_gpu_memory_total(devices[j], AMDSMI_MEM_TYPE_VRAM, &vram_total);
            amdsmi_get_gpu_memory_usage(devices[j], AMDSMI_MEM_TYPE_VRAM, &vram_used);
            std::cout << "VRAM: " << vram_used / (1024*1024) << "/"
                      << vram_total / (1024*1024) << " MB" << std::endl;
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
