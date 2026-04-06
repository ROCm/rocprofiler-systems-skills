---
name: verify_pmc_metrics
description: Use when verifying GPU PMC (AMD SMI), SDMA, JPEG, VCN, XGMI, PCIe, or NIC RDMA metrics across Perfetto and RocPD output formats
---

# PMC Verification

Per-metric verification of AMD SMI Performance Monitoring Counter (PMC) implementation across all output formats.

<IMPORTANT>
- Test each metric INDIVIDUALLY with its specific workload.
- Always test ALL THREE output formats per metric: Perfetto Standard, Perfetto Legacy, and RocPD.
- Use the rocprof-sys MCP tools to analyze Perfetto traces, sqlite3 for RocPD databases.
- **Run tests automatically** - do NOT ask for user confirmation before running workloads.
- Execute all profiling commands directly using the Bash tool.
</IMPORTANT>

## Output Formats

| # | Output Type | Environment Variables | Description |
|---|-------------|----------------------|-------------|
| 1 | **Perfetto** | `ROCPROFSYS_TRACE=1` | Standard cached Perfetto format |
| 2 | **Perfetto Legacy** | `ROCPROFSYS_TRACE=1 ROCPROFSYS_TRACE_LEGACY=true` | Legacy direct Perfetto format |
| 3 | **RocPD** | `ROCPROFSYS_USE_ROCPD=1` | SQLite database format |

## Metric Registry

Each metric has its own config value, workload, expected Perfetto track pattern, and RocPD column name.

### GPU Metrics

| # | Metric | Config Value | Workload | Perfetto Track Pattern | RocPD Name | Notes |
|---|--------|-------------|----------|----------------------|------------|-------|
| 1 | Power | `power` | `./transpose` | `GPU [N] Current Power (S)` | `device_power` | Watts |
| 2 | Temperature | `temp` | `./transpose` | `GPU [N] Temperature (S)` | `device_temp` | Celsius |
| 3 | Memory Usage | `mem_usage` | `./transpose` | `GPU [N] Memory Usage (S)` | `device_memory_usage` | MB |
| 4 | GFX Busy | `busy` | `./transpose` | `GPU [N] GFX Busy (S)` | `device_busy_gfx` | % |
| 5 | UMC Busy | `busy` | `./transpose` | `GPU [N] UMC Busy (S)` | `device_busy_umc` | % |
| 6 | MM Busy | `busy` | `./transpose` | `GPU [N] MM Busy (S)` | `device_busy_mm` | % |
| 7 | SDMA Usage | `sdma_usage` | `./sdma_test` | `GPU [N] SDMA Usage (S)` | `device_sdma_usage` | % |
| 8 | PCIe Link Speed | `pcie` | `./transpose` | `GPU [N] PCIe Link Speed (S)` | `device_pcie_link_speed` | GT/s |
| 9 | PCIe Link Width | `pcie` | `./transpose` | `GPU [N] PCIe Link Width (S)` | `device_pcie_link_width` | lanes |
| 10 | PCIe Bandwidth Acc | `pcie` | `./transpose` | `GPU [N] PCIe Bandwidth Acc (S)` | `device_pcie_bandwidth_acc` | bytes |
| 11 | PCIe Bandwidth Inst | `pcie` | `./transpose` | `GPU [N] PCIe Bandwidth Inst (S)` | `device_pcie_bandwidth_inst` | bytes/s |
| 12 | VCN Activity | `vcn_activity` | `./videodecode -i <video>` | `GPU [N] VCN Activity ... (S)` | `device_vcn_activity_*` | % |
| 13 | JPEG Activity | `jpeg_busy,jpeg_activity` | `./jpegdecode -i <images>` | `GPU [N] JPEG Activity ... (S)` | `device_jpeg_activity_*` | %, Navi vs MI300 differs |
| 14 | XGMI | `xgmi` | `./transpose` | `GPU [N] XGMI ... (S)` | `device_xgmi_*` | Skip if no XGMI links |

### NIC (AINIC) Metrics

| # | Metric | Config Value | Workload | Perfetto Track Pattern | RocPD Name | Notes |
|---|--------|-------------|----------|----------------------|------------|-------|
| 15 | RX RDMA Bytes | `all` + NIC env | `./transpose` | `NIC [N] RX RDMA Bytes (S)` | `nic_rx_ucast_bytes` | Use `AMDSMI_FAKE_AINIC=1` |
| 16 | TX RDMA Bytes | `all` + NIC env | `./transpose` | `NIC [N] TX RDMA Bytes (S)` | `nic_tx_ucast_bytes` | |
| 17 | RX RDMA Packets | `all` + NIC env | `./transpose` | `NIC [N] RX RDMA Packets (S)` | `nic_rx_ucast_pkts` | |
| 18 | TX RDMA Packets | `all` + NIC env | `./transpose` | `NIC [N] TX RDMA Packets (S)` | `nic_tx_ucast_pkts` | |
| 19 | RX CNP Packets | `all` + NIC env | `./transpose` | `NIC [N] RX CNP Packets (S)` | `nic_rx_cnp_pkts` | |
| 20 | TX CNP Packets | `all` + NIC env | `./transpose` | `NIC [N] TX CNP Packets (S)` | `nic_tx_cnp_pkts` | |

### Perfetto Legacy Track Name Differences

Legacy format uses different track naming:
- GPU: `GPU <Metric> [N] (S)` instead of `GPU [N] <Metric> (S)`
- NIC: `NIC <device_name> <Metric> [N] (S)` instead of `NIC [N] <Metric> (S)`
- NIC uses abbreviated forms: `Pkts` vs `Packets`

## Process

<IMPORTANT>
Execute all phases automatically without asking for user confirmation.
Run profiling commands directly - the workloads are safe test applications.
</IMPORTANT>

### Phase 1: Setup

1. Auto-discover build directory (`build/debug`, `build/release`, or `build/`)
2. `cd` into build dir, source `share/rocprofiler-systems/setup-env.sh`
3. Verify workload binaries exist: `transpose`, `sdma_test`, `jpegdecode`, `videodecode`

### Phase 2: Run Per-Metric Tests

For each metric group, run 3 tests (one per output format). Use `/tmp/pmc-test-<metric>-<format>` output paths.

**Template for each metric:**

```bash
source share/rocprofiler-systems/setup-env.sh

# Perfetto Standard
ROCPROFSYS_OUTPUT_PATH=/tmp/pmc-test-<metric>-perfetto \
ROCPROFSYS_TRACE=1 \
ROCPROFSYS_AMD_SMI_METRICS="<config_value>" \
[EXTRA_ENV_VARS] \
bin/rocprof-sys-run -- <workload>

# Perfetto Legacy
ROCPROFSYS_OUTPUT_PATH=/tmp/pmc-test-<metric>-legacy \
ROCPROFSYS_TRACE=1 \
ROCPROFSYS_TRACE_LEGACY=true \
ROCPROFSYS_AMD_SMI_METRICS="<config_value>" \
[EXTRA_ENV_VARS] \
bin/rocprof-sys-run -- <workload>

# RocPD
ROCPROFSYS_OUTPUT_PATH=/tmp/pmc-test-<metric>-rocpd \
ROCPROFSYS_USE_ROCPD=1 \
ROCPROFSYS_AMD_SMI_METRICS="<config_value>" \
[EXTRA_ENV_VARS] \
bin/rocprof-sys-run -- <workload>
```

**Metric groups to test (can share workload runs):**

| Run | Config Value | Workload | Metrics Covered |
|-----|-------------|----------|-----------------|
| gpu-basic | `power,temp,mem_usage,busy` | `./transpose` | Power, Temp, Memory, GFX/UMC/MM Busy |
| sdma | `sdma_usage` | `./sdma_test` | SDMA Usage |
| pcie | `pcie` | `./transpose` | PCIe Link Speed/Width, Bandwidth Acc/Inst |
| vcn | `vcn_activity` | `./videodecode -i <video>` | VCN Activity |
| jpeg | `jpeg_busy,jpeg_activity` | `./jpegdecode -i <images>` | JPEG Activity/Busy |
| xgmi | `xgmi` | `./transpose` | XGMI (skip if unavailable) |
| nic | `all` + NIC env | `./transpose` | All 6 NIC RDMA metrics |

**NIC-specific env vars:**
```bash
AMDSMI_FAKE_AINIC=1
ROCPROFSYS_SAMPLING_AINICS="all"
```

**Workload commands:**

| Workload | Command | Default Runtime | Notes |
|----------|---------|-----------------|-------|
| transpose | `./transpose` | ~2.4 sec | No args needed, 9920x9920, 500 iter |
| sdma_test | `./sdma_test` | ~5-10 sec | 512MB, 10 iter, 10 copies |
| videodecode | `./videodecode -i /opt/rocm/share/rocdecode/video/AMD_driving_virtual_20-H264.264` | Varies | H264 decode |
| jpegdecode | `./jpegdecode -i /opt/rocm/share/rocjpeg/images/` | <1 sec | JPEG decode, short workload |

**IMPORTANT: Workload Runtimes**

- `transpose` and `sdma_test` run long enough for PMC sampling (~2+ sec)
- `jpegdecode` is very short (<0.5 sec) — may get few/no samples in Perfetto Legacy (known timing issue)
- `videodecode` duration depends on video length — short videos may also have low sample counts
- Always use default parameters (no explicit size/iteration arguments)

### Phase 3: Analyze Traces

For each metric group, load and query all 3 traces.

**Perfetto traces (Standard and Legacy):**

```
mcp__rocprof-sys__load_trace(path="<trace-file>", name="<metric>-<format>")
```

Query for GPU metric tracks:
```sql
SELECT t.name,
       COUNT(*) as samples,
       MIN(c.value) as min_val,
       MAX(c.value) as max_val,
       ROUND(AVG(c.value), 2) as avg_val
FROM counter c
JOIN counter_track t ON c.track_id = t.id
WHERE t.name LIKE '%<PATTERN>%' AND t.name LIKE '%(S)%'
GROUP BY t.name
ORDER BY t.name
```

Query for NIC metric tracks:
```sql
SELECT t.name,
       COUNT(*) as samples,
       MIN(c.value) as min_val,
       MAX(c.value) as max_val,
       ROUND(AVG(c.value), 2) as avg_val
FROM counter c
JOIN counter_track t ON c.track_id = t.id
WHERE t.name LIKE '%NIC%' AND t.name LIKE '%(S)%'
GROUP BY t.name
ORDER BY t.name
```

**RocPD databases:**

```bash
# List available PMC metrics
sqlite3 <db-file> "SELECT DISTINCT name FROM rocpd_info_pmc WHERE name LIKE '<pattern>' ORDER BY name;"

# Get metric stats
sqlite3 <db-file> "SELECT p.name, COUNT(*) as samples, MIN(e.value) as min_val, MAX(e.value) as max_val, ROUND(AVG(e.value),2) as avg_val FROM rocpd_pmc_event e JOIN rocpd_info_pmc p ON e.pmc_id = p.id WHERE p.name LIKE '<pattern>' GROUP BY p.name ORDER BY p.name;"
```

### Phase 4: Generate Report

Generate a single summary table plus per-metric detail.

**Report format:**

```markdown
# PMC Verification Report

**Date**: YYYY-MM-DD
**Version**: rocprofiler-systems vX.Y.Z
**Target**: local | <machine>:<path>
**Build Dir**: <build_dir>
**Branch**: <branch_name>

## Summary Table

| # | Metric | Config Value | Workload | Perfetto | Legacy | RocPD | Notes |
|---|--------|-------------|----------|----------|--------|-------|-------|
| 1 | Power | `power` | transpose | PASS (N samples) | PASS (N samples) | PASS (N samples) | |
| 2 | Temperature | `temp` | transpose | PASS | PASS | PASS | |
| ... | ... | ... | ... | ... | ... | ... | ... |

### Status Values

- **PASS (N samples)**: Track present, N samples collected, values look reasonable
- **PASS (0%)**: Track present and sampled, but values are all zero (hardware-dependent)
- **FAIL (no tracks)**: Expected track not found in output
- **FAIL (0 samples)**: Track present but no samples collected
- **SKIP**: Metric not available on this hardware (e.g., XGMI without multi-GPU links)
- **WARN**: Track present but unexpected values (e.g., sentinel values)

## Per-Metric Details

### <Metric Name>

**Config**: `ROCPROFSYS_AMD_SMI_METRICS="<value>"`
**Workload**: `<command>`

#### Perfetto Standard
| Track Name | Samples | Min | Max | Avg |
|------------|---------|-----|-----|-----|
| ... | ... | ... | ... | ... |

#### Perfetto Legacy
| Track Name | Samples | Min | Max | Avg |
|------------|---------|-----|-----|-----|
| ... | ... | ... | ... | ... |

#### RocPD
| PMC Name | Samples | Min | Max | Avg |
|----------|---------|-----|-----|-----|
| ... | ... | ... | ... | ... |

[Repeat for each metric]

## Issues Found
[List any issues with severity: HIGH/MEDIUM/LOW/INFO]

## Conclusion
[Overall assessment]
```

**Save report to:** `planning/pmc-verification-report.md`

## Verification Criteria

For each metric in each output format:

| Criterion | Check |
|-----------|-------|
| Track Presence | Expected track/column appears in output |
| Sample Count | At least 1 sample; ideally 100+ for long workloads |
| Non-Zero Values | Values show activity during workload (metric-dependent) |
| Valid Range | Within expected range (0-100% for activity, >0 for power/temp) |
| No Sentinels | No 0xFFFF or max-value sentinels |

## Common Issues

### Workload Issues

| Issue | Symptom | Cause | Fix |
|-------|---------|-------|-----|
| Short workload | 0-1 samples | Workload < PMC sampling interval | Use longer workload or default params |
| Legacy timing bug | No counter tracks for <0.5 sec workloads | Legacy path sync issue | Known issue; use default params for >2 sec |
| Invalid timestamps | "Invalid timestamp" warnings in legacy | First sample timestamp invalid | Known; drops 1-2 samples |

### GPU Metric Issues

| Issue | Symptom | Cause | Fix |
|-------|---------|-------|-----|
| Missing Perfetto tracks | No counter tracks in standard mode | `cache_policy` not wired | Check cache_policy/perfetto_policy integration |
| SDMA always 0% | Track present but 0% | Consumer GPU (RX) limitation | Normal on Navi; works on MI series |
| JPEG no tracks in Perfetto | JPEG in RocPD but not Perfetto | Missing Perfetto policy for JPEG | Check perfetto_policy.hpp JPEG handling |
| JPEG vs Navi/MI | `jpeg_activity` vs `jpeg_busy` | Different APIs per arch | Use both: `jpeg_busy,jpeg_activity` |
| VCN 0% short video | VCN track 0% | Video too short | Use longer video file |
| XGMI not available | No XGMI tracks | No multi-GPU XGMI links | Mark as SKIP |
| Excessive VCN/JPEG tracks | Many zero-value XCP tracks | MI300-style output on non-XCP GPU | Expected on consumer GPUs |

### NIC Issues

| Issue | Symptom | Cause | Fix |
|-------|---------|-------|-----|
| No NIC devices | 0 NIC devices in log | `ROCPROFSYS_SAMPLING_AINICS` not set | Set to `"all"` |
| NIC not supported | "not supported" log | No RDMA ports | Use `AMDSMI_FAKE_AINIC=1` |
| Missing NIC in Standard | NIC in Legacy but not Standard | cache_policy not integrated | Check NIC cache_policy/perfetto_policy |
| Missing NIC in RocPD | No nic_* in SQLite | RocPD path not handling NIC | Check rocpd_processor NIC handling |

## Integration with Other Skills

| After This Skill | Use |
|------------------|-----|
| Issues found | `planning-bugfix` to plan fix |
| All tests pass | `git-prepare-pull-request` to submit changes |

## Quick Reference

**Per-metric verification (single metric):**
```bash
source share/rocprofiler-systems/setup-env.sh

# Test one metric across all 3 formats
for fmt_name fmt_env in \
  perfetto "ROCPROFSYS_TRACE=1" \
  legacy "ROCPROFSYS_TRACE=1 ROCPROFSYS_TRACE_LEGACY=true" \
  rocpd "ROCPROFSYS_USE_ROCPD=1"; do
    eval "$fmt_env ROCPROFSYS_OUTPUT_PATH=/tmp/pmc-test-<metric>-$fmt_name \
      ROCPROFSYS_AMD_SMI_METRICS='<config>' \
      bin/rocprof-sys-run -- <workload>"
done
```

**Full verification (all metrics):**
Run each metric group from the table above, then load all traces and generate the summary table.

## Remote Execution (SSH)

Same process as local but:
1. SSH into remote, discover build dir
2. Run workloads via SSH with `/tmp/pmc-remote-*` output paths
3. `scp` traces back to local machine
4. Analyze locally with MCP tools
5. Cleanup remote `/tmp/pmc-remote-*`

See previous skill version for detailed remote execution commands.
