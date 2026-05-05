---
name: verify-pmc-metrics
description: Mock-based rigorous PMC metric validation — tests sentinel filtering, value ranges, and architecture-specific behavior across Perfetto and RocPD
---

# Mock-Based PMC Validation

Deterministic validation of AMD SMI Performance Monitoring Counter (PMC) metrics using the mock system (`AMD_SMI_MOCK_CONFIG`). Tests sentinel filtering, expected value ranges, positive presence of configured metrics, and negative absence of unsupported metrics across all output formats.

<IMPORTANT>
- Execute all profiling and validation automatically — do NOT ask for user confirmation.
- Run ALL 6 test matrix entries (2 architectures x 3 formats).
- Sentinel detection is THE critical check — a single leaked sentinel is a FAIL.
- Use rocprof-sys MCP tools for Perfetto traces, sqlite3 for RocPD databases.
- Mock configs are in the worktree at `~/worktree/rocm-systems/amd-smi-mocks/`.
</IMPORTANT>

## Sentinel Value Reference

GPU firmware returns these values for unsupported/unavailable metrics. They must NEVER appear in output.

| Type | Hex | Decimal | Float (Perfetto) | Where Used |
|------|-----|---------|-------------------|------------|
| `uint16_t` | `0xFFFF` | 65535 | 65535.0 | Temperature, activity %, power, voltage, clocks, PCIe width/speed, VCN/JPEG arrays |
| `uint32_t` | `0xFFFFFFFF` | 4294967295 | 4294967295.0 | Various 32-bit fields |
| `uint64_t` | `0xFFFFFFFFFFFFFFFF` | 18446744073709551615 | 1.8446744073709552e+19 | PCIe bandwidth, XGMI data, memory |

Perfetto stores counter values as doubles, so `UINT64_MAX` appears as `1.8446744073709552e+19`. Both exact and float representations must be checked.

## Known Sentinel Filtering Pipeline

| Metric | device.hpp | perfetto_policy.hpp | perfetto_processor.cpp | rocpd_processor.cpp |
|--------|-----------|--------------------|-----------------------|--------------------|
| VCN/JPEG (uint16) | Support check only | Filtered | Filtered | **NOT filtered** |
| XGMI (uint64) | Zeroed via `populate_if_supported()` | N/A | Double-checked | Filtered |
| PCIe (uint16/64) | Zeroed via `populate_if_supported()` | N/A | Relies on zero check | **NOT filtered** |
| NIC RDMA | N/A | N/A | No filtering | No filtering |

**Known leakage risks:**
1. RocPD VCN/JPEG array values (no explicit sentinel filter)
2. RocPD PCIe values (relies on device.hpp zeroing only)
3. NIC metrics in all outputs (no sentinel filtering anywhere)

## Mock Configurations

Two architectures test complementary metric subsets. Located in `~/worktree/rocm-systems/amd-smi-mocks/`.

### MI300X (`mock_mi300x.yaml`)

Data-center GPU with per-XCP metrics, HBM, and NIC.

| Category | What's Configured | Expected Range | Notes |
|----------|------------------|----------------|-------|
| Temperature | hotspot only | [55, 75] | No temperature_edge (sentineled) |
| HBM Temperature | 4 active / 4 total | [40, 60] | Array: active entries have values, rest sentineled |
| Power | current_socket_power | [300, 500] | Watts |
| GFX Busy | gfx_activity | [80, 100] | % |
| UMC Busy | umc_activity | [0, 10] | % |
| MM Busy | NOT configured | N/A | Should be absent (sentineled) |
| VCN Busy | per-XCP, 4 active engines | [0, 10] | Per-XCP format, NOT device-level VCN Activity |
| JPEG Busy | per-XCP, 32 active engines | [0, 10] | Per-XCP format, NOT device-level JPEG Activity |
| PCIe Width | Fixed 16 | 16 | Lanes |
| PCIe Speed | Fixed 32000 | 32000 | MT/s |
| XGMI | NOT configured | N/A | Should be absent (sentineled) |
| SDMA | 2 processes | varies | Cumulative byte counters |
| Memory | vram_used | varies | Derived from vram_used / vram_total |
| Voltages | NOT configured | N/A | Should be absent (sentineled) |
| Fan | NOT configured | N/A | Should be absent (sentineled) |
| NIC RDMA | 6 stats configured | [0, 1000000] | RX/TX bytes, packets, CNP |

### Navi 48 (`mock_navi48.yaml`)

Consumer GPU with device-level metrics, no XCP, no NIC.

| Category | What's Configured | Expected Range | Notes |
|----------|------------------|----------------|-------|
| Temperature | edge, hotspot, mem | [35, 75] | Has temperature_edge |
| HBM Temperature | NOT configured | N/A | Should be absent (sentineled) |
| Power | current_socket_power | [20, 30] | Watts |
| GFX Busy | gfx_activity | [0, 10] | % |
| UMC Busy | umc_activity | [0, 5] | % |
| MM Busy | mm_activity | [0, 10] | % (present, unlike MI300X) |
| VCN Activity | device-level, 1 active / 4 total | [0, 10] | Device-level, NOT per-XCP |
| JPEG Activity | NOT configured | N/A | Should be absent (sentineled) |
| PCIe Width | Fixed 16 | 16 | Lanes |
| PCIe Speed | Fixed 2500 | 2500 | MT/s |
| XGMI | NOT configured | N/A | Should be absent |
| SDMA | 1 process | varies | Cumulative byte counters |
| Memory | vram_used | varies | Derived |
| Voltages | gfx, soc, mem configured | [700, 1200] | mV |
| Fan | rpm and max configured | [800, 1200] | RPM |
| NIC | No NIC devices | N/A | No NIC tracks should appear |

## Output Formats

| # | Format | Environment Variables |
|---|--------|---------------------|
| 1 | Perfetto Standard | `ROCPROFSYS_TRACE=1` |
| 2 | Perfetto Legacy | `ROCPROFSYS_TRACE=1 ROCPROFSYS_TRACE_LEGACY=true` |
| 3 | RocPD | `ROCPROFSYS_USE_ROCPD=1` |

### Perfetto Track Name Differences

| Format | GPU Pattern | NIC Pattern |
|--------|------------|-------------|
| Standard | `GPU [N] <Metric> (S)` | `NIC [N] <Metric> (S)` |
| Legacy | `GPU <Metric> [N] (S)` | `NIC <device_name> <Metric> [N] (S)` |

Legacy also uses abbreviated forms: `Pkts` vs `Packets`.

## Test Matrix

| Run ID | Config | Format | Extra Env |
|--------|--------|--------|-----------|
| mi300-perfetto | mock_mi300x.yaml | Perfetto Standard | `ROCPROFSYS_SAMPLING_AINICS="all"` |
| mi300-legacy | mock_mi300x.yaml | Perfetto Legacy | `ROCPROFSYS_SAMPLING_AINICS="all"` |
| mi300-rocpd | mock_mi300x.yaml | RocPD | `ROCPROFSYS_SAMPLING_AINICS="all"` |
| navi-perfetto | mock_navi48.yaml | Perfetto Standard | — |
| navi-legacy | mock_navi48.yaml | Perfetto Legacy | — |
| navi-rocpd | mock_navi48.yaml | RocPD | — |

Common env for ALL runs:
- `AMD_SMI_MOCK_CONFIG=<path-to-yaml>`
- `ROCPROFSYS_AMD_SMI_METRICS="all"`

Workload: `./transpose` (mock generates all metric values regardless of workload type).

## Execution

### Phase 1: Setup

1. Auto-discover build directory (`build/debug`, `build/release`, or `build/`)
2. `cd` into build dir, source `share/rocprofiler-systems/setup-env.sh`
3. Verify mock support: `ldd bin/rocprof-sys-run | grep yaml` (yaml-cpp must be linked)
4. Locate mock configs: `~/worktree/rocm-systems/amd-smi-mocks/mock_mi300x.yaml` and `mock_navi48.yaml`
5. Verify `transpose` workload exists

### Phase 2: Execute Test Matrix

Run 6 profiling sessions. Use `/tmp/pmc-validate-<run-id>/` output paths.

```bash
source share/rocprofiler-systems/setup-env.sh

# MI300X — Perfetto Standard
AMD_SMI_MOCK_CONFIG=~/worktree/rocm-systems/amd-smi-mocks/mock_mi300x.yaml \
ROCPROFSYS_OUTPUT_PATH=/tmp/pmc-validate-mi300-perfetto \
ROCPROFSYS_TRACE=1 \
ROCPROFSYS_AMD_SMI_METRICS="all" \
ROCPROFSYS_SAMPLING_AINICS="all" \
bin/rocprof-sys-run -- ./transpose

# MI300X — Perfetto Legacy
AMD_SMI_MOCK_CONFIG=~/worktree/rocm-systems/amd-smi-mocks/mock_mi300x.yaml \
ROCPROFSYS_OUTPUT_PATH=/tmp/pmc-validate-mi300-legacy \
ROCPROFSYS_TRACE=1 \
ROCPROFSYS_TRACE_LEGACY=true \
ROCPROFSYS_AMD_SMI_METRICS="all" \
ROCPROFSYS_SAMPLING_AINICS="all" \
bin/rocprof-sys-run -- ./transpose

# MI300X — RocPD
AMD_SMI_MOCK_CONFIG=~/worktree/rocm-systems/amd-smi-mocks/mock_mi300x.yaml \
ROCPROFSYS_OUTPUT_PATH=/tmp/pmc-validate-mi300-rocpd \
ROCPROFSYS_USE_ROCPD=1 \
ROCPROFSYS_AMD_SMI_METRICS="all" \
ROCPROFSYS_SAMPLING_AINICS="all" \
bin/rocprof-sys-run -- ./transpose

# Navi 48 — Perfetto Standard
AMD_SMI_MOCK_CONFIG=~/worktree/rocm-systems/amd-smi-mocks/mock_navi48.yaml \
ROCPROFSYS_OUTPUT_PATH=/tmp/pmc-validate-navi-perfetto \
ROCPROFSYS_TRACE=1 \
ROCPROFSYS_AMD_SMI_METRICS="all" \
bin/rocprof-sys-run -- ./transpose

# Navi 48 — Perfetto Legacy
AMD_SMI_MOCK_CONFIG=~/worktree/rocm-systems/amd-smi-mocks/mock_navi48.yaml \
ROCPROFSYS_OUTPUT_PATH=/tmp/pmc-validate-navi-legacy \
ROCPROFSYS_TRACE=1 \
ROCPROFSYS_TRACE_LEGACY=true \
ROCPROFSYS_AMD_SMI_METRICS="all" \
bin/rocprof-sys-run -- ./transpose

# Navi 48 — RocPD
AMD_SMI_MOCK_CONFIG=~/worktree/rocm-systems/amd-smi-mocks/mock_navi48.yaml \
ROCPROFSYS_OUTPUT_PATH=/tmp/pmc-validate-navi-rocpd \
ROCPROFSYS_USE_ROCPD=1 \
ROCPROFSYS_AMD_SMI_METRICS="all" \
bin/rocprof-sys-run -- ./transpose
```

### Phase 3: Sentinel Detection (CRITICAL)

This is the most important validation phase. A single leaked sentinel value is a FAIL.

#### Perfetto Traces (Standard and Legacy)

Load each trace with MCP tools, then run:

```sql
-- SENTINEL CHECK: Find ANY sentinel value in PMC counters
SELECT t.name, c.value, c.ts
FROM counter c JOIN counter_track t ON c.track_id = t.id
WHERE t.name LIKE '%(S)%'
  AND (c.value = 65535
    OR c.value = 4294967295
    OR c.value = 18446744073709551615
    OR c.value = 1.8446744073709552e+19
    OR c.value >= 1.844e+19)
LIMIT 20;
-- Expected: 0 rows. ANY result is a FAIL.
```

#### RocPD Databases

```bash
sqlite3 <db-file> "
SELECT p.name, e.value
FROM rocpd_pmc_event e JOIN rocpd_info_pmc p ON e.pmc_id = p.id
WHERE e.value IN (65535, 4294967295, 18446744073709551615)
   OR e.value > 1e18
LIMIT 20;
"
# Expected: 0 rows. ANY result is a FAIL.
```

### Phase 4: Positive Validation (Configured Metrics Present)

Verify that all configured metrics appear in output with expected value ranges.

#### Perfetto SQL

```sql
-- ALL PMC TRACKS: Get every metric with stats
SELECT t.name,
       COUNT(*) as samples,
       MIN(c.value) as min_val,
       MAX(c.value) as max_val,
       ROUND(AVG(c.value), 2) as avg_val
FROM counter c JOIN counter_track t ON c.track_id = t.id
WHERE t.name LIKE '%(S)%'
GROUP BY t.name
ORDER BY t.name;
```

#### RocPD SQL

```bash
sqlite3 <db-file> "
SELECT p.name, COUNT(*) as samples,
       MIN(e.value) as min_val, MAX(e.value) as max_val,
       ROUND(AVG(e.value), 2) as avg_val
FROM rocpd_pmc_event e JOIN rocpd_info_pmc p ON e.pmc_id = p.id
GROUP BY p.name ORDER BY p.name;
"
```

#### MI300X Expected Metrics

| Metric | Perfetto Standard Track | Expected Range | Notes |
|--------|------------------------|----------------|-------|
| Temperature (hotspot) | `GPU [0] Temperature (S)` | [55, 75] | Celsius |
| Power | `GPU [0] Current Power (S)` | [300, 500] | Watts |
| GFX Busy | `GPU [0] GFX Busy (S)` | [80, 100] | % |
| UMC Busy | `GPU [0] UMC Busy (S)` | [0, 10] | % |
| Memory Usage | `GPU [0] Memory Usage (S)` | >0 | MB, derived from vram |
| VCN Busy | `GPU [0] VCN Busy ... (S)` | [0, 10] | Per-XCP, 4 active engines |
| JPEG Busy | `GPU [0] JPEG Busy ... (S)` | [0, 10] | Per-XCP, 32 active engines |
| PCIe Width | `GPU [0] PCIe Link Width (S)` | 16 | Fixed |
| PCIe Speed | `GPU [0] PCIe Link Speed (S)` | 32000 | Fixed MT/s |
| SDMA Usage | `GPU [0] SDMA Usage (S)` | >=0 | Derived from cumulative counters |
| NIC RX Bytes | `NIC [0] RX RDMA Bytes (S)` | [0, 1000000] | |
| NIC TX Bytes | `NIC [0] TX RDMA Bytes (S)` | [0, 1000000] | |
| NIC RX Packets | `NIC [0] RX RDMA Packets (S)` | [0, 1000000] | |
| NIC TX Packets | `NIC [0] TX RDMA Packets (S)` | [0, 1000000] | |
| NIC RX CNP | `NIC [0] RX CNP Packets (S)` | [0, 1000000] | |
| NIC TX CNP | `NIC [0] TX CNP Packets (S)` | [0, 1000000] | |

#### Navi 48 Expected Metrics

| Metric | Perfetto Standard Track | Expected Range | Notes |
|--------|------------------------|----------------|-------|
| Temperature (edge) | `GPU [0] Temperature (S)` | [35, 55] | Has edge temp |
| Power | `GPU [0] Current Power (S)` | [20, 30] | Watts |
| GFX Busy | `GPU [0] GFX Busy (S)` | [0, 10] | % |
| UMC Busy | `GPU [0] UMC Busy (S)` | [0, 5] | % |
| MM Busy | `GPU [0] MM Busy (S)` | [0, 10] | % (absent on MI300X) |
| VCN Activity | `GPU [0] VCN Activity ... (S)` | [0, 10] | Device-level, 1 active |
| Memory Usage | `GPU [0] Memory Usage (S)` | >0 | MB |
| PCIe Width | `GPU [0] PCIe Link Width (S)` | 16 | Fixed |
| PCIe Speed | `GPU [0] PCIe Link Speed (S)` | 2500 | Fixed MT/s |
| SDMA Usage | `GPU [0] SDMA Usage (S)` | >=0 | 1 process |

#### Range Validation SQL

For each metric with a known range, verify no values fall outside:

```sql
-- Example: MI300 power should be [300, 500]
SELECT t.name, c.value
FROM counter c JOIN counter_track t ON c.track_id = t.id
WHERE t.name LIKE '%Current Power%' AND t.name LIKE '%(S)%'
  AND (c.value < 300 OR c.value > 500)
LIMIT 10;
-- Expected: 0 rows
```

Repeat for each metric with known range bounds from the mock config.

### Phase 5: Negative Validation (Unsupported Metrics Absent)

Verify that metrics NOT configured in the mock do NOT appear in output.

#### MI300X Should NOT Have

| Absent Metric | Perfetto Pattern | RocPD Pattern |
|---------------|-----------------|---------------|
| Temperature Edge | `%Temperature Edge%` or `%temperature_edge%` | `device_temp_edge` |
| MM Busy | `%MM Busy%` or `%mm_activity%` | `device_busy_mm` |
| VCN Activity (device-level) | `%VCN Activity%` | `device_vcn_activity` |
| JPEG Activity (device-level) | `%JPEG Activity%` | `device_jpeg_activity` |
| XGMI | `%XGMI%` | `device_xgmi%` |
| Voltage | `%Voltage%` | `device_voltage%` |
| Fan | `%Fan%` | `device_fan%` |

#### Navi 48 Should NOT Have

| Absent Metric | Perfetto Pattern | RocPD Pattern |
|---------------|-----------------|---------------|
| HBM Temperature | `%HBM Temp%` | `device_temp_hbm%` |
| VCN Busy (per-XCP) | `%VCN Busy%` | N/A |
| JPEG Busy (per-XCP) | `%JPEG Busy%` | N/A |
| JPEG Activity | `%JPEG Activity%` | `device_jpeg_activity%` |
| XGMI | `%XGMI%` | `device_xgmi%` |
| NIC | `%NIC%` | `nic_%` |

#### Perfetto Negative Check SQL

```sql
-- MI300X: Verify absent metrics
SELECT t.name FROM counter_track t
WHERE t.name LIKE '%(S)%'
  AND (t.name LIKE '%Temperature Edge%'
    OR t.name LIKE '%MM Busy%'
    OR t.name LIKE '%VCN Activity%'
    OR t.name LIKE '%JPEG Activity%'
    OR t.name LIKE '%XGMI%'
    OR t.name LIKE '%Voltage%'
    OR t.name LIKE '%Fan%');
-- Expected: 0 rows

-- Navi 48: Verify absent metrics
SELECT t.name FROM counter_track t
WHERE t.name LIKE '%(S)%'
  AND (t.name LIKE '%HBM Temp%'
    OR t.name LIKE '%VCN Busy%'
    OR t.name LIKE '%JPEG Busy%'
    OR t.name LIKE '%JPEG Activity%'
    OR t.name LIKE '%XGMI%'
    OR t.name LIKE '%NIC%');
-- Expected: 0 rows
```

#### RocPD Negative Check

```bash
# MI300X
sqlite3 <db-file> "
SELECT DISTINCT p.name FROM rocpd_info_pmc p
WHERE p.name IN ('device_busy_mm', 'device_temp_edge')
   OR p.name LIKE 'device_vcn_activity%'
   OR p.name LIKE 'device_jpeg_activity%'
   OR p.name LIKE 'device_xgmi%'
   OR p.name LIKE 'device_voltage%'
   OR p.name LIKE 'device_fan%';
"
# Expected: 0 rows

# Navi 48
sqlite3 <db-file> "
SELECT DISTINCT p.name FROM rocpd_info_pmc p
WHERE p.name LIKE 'device_temp_hbm%'
   OR p.name LIKE 'device_jpeg_activity%'
   OR p.name LIKE 'device_xgmi%'
   OR p.name LIKE 'nic_%';
"
# Expected: 0 rows
```

### Phase 6: Cross-Format Consistency

For each architecture, verify that the same set of metrics appears across all 3 formats (accounting for naming differences):

```sql
-- Compare metric counts between Standard and Legacy Perfetto
-- Both should have the same number of unique PMC track names
SELECT COUNT(DISTINCT t.name) FROM counter_track t WHERE t.name LIKE '%(S)%';
```

For RocPD, compare the set of distinct `rocpd_info_pmc.name` values against Perfetto track names.

Discrepancies between formats indicate a bug in one of the output processors.

### Phase 7: Cleanup

```bash
rm -rf /tmp/pmc-validate-mi300-perfetto /tmp/pmc-validate-mi300-legacy /tmp/pmc-validate-mi300-rocpd
rm -rf /tmp/pmc-validate-navi-perfetto /tmp/pmc-validate-navi-legacy /tmp/pmc-validate-navi-rocpd
```

## Report Format

```markdown
# PMC Validation Report (Mock-Based)

**Date**: YYYY-MM-DD
**Build**: <build_dir>
**Branch**: <branch>

## Sentinel Check Results

| Config | Format | Sentinel Values Found | Status |
|--------|--------|--------------------|--------|
| MI300X | Perfetto | 0 | PASS |
| MI300X | Legacy | 0 | PASS |
| MI300X | RocPD | 0 | PASS |
| Navi 48 | Perfetto | 0 | PASS |
| Navi 48 | Legacy | 0 | PASS |
| Navi 48 | RocPD | 0 | PASS |

## Positive Validation (Configured Metrics)

| Config | Metric | Perfetto | Legacy | RocPD | Range OK |
|--------|--------|----------|--------|-------|----------|
| MI300X | Power | PASS (N, [300-500]) | PASS | PASS | YES |
| MI300X | Temperature | PASS (N, [55-75]) | PASS | PASS | YES |
| ... | ... | ... | ... | ... | ... |
| Navi 48 | Power | PASS (N, [20-30]) | PASS | PASS | YES |
| ... | ... | ... | ... | ... | ... |

## Negative Validation (Unsupported Metrics)

| Config | Metric Should Be Absent | Perfetto | Legacy | RocPD |
|--------|------------------------|----------|--------|-------|
| MI300X | temperature_edge | PASS (absent) | PASS | PASS |
| MI300X | MM Busy | PASS (absent) | PASS | PASS |
| MI300X | XGMI | PASS (absent) | PASS | PASS |
| Navi 48 | HBM Temperature | PASS (absent) | PASS | PASS |
| Navi 48 | JPEG Activity | PASS (absent) | PASS | PASS |
| Navi 48 | NIC | PASS (absent) | PASS | PASS |
| ... | ... | ... | ... | ... |

## Cross-Format Consistency

| Config | Perfetto Metrics | Legacy Metrics | RocPD Metrics | Match |
|--------|-----------------|----------------|---------------|-------|
| MI300X | N | N | N | YES |
| Navi 48 | N | N | N | YES |

## Issues Found
[List with severity: CRITICAL / HIGH / MEDIUM / LOW]

## Conclusion
[Overall assessment]
```

Save report to: `planning/pmc-validation-report.md` in the project worktree.

## Common Issues & Known Limitations

| Issue | Description | Impact |
|-------|-------------|--------|
| Perfetto double precision | UINT64_MAX stored as `1.8446744073709552e+19` | Must check `>= 1.844e+19` in addition to exact values |
| Legacy timing | Short workloads (<0.5s) may get 0-1 samples in Legacy format | Use `transpose` which runs ~2.4s |
| SDMA cumulative | SDMA values are cumulative byte counters, not instantaneous rates | Delta calculation needed for rate validation |
| Mock workload independence | Mock generates values regardless of workload type | VCN/JPEG don't need decode binaries |
| yaml-cpp dependency | Mock requires yaml-cpp linked into the build | Check with `ldd` before running |
| Invalid timestamps (Legacy) | First sample may have invalid timestamp, dropped with warning | Reduces sample count by 1-2 |

## Integration

| Outcome | Next Step |
|---------|-----------|
| Sentinel found | `planning-bugfix` — plan fix for the leaking pipeline stage |
| Missing configured metric | `planning-bugfix` — investigate why metric isn't reaching output |
| Unsupported metric present | `planning-bugfix` — sentinel filtering gap |
| All checks pass | `git-prepare-pull-request` to submit |

This skill is also agent-level knowledge for the orchestrator's Tester agent.
