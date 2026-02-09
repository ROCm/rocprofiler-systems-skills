---
name: testing-gpu-pmc-verify
description: Use when verifying GPU PMC (AMD SMI) metrics across Perfetto and RocPD output formats
---

# GPU PMC Verification

Systematic verification of AMD SMI Performance Monitoring Counter (PMC) implementation across all output formats.

<IMPORTANT>
Always test ALL THREE output formats: Perfetto (standard), Perfetto Legacy, and RocPD.
Use the rocprof-sys MCP tools to analyze traces - do not manually parse files.
</IMPORTANT>

## When to Use

- After implementing or modifying AMD SMI/PMC collection code
- After changes to `cache_policy`, `perfetto_policy`, or `perfetto_processor`
- When debugging missing GPU metrics in traces
- Before submitting PRs that affect GPU metrics collection

## Output Formats

| # | Output Type | Environment Variables | Description |
|---|-------------|----------------------|-------------|
| 1 | **Perfetto** | `ROCPROFSYS_TRACE=1` | Standard cached Perfetto format |
| 2 | **Perfetto Legacy** | `ROCPROFSYS_TRACE=1 ROCPROFSYS_TRACE_LEGACY=true` | Legacy direct Perfetto format |
| 3 | **RocPD** | `ROCPROFSYS_USE_ROCPD=1` | SQLite database format |

## Available Metrics

### Basic Metrics

| Category | Config Value | Description |
|----------|--------------|-------------|
| Power | `power` | GPU power consumption (W) |
| Memory | `mem_usage` | VRAM memory usage (MB) |
| Temperature | `temp` | GPU temperature (C) |
| Activity | `busy` | GFX/UMC/MM utilization (%) |

### Advanced Metrics

| Category | Config Value | Description |
|----------|--------------|-------------|
| VCN | `vcn_activity` | Video decode engine activity |
| JPEG | `jpeg_activity` | JPEG decode engine activity |
| XGMI | `xgmi` | GPU-to-GPU interconnect metrics |
| PCIe | `pcie` | PCIe bandwidth and link metrics |

## Process

### Phase 1: Setup and Run Tests

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. Build rocprofiler-systems                                    │
│ 2. Source setup-env.sh                                          │
│ 3. Run workload with each output format                         │
│ 4. Verify output files exist                                    │
└─────────────────────────────────────────────────────────────────┘
```

**Test Commands:**

```bash
# Setup
cd build/debug
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

**IMPORTANT: Use Default Parameters**

Always run workloads with their **default parameters** (no explicit size/iteration arguments). This ensures:
1. Sufficient runtime for PMC sampling to complete (~2+ seconds)
2. Counter tracks are properly flushed in all output formats
3. Perfetto Legacy format has time to write counter data (timing-sensitive)

**Workload Details:**

| Workload | Default Runtime | Purpose | Metrics Verified |
|----------|-----------------|---------|------------------|
| `./transpose` | ~2.4 sec (9920x9920, 500 iter) | General GPU compute | Power, Temp, GFX/UMC Busy, Memory |
| `./videodecode` | Varies by video | VCN engine | VCN Activity |
| `./jpegdecode` | Varies by images | JPEG engine | JPEG Activity |

**Known Issue**: Perfetto Legacy format has a timing bug where counter tracks are not captured for short workloads (<0.5 seconds). Using default parameters avoids this issue.

### Phase 2: Analyze Traces

Use MCP tools to analyze each trace:

**Step 2.1: Load trace**
```
mcp__rocprof-sys__load_trace(path="<trace-file>", name="<test-name>")
```

**Step 2.2: List AMD SMI counter tracks**
```sql
SELECT DISTINCT name FROM track
WHERE name LIKE '%GPU%' AND name LIKE '%(S)%'
ORDER BY name
```

**Step 2.3: Get metric statistics**
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

**Step 2.4: For RocPD, query SQLite directly**
```bash
# List PMC metrics
sqlite3 <db-file> "SELECT DISTINCT name FROM rocpd_info_pmc_* ORDER BY name;"

# Count samples
sqlite3 <db-file> "SELECT COUNT(*) FROM rocpd_sample_*;"
```

### Phase 3: Create Report

Generate verification report with this structure:

```markdown
# PMC Verification Report

**Date**: YYYY-MM-DD
**Version**: rocprofiler-systems vX.Y.Z

## Summary

| Output Type | Status | Notes |
|-------------|--------|-------|
| Perfetto (Standard) | PASS/FAIL | |
| Perfetto Legacy | PASS/FAIL | |
| RocPD | PASS/FAIL | |

## Test Results

### Perfetto (Standard)
- **Trace ID**: <id>
- **Metrics Found**: [list]
- **Sample Count**: N

| Metric | Samples | Min | Max | Avg |
|--------|---------|-----|-----|-----|
| ... | ... | ... | ... | ... |

### Perfetto Legacy
[Same structure]

### RocPD
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

### Perfetto (Standard/Legacy)

Counter tracks should include:
- `GPU [N] Current Power (S)`
- `GPU [N] GFX Busy (S)`
- `GPU [N] UMC Busy (S)`
- `GPU [N] MM Busy (S)`
- `GPU [N] Temperature (S)`
- `GPU [N] Memory Usage (S)`
- `GPU [N] PCIe Link Width (S)`
- `GPU [N] PCIe Link Speed (S)`
- `GPU [N] VCN Activity ...` (multiple tracks)

### RocPD

PMC info names should include:
- `device_busy_gfx`
- `device_busy_umc`
- `device_busy_mm`
- `device_power`
- `device_temp`
- `device_memory_usage`
- `device_pcie_*`
- `device_vcn_activity*`

## Common Issues

| Issue | Symptom | Cause | Fix |
|-------|---------|-------|-----|
| Missing Perfetto metrics | No counter tracks in standard mode | `cache_policy` guard not checking `get_caching_perfetto()` | Update guard to use `get_use_cache_output()` |
| Legacy: No counters (short workload) | Counter tracks = 0 for workloads <0.5 sec | Timing/sync issue in legacy path | Use default parameters (no size args) for >2 sec runtime |
| Timestamp validation errors | "Invalid timestamp" warnings | Timestamp outside valid range | Check `thread_info::is_valid_time()` |
| Excessive VCN tracks | 32 tracks on Radeon | MI300-style XCP output on non-XCP GPU | Check `vcn_activity` vs `vcn_busy` flag |
| Missing samples | 0 samples in output | Metrics not being sampled | Check `ROCPROFSYS_AMD_SMI_METRICS` config |

## Integration with Other Skills

| After This Skill | Use |
|------------------|-----|
| Issues found | `planning-bugfix` to plan fix |
| All tests pass | `git-prepare-pull-request` to submit changes |

## Quick Reference

**Minimum verification command sequence:**
```bash
# Build
ninja rocprofiler-systems-shared-library

# Test Perfetto Standard (use default parameters - no size args!)
ROCPROFSYS_TRACE=1 ROCPROFSYS_AMD_SMI_METRICS="all" \
  bin/rocprof-sys-run -- ./transpose

# Load and query trace
mcp__rocprof-sys__load_trace(path="<output>/perfetto-trace-*.proto")
mcp__rocprof-sys__query_trace(sql="SELECT DISTINCT name FROM counter_track")
```

**Critical**: Always run `./transpose` without parameters. Default runtime (~2.4 sec) ensures PMC counter tracks are captured in all formats, especially Perfetto Legacy which fails on short workloads.
