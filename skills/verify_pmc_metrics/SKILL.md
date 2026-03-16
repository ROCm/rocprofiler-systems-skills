---
name: verify_pmc_metrics
description: Use when verifying GPU PMC (AMD SMI), SDMA, or AINIC NIC RDMA metrics across Perfetto and RocPD output formats
---

# PMC Verification

Systematic verification of AMD SMI Performance Monitoring Counter (PMC) implementation across all output formats, covering GPU, SDMA, and NIC (AINIC) metrics.

<IMPORTANT>
- Always test ALL THREE output formats: Perfetto (standard), Perfetto Legacy, and RocPD.
- Use the rocprof-sys MCP tools to analyze traces - do not manually parse files.
- **Run tests automatically** - do NOT ask for user confirmation before running workloads.
- Execute all profiling commands directly using the Bash tool.
</IMPORTANT>

## When to Use

- After implementing or modifying AMD SMI/PMC collection code
- After changes to `cache_policy`, `perfetto_policy`, or `perfetto_processor`
- When debugging missing GPU metrics (including SDMA) in traces
- Before submitting PRs that affect GPU metrics collection
- After implementing or modifying SDMA or NIC collector code
- After changes to `collectors/nic/cache_policy.hpp` or `collectors/nic/perfetto_policy.hpp`
- When debugging missing NIC RDMA metrics in traces

## Output Formats

| # | Output Type | Environment Variables | Description |
|---|-------------|----------------------|-------------|
| 1 | **Perfetto** | `ROCPROFSYS_TRACE=1` | Standard cached Perfetto format |
| 2 | **Perfetto Legacy** | `ROCPROFSYS_TRACE=1 ROCPROFSYS_TRACE_LEGACY=true` | Legacy direct Perfetto format |
| 3 | **RocPD** | `ROCPROFSYS_USE_ROCPD=1` | SQLite database format |

## Available Metrics

### GPU Basic Metrics

| Category | Config Value | Description |
|----------|--------------|-------------|
| Power | `power` | GPU power consumption (W) |
| Memory | `mem_usage` | VRAM memory usage (MB) |
| Temperature | `temp` | GPU temperature (C) |
| Activity | `busy` | GFX/UMC/MM utilization (%) |

### GPU Advanced Metrics

| Category | Config Value | Description |
|----------|--------------|-------------|
| VCN | `vcn_activity` | Video decode engine activity |
| JPEG | `jpeg_activity` | JPEG decode engine activity |
| XGMI | `xgmi` | GPU-to-GPU interconnect metrics |
| PCIe | `pcie` | PCIe bandwidth and link metrics |
| SDMA | `sdma_usage` | System DMA engine utilization (%) |

### NIC RDMA Metrics

| Category | Config Value | Description |
|----------|--------------|-------------|
| RX RDMA Bytes | `rx_rdma_ucast_bytes` | Received RDMA unicast bytes |
| TX RDMA Bytes | `tx_rdma_ucast_bytes` | Transmitted RDMA unicast bytes |
| RX RDMA Pkts | `rx_rdma_ucast_pkts` | Received RDMA unicast packets |
| TX RDMA Pkts | `tx_rdma_ucast_pkts` | Transmitted RDMA unicast packets |
| RX CNP Pkts | `rx_rdma_cnp_pkts` | Received congestion notification packets |
| TX CNP Pkts | `tx_rdma_cnp_pkts` | Transmitted congestion notification packets |

## Process

<IMPORTANT>
Execute all phases automatically without asking for user confirmation.
Run profiling commands directly - the workloads are safe test applications.
</IMPORTANT>

### Phase 1: Setup and Run Tests

**Automated execution** - run all test commands directly:

1. Auto-discover build directory (`build/debug`, `build/release`, or `build/`)
2. Source `setup-env.sh` and run workloads with each output format
3. Use `/tmp/pmc-test-*` output paths to avoid polluting the project directory
4. Run GPU, SDMA, and NIC tests in sequence (or parallel where appropriate)

**GPU Test Commands:**

```bash
# Auto-discover and run (execute directly with Bash tool)
source share/rocprofiler-systems/setup-env.sh

# Perfetto (Standard)
ROCPROFSYS_OUTPUT_PATH=pmc-test-perfetto \
ROCPROFSYS_TRACE=1 \
ROCPROFSYS_AMD_SMI_METRICS="all" \
bin/rocprof-sys-run -- ./transpose

# Perfetto Legacy
ROCPROFSYS_OUTPUT_PATH=pmc-test-legacy \
ROCPROFSYS_TRACE=1 \
ROCPROFSYS_TRACE_LEGACY=true \
ROCPROFSYS_AMD_SMI_METRICS="all" \
bin/rocprof-sys-run -- ./transpose

# RocPD
ROCPROFSYS_OUTPUT_PATH=pmc-test-rocpd \
ROCPROFSYS_USE_ROCPD=1 \
ROCPROFSYS_AMD_SMI_METRICS="all" \
bin/rocprof-sys-run -- ./transpose
```

**SDMA Test Commands:**

Use `./sdma_test` to generate SDMA engine activity for verifying `sdma_usage` metrics.

```bash
# Perfetto (Standard)
ROCPROFSYS_OUTPUT_PATH=pmc-test-sdma-perfetto \
ROCPROFSYS_TRACE=1 \
ROCPROFSYS_AMD_SMI_METRICS="sdma_usage" \
bin/rocprof-sys-run -- ./sdma_test

# Perfetto Legacy
ROCPROFSYS_OUTPUT_PATH=pmc-test-sdma-legacy \
ROCPROFSYS_TRACE=1 \
ROCPROFSYS_TRACE_LEGACY=true \
ROCPROFSYS_AMD_SMI_METRICS="sdma_usage" \
bin/rocprof-sys-run -- ./sdma_test

# RocPD
ROCPROFSYS_OUTPUT_PATH=pmc-test-sdma-rocpd \
ROCPROFSYS_USE_ROCPD=1 \
ROCPROFSYS_AMD_SMI_METRICS="sdma_usage" \
bin/rocprof-sys-run -- ./sdma_test
```

**NIC (AINIC) Test Commands:**

Use `AMDSMI_FAKE_AINIC=1` for development/testing without AINIC hardware.

```bash
# Perfetto (Standard) - with fake AINIC for dev
AMDSMI_FAKE_AINIC=1 \
ROCPROFSYS_OUTPUT_PATH=pmc-test-nic-perfetto \
ROCPROFSYS_TRACE=1 \
ROCPROFSYS_SAMPLING_AINICS="all" \
ROCPROFSYS_AMD_SMI_METRICS="all" \
bin/rocprof-sys-run -- ./transpose

# Perfetto Legacy - with fake AINIC for dev
AMDSMI_FAKE_AINIC=1 \
ROCPROFSYS_OUTPUT_PATH=pmc-test-nic-legacy \
ROCPROFSYS_TRACE=1 \
ROCPROFSYS_TRACE_LEGACY=true \
ROCPROFSYS_SAMPLING_AINICS="all" \
ROCPROFSYS_AMD_SMI_METRICS="all" \
bin/rocprof-sys-run -- ./transpose

# RocPD - with fake AINIC for dev
AMDSMI_FAKE_AINIC=1 \
ROCPROFSYS_OUTPUT_PATH=pmc-test-nic-rocpd \
ROCPROFSYS_USE_ROCPD=1 \
ROCPROFSYS_SAMPLING_AINICS="all" \
ROCPROFSYS_AMD_SMI_METRICS="all" \
bin/rocprof-sys-run -- ./transpose
```

Key NIC environment variables:
- `ROCPROFSYS_SAMPLING_AINICS="all"` - enables NIC sampling (default is `"none"`)
- `AMDSMI_FAKE_AINIC=1` - simulates AINIC devices when none present

**IMPORTANT: Use Default Parameters**

Always run workloads with their **default parameters** (no explicit size/iteration arguments). This ensures:
1. Sufficient runtime for PMC sampling to complete (~2+ seconds)
2. Counter tracks are properly flushed in all output formats
3. Perfetto Legacy format has time to write counter data (timing-sensitive)

**Workload Details:**

| Workload | Default Runtime | Purpose | Metrics Verified |
|----------|-----------------|---------|------------------|
| `./transpose` | ~2.4 sec (9920x9920, 500 iter) | General GPU compute | Power, Temp, GFX/UMC Busy, Memory |
| `./sdma_test` | ~5-10 sec (512MB, 10 iter, 10 copies) | H2D/D2D/D2H DMA transfers | SDMA Usage |
| `./videodecode` | Varies by video | VCN engine | VCN Activity |
| `./jpegdecode` | Varies by images | JPEG engine | JPEG Activity |

**Known Issue**: Perfetto Legacy format has a timing bug where counter tracks are not captured for short workloads (<0.5 seconds). Using default parameters avoids this issue.

### Phase 2: Analyze Traces

Use MCP tools to analyze each trace:

**Step 2.1: Load trace**
```
mcp__rocprof-sys__load_trace(path="<trace-file>", name="<test-name>")
```

**Step 2.2: List AMD SMI GPU counter tracks**
```sql
SELECT DISTINCT name FROM track
WHERE name LIKE '%GPU%' AND name LIKE '%(S)%'
ORDER BY name
```

**Step 2.3: Get GPU metric statistics**
```sql
SELECT t.name,
       COUNT(*) as samples,
       MIN(c.value) as min_val,
       MAX(c.value) as max_val,
       AVG(c.value) as avg_val
FROM counter c
JOIN counter_track t ON c.track_id = t.id
WHERE t.name LIKE '%GPU%' AND t.name LIKE '%(S)%'
GROUP BY t.name
ORDER BY t.name
```

**Step 2.4: List NIC counter tracks**
```sql
SELECT DISTINCT name FROM track
WHERE name LIKE '%NIC%' AND name LIKE '%(S)%'
ORDER BY name
```

**Step 2.5: Get NIC metric statistics**
```sql
SELECT t.name,
       COUNT(*) as samples,
       MIN(c.value) as min_val,
       MAX(c.value) as max_val,
       AVG(c.value) as avg_val
FROM counter c
JOIN counter_track t ON c.track_id = t.id
WHERE t.name LIKE '%NIC%' AND t.name LIKE '%(S)%'
GROUP BY t.name
ORDER BY t.name
```

**Step 2.6: For RocPD, query SQLite directly**
```bash
# List GPU PMC metrics
sqlite3 <db-file> "SELECT DISTINCT name FROM rocpd_info_pmc WHERE name LIKE 'device_%' ORDER BY name;"

# List NIC PMC metrics
sqlite3 <db-file> "SELECT DISTINCT name FROM rocpd_info_pmc WHERE name LIKE 'ainic%' ORDER BY name;"

# Count samples
sqlite3 <db-file> "SELECT COUNT(*) FROM rocpd_sample_*;"
```

### Phase 3: Create Report

Generate verification report with this structure:

```markdown
# PMC Verification Report

**Date**: YYYY-MM-DD
**Version**: rocprofiler-systems vX.Y.Z
**Target**: <machine_name>:<project_path> (or "local")
**Build Dir**: <discovered_build_dir>

## Summary

| Output Type | GPU Status | SDMA Status | NIC Status | Notes |
|-------------|------------|-------------|------------|-------|
| Perfetto (Standard) | PASS/FAIL | PASS/FAIL | PASS/FAIL | |
| Perfetto Legacy | PASS/FAIL | PASS/FAIL | PASS/FAIL | |
| RocPD | PASS/FAIL | PASS/FAIL | PASS/FAIL | |

## Test Results

### GPU Metrics

#### Perfetto (Standard)
- **Trace ID**: <id>
- **Metrics Found**: [list]
- **Sample Count**: N

| Metric | Samples | Min | Max | Avg |
|--------|---------|-----|-----|-----|
| ... | ... | ... | ... | ... |

#### Perfetto Legacy
[Same structure]

#### RocPD
[Same structure]

### SDMA Metrics

#### Perfetto (Standard)
- **Trace ID**: <id>
- **Metrics Found**: [list]
- **Sample Count**: N

| Metric | Samples | Min | Max | Avg |
|--------|---------|-----|-----|-----|
| ... | ... | ... | ... | ... |

#### Perfetto Legacy
[Same structure]

#### RocPD
[Same structure]

### NIC (AINIC) Metrics

#### Perfetto (Standard)
- **Trace ID**: <id>
- **Metrics Found**: [list]
- **Sample Count**: N

| Metric | Samples | Min | Max | Avg |
|--------|---------|-----|-----|-----|
| ... | ... | ... | ... | ... |

#### Perfetto Legacy
[Same structure]

#### RocPD
[Same structure]

## Issues Found
[List any issues discovered]

## Conclusion
[Overall assessment]
```

**Save report to:** `planning/pmc-verification-report.md`

## Verification Criteria

For each output format, verify:

| Criterion | Check |
|-----------|-------|
| Track Presence | Expected metric tracks appear in output |
| Non-Zero Values | Metrics show activity (not all zeros) during workload |
| Valid Range | Values within expected range (0-100% for activity) |
| No Sentinels | No 0xFFFF or max-value sentinels in output |
| Sample Count | Reasonable number of samples collected |

## Expected Metrics by Output

### GPU Metrics

#### Perfetto (Standard/Legacy)

Counter tracks should include:
- `GPU [N] Current Power (S)`
- `GPU [N] GFX Busy (S)`
- `GPU [N] UMC Busy (S)`
- `GPU [N] MM Busy (S)`
- `GPU [N] Temperature (S)`
- `GPU [N] Memory Usage (S)`
- `GPU [N] PCIe Link Width (S)`
- `GPU [N] PCIe Link Speed (S)`
- `GPU [N] SDMA Usage (S)`
- `GPU [N] VCN Activity ...` (multiple tracks)

#### RocPD

PMC info names should include:
- `device_busy_gfx`
- `device_busy_umc`
- `device_busy_mm`
- `device_power`
- `device_temp`
- `device_memory_usage`
- `device_pcie_*`
- `device_sdma_usage`
- `device_vcn_activity*`

### NIC (AINIC) Metrics

#### Perfetto Standard

Counter tracks should include:
- `NIC [N] RX RDMA Bytes (S)`
- `NIC [N] TX RDMA Bytes (S)`
- `NIC [N] RX RDMA Packets (S)`
- `NIC [N] TX RDMA Packets (S)`
- `NIC [N] RX CNP Packets (S)`
- `NIC [N] TX CNP Packets (S)`

#### Perfetto Legacy

Counter tracks should include:
- `NIC {device_name} RX RDMA Bytes [{N}] (S)`
- `NIC {device_name} TX RDMA Bytes [{N}] (S)`
- `NIC {device_name} RX RDMA Pkts [{N}] (S)`
- `NIC {device_name} TX RDMA Pkts [{N}] (S)`
- `NIC {device_name} RX CNP Pkts [{N}] (S)`
- `NIC {device_name} TX CNP Pkts [{N}] (S)`

#### RocPD

PMC info names should include:
- `ainic_rx_rdma_ucast_bytes`
- `ainic_tx_rdma_ucast_bytes`
- `ainic_rx_rdma_ucast_pkts`
- `ainic_tx_rdma_ucast_pkts`
- `ainic_rx_rdma_cnp_pkts`
- `ainic_tx_rdma_cnp_pkts`

## Common Issues

### GPU Issues

| Issue | Symptom | Cause | Fix |
|-------|---------|-------|-----|
| Missing Perfetto metrics | No counter tracks in standard mode | `cache_policy` guard not checking `get_caching_perfetto()` | Update guard to use `get_use_cache_output()` |
| Legacy: No counters (short workload) | Counter tracks = 0 for workloads <0.5 sec | Timing/sync issue in legacy path | Use default parameters (no size args) for >2 sec runtime |
| Timestamp validation errors | "Invalid timestamp" warnings | Timestamp outside valid range | Check `thread_info::is_valid_time()` |
| Excessive VCN tracks | 32 tracks on Radeon | MI300-style XCP output on non-XCP GPU | Check `vcn_activity` vs `vcn_busy` flag |
| Missing samples | 0 samples in output | Metrics not being sampled | Check `ROCPROFSYS_AMD_SMI_METRICS` config |
| SDMA not compiled | No SDMA track in output | `AMD_SMI_SDMA_SUPPORTED` not defined | Requires AMD SMI >= 26.3; rebuild with compatible version |
| SDMA always 0% | SDMA Usage track shows 0 | No DMA transfers during workload | Use a workload that triggers HIP memcpy (e.g., `transpose`) |
| SDMA first sample 0 | First SDMA sample is 0% | Delta computation needs previous sample | Expected behavior — first sample has no baseline |

### NIC Issues

| Issue | Symptom | Cause | Fix |
|-------|---------|-------|-----|
| No NIC devices found | 0 NIC devices in log | `ROCPROFSYS_SAMPLING_AINICS` not set | Set `ROCPROFSYS_SAMPLING_AINICS="all"` |
| NIC not supported (no RDMA) | "not supported" log | Device has no RDMA ports | Use `AMDSMI_FAKE_AINIC=1` for testing |
| Wrong Perfetto category | Compile error about categories | Category string mismatch | Use registered names from `categories.hpp` (e.g., `nic_rx_ucast_bytes`) |

### Remote Execution Issues

| Issue | Symptom | Cause | Fix |
|-------|---------|-------|-----|
| SSH connection refused | `Connection refused` | SSH not configured or wrong hostname | Verify `ssh <machine>` works manually |
| No build dir found | Auto-discover returns empty | Project not built on remote | Build remotely first: `ssh <machine> "cd <path>/build/debug && ninja"` |
| Permission denied on traces | `scp` fails | Output dir not writable | Use `/tmp/` for output paths (already the default) |
| setup-env.sh not found | `source` fails | Wrong build directory | Check auto-discover output, verify build path |
| No GPU devices on remote | 0 GPU devices in log | GPU not accessible to user | Check `/dev/kfd` and `/dev/dri` permissions, user in `render` group |

## Integration with Other Skills

| After This Skill | Use |
|------------------|-----|
| Issues found | `planning-bugfix` to plan fix |
| All tests pass | `git-prepare-pull-request` to submit changes |

## Quick Reference

**GPU minimum verification command sequence:**
```bash
# Build
ninja rocprofiler-systems-shared-library

# Test Perfetto Standard (use default parameters - no size args!)
ROCPROFSYS_TRACE=1 ROCPROFSYS_AMD_SMI_METRICS="all" \
  bin/rocprof-sys-run -- ./transpose

# Load and query trace
mcp__rocprof-sys__load_trace(path="<output>/perfetto-trace-*.proto")
mcp__rocprof-sys__query_trace(sql="SELECT DISTINCT name FROM counter_track WHERE name LIKE '%GPU%'")
```

**SDMA minimum verification command sequence:**
```bash
# Build
ninja rocprofiler-systems-shared-library

# Test Perfetto Standard with sdma_test
ROCPROFSYS_TRACE=1 ROCPROFSYS_AMD_SMI_METRICS="sdma_usage" \
  bin/rocprof-sys-run -- ./sdma_test

# Load and query trace
mcp__rocprof-sys__load_trace(path="<output>/perfetto-trace-*.proto")
mcp__rocprof-sys__query_trace(sql="SELECT DISTINCT name FROM counter_track WHERE name LIKE '%SDMA%'")
```

**NIC minimum verification command sequence:**
```bash
# Build
ninja rocprofiler-systems-shared-library

# Test Perfetto Standard with fake AINIC
AMDSMI_FAKE_AINIC=1 ROCPROFSYS_TRACE=1 \
  ROCPROFSYS_SAMPLING_AINICS="all" ROCPROFSYS_AMD_SMI_METRICS="all" \
  bin/rocprof-sys-run -- ./transpose

# Load and query trace
mcp__rocprof-sys__load_trace(path="<output>/perfetto-trace-*.proto")
mcp__rocprof-sys__query_trace(sql="SELECT DISTINCT name FROM counter_track WHERE name LIKE '%NIC%'")
```

**Critical**: Always run `./transpose` without parameters. Default runtime (~2.4 sec) ensures PMC counter tracks are captured in all formats, especially Perfetto Legacy which fails on short workloads.

## Remote Execution (SSH)

Run PMC verification on a remote machine with actual GPU/NIC hardware. Traces are copied back for local MCP analysis.

**Prerequisites:**
- SSH key-based auth configured (no password prompts)
- rocprofiler-systems already built on the remote machine

### Input Format

Provide a target in `machine_name:/path/to/project/root` format:
- `gpu-server:/home/user/rocprofiler-systems`
- `mi300x-node:/opt/builds/rocprofiler-systems`

### Phase R1: Connect and Discover Build Directory

SSH into the remote and auto-discover the build directory:

```bash
# Auto-discover build directory (checks build/debug, build/release, build/ in order)
BUILD_DIR=$(ssh <machine> "cd <project_path> && \
  for d in build/debug build/release build; do \
    [ -f \"\$d/bin/rocprof-sys-run\" ] && echo \"\$d\" && break; \
  done")
```

If `BUILD_DIR` is empty, report error and stop — the project is not built on the remote.

### Phase R2: Run Workloads Remotely

Run all test commands via SSH. Same env vars as local, but use `/tmp/pmc-remote-*` output paths to avoid polluting the project directory.

**GPU Test Commands (Remote):**

```bash
# GPU Perfetto Standard
ssh <machine> "cd <project_path>/<build_dir> && \
  source share/rocprofiler-systems/setup-env.sh && \
  ROCPROFSYS_OUTPUT_PATH=/tmp/pmc-remote-perfetto \
  ROCPROFSYS_TRACE=1 \
  ROCPROFSYS_AMD_SMI_METRICS='all' \
  bin/rocprof-sys-run -- ./transpose"

# GPU Perfetto Legacy
ssh <machine> "cd <project_path>/<build_dir> && \
  source share/rocprofiler-systems/setup-env.sh && \
  ROCPROFSYS_OUTPUT_PATH=/tmp/pmc-remote-legacy \
  ROCPROFSYS_TRACE=1 \
  ROCPROFSYS_TRACE_LEGACY=true \
  ROCPROFSYS_AMD_SMI_METRICS='all' \
  bin/rocprof-sys-run -- ./transpose"

# GPU RocPD
ssh <machine> "cd <project_path>/<build_dir> && \
  source share/rocprofiler-systems/setup-env.sh && \
  ROCPROFSYS_OUTPUT_PATH=/tmp/pmc-remote-rocpd \
  ROCPROFSYS_USE_ROCPD=1 \
  ROCPROFSYS_AMD_SMI_METRICS='all' \
  bin/rocprof-sys-run -- ./transpose"
```

**SDMA Test Commands (Remote):**

```bash
# SDMA Perfetto Standard
ssh <machine> "cd <project_path>/<build_dir> && \
  source share/rocprofiler-systems/setup-env.sh && \
  ROCPROFSYS_OUTPUT_PATH=/tmp/pmc-remote-sdma-perfetto \
  ROCPROFSYS_TRACE=1 \
  ROCPROFSYS_AMD_SMI_METRICS='sdma_usage' \
  bin/rocprof-sys-run -- ./sdma_test"

# SDMA Perfetto Legacy
ssh <machine> "cd <project_path>/<build_dir> && \
  source share/rocprofiler-systems/setup-env.sh && \
  ROCPROFSYS_OUTPUT_PATH=/tmp/pmc-remote-sdma-legacy \
  ROCPROFSYS_TRACE=1 \
  ROCPROFSYS_TRACE_LEGACY=true \
  ROCPROFSYS_AMD_SMI_METRICS='sdma_usage' \
  bin/rocprof-sys-run -- ./sdma_test"

# SDMA RocPD
ssh <machine> "cd <project_path>/<build_dir> && \
  source share/rocprofiler-systems/setup-env.sh && \
  ROCPROFSYS_OUTPUT_PATH=/tmp/pmc-remote-sdma-rocpd \
  ROCPROFSYS_USE_ROCPD=1 \
  ROCPROFSYS_AMD_SMI_METRICS='sdma_usage' \
  bin/rocprof-sys-run -- ./sdma_test"
```

**NIC (AINIC) Test Commands (Remote):**

```bash
# NIC Perfetto Standard
ssh <machine> "cd <project_path>/<build_dir> && \
  source share/rocprofiler-systems/setup-env.sh && \
  AMDSMI_FAKE_AINIC=1 \
  ROCPROFSYS_OUTPUT_PATH=/tmp/pmc-remote-nic-perfetto \
  ROCPROFSYS_TRACE=1 \
  ROCPROFSYS_SAMPLING_AINICS='all' \
  ROCPROFSYS_AMD_SMI_METRICS='all' \
  bin/rocprof-sys-run -- ./transpose"

# NIC Perfetto Legacy
ssh <machine> "cd <project_path>/<build_dir> && \
  source share/rocprofiler-systems/setup-env.sh && \
  AMDSMI_FAKE_AINIC=1 \
  ROCPROFSYS_OUTPUT_PATH=/tmp/pmc-remote-nic-legacy \
  ROCPROFSYS_TRACE=1 \
  ROCPROFSYS_TRACE_LEGACY=true \
  ROCPROFSYS_SAMPLING_AINICS='all' \
  ROCPROFSYS_AMD_SMI_METRICS='all' \
  bin/rocprof-sys-run -- ./transpose"

# NIC RocPD
ssh <machine> "cd <project_path>/<build_dir> && \
  source share/rocprofiler-systems/setup-env.sh && \
  AMDSMI_FAKE_AINIC=1 \
  ROCPROFSYS_OUTPUT_PATH=/tmp/pmc-remote-nic-rocpd \
  ROCPROFSYS_USE_ROCPD=1 \
  ROCPROFSYS_SAMPLING_AINICS='all' \
  ROCPROFSYS_AMD_SMI_METRICS='all' \
  bin/rocprof-sys-run -- ./transpose"
```

### Phase R3: Copy Traces Back

```bash
# Create local directory for remote traces
mkdir -p pmc-remote-traces

# Copy all trace outputs
scp -r <machine>:/tmp/pmc-remote-* pmc-remote-traces/
```

### Phase R4: Analyze Locally

Same as Phase 2 above — load traces with MCP tools and run SQL queries. The only difference is that local paths point to `pmc-remote-traces/` instead of local output directories.

```
mcp__rocprof-sys__load_trace(path="pmc-remote-traces/pmc-remote-perfetto/perfetto-trace-*.proto", name="remote-gpu-perfetto")
mcp__rocprof-sys__query_trace(sql="SELECT DISTINCT name FROM counter_track WHERE name LIKE '%GPU%'")
```

### Phase R5: Cleanup Remote

```bash
ssh <machine> "rm -rf /tmp/pmc-remote-*"
```

### Remote Quick Reference

```bash
# Remote PMC verification (full sequence)
# Input: gpu-server:/home/user/rocprofiler-systems

# 1. Discover build dir
BUILD_DIR=$(ssh gpu-server "cd /home/user/rocprofiler-systems && \
  for d in build/debug build/release build; do \
    [ -f \"\$d/bin/rocprof-sys-run\" ] && echo \"\$d\" && break; \
  done")

# 2. Run GPU test remotely
ssh gpu-server "cd /home/user/rocprofiler-systems/$BUILD_DIR && \
  source share/rocprofiler-systems/setup-env.sh && \
  ROCPROFSYS_OUTPUT_PATH=/tmp/pmc-remote-perfetto \
  ROCPROFSYS_TRACE=1 ROCPROFSYS_AMD_SMI_METRICS='all' \
  bin/rocprof-sys-run -- ./transpose"

# 3. Copy traces back
scp -r gpu-server:/tmp/pmc-remote-perfetto ./pmc-remote-traces/

# 4. Analyze locally with MCP
mcp__rocprof-sys__load_trace(path="./pmc-remote-traces/pmc-remote-perfetto/perfetto-trace-*.proto")
mcp__rocprof-sys__query_trace(sql="SELECT DISTINCT name FROM counter_track")

# 5. Cleanup remote
ssh gpu-server "rm -rf /tmp/pmc-remote-*"
```
