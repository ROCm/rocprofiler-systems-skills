---
name: rocprofsys
description: ROCm Systems Profiler (rocprofiler-systems) project workflows - configure, build, test, and development
---

# ROCm Systems Profiler Workflows

Main entry point for working with the rocprofiler-systems project. Provides guidance on configuration, building, testing, and common development workflows.

## Project Overview

**rocprofiler-systems** (formerly Omnitrace) is a comprehensive profiling and tracing tool for parallel applications (C, C++, Fortran, HIP, OpenCL, Python) on CPU and GPU.

**Key characteristics:**
- C++17 codebase with CMake build system
- Part of the rocm-systems monorepo (`projects/rocprofiler-systems/`)
- Uses CMakePresets.json for standard configurations
- Complex dependencies: Dyninst, Perfetto, TBB, Boost, elfutils
- Supports dynamic instrumentation, sampling, tracing, causal profiling

### Output Formats

rocprofiler-systems supports **two main output types**:

| Output Type | Environment Variable | Description |
|-------------|---------------------|-------------|
| **Perfetto** | `ROCPROFSYS_TRACE=1` | Protobuf trace format (viewable in ui.perfetto.dev) |
| **RocPD** | `ROCPROFSYS_USE_ROCPD=1` | SQLite database format for offline analysis |

### Perfetto Output Modes

Perfetto format has **two implementations**:

| Mode | Environment Variables | Implementation | Status |
|------|----------------------|----------------|--------|
| **Standard (Cached)** | `ROCPROFSYS_TRACE=1` | New caching implementation via `cache_policy` | Current, recommended |
| **Legacy** | `ROCPROFSYS_TRACE=1` + `ROCPROFSYS_TRACE_LEGACY=true` | Old direct-write implementation via `perfetto_policy` | Legacy, has timing issues on short workloads |

**Key differences:**
- **Standard**: Uses trace caching, more robust, recommended for all use cases
- **Legacy**: Direct Perfetto write, has known timing bug where counter tracks aren't captured for workloads <0.5 seconds

## When to Use

Use this skill when:
- User asks about rocprofiler-systems or rocprof-sys
- User wants to configure, build, or work with the project
- User needs guidance on project structure or workflows
- User asks "how do I build rocprofsys?"

## Project Structure

```
rocm-systems/                          # Monorepo root
└── projects/
    └── rocprofiler-systems/           # Project root
        ├── CMakeLists.txt
        ├── CMakePresets.json          # Standard build configs
        ├── build/                     # Build directories
        │   ├── ci/                    # CI build
        │   ├── debug/                 # Debug build
        │   ├── release/               # Release build
        │   └── debug-optimized/       # RelWithDebInfo build
        ├── source/                    # Source code
        ├── external/                  # Third-party deps
        ├── examples/                  # Example programs
        ├── tests/                     # Test suite
        ├── scripts/
        │   └── build-release.sh       # Release build script
        └── docs/                      # Documentation
```

## Common Workflows

### 1. First-Time Setup

For new developers or clean environment:

```
1. Find project location (in monorepo)
2. Configure with a preset → use rocprofsys-configure
3. Build the project → use rocprofsys-build
4. Run tests
```

### 2. Development Build

For active development with debugging:

```
1. Configure with debug preset
2. Build incrementally
3. Run specific tests
```

### 3. Release Build

For packaging or performance testing:

```
1. Configure with release preset
2. Build with optimizations
3. Create packages
```

### 4. Clean Rebuild

When dependencies change or build is corrupted:

```
1. Remove build directory
2. Reconfigure from scratch
3. Full rebuild
```

## Available Skills

| Skill | Use For |
|-------|---------|
| `rocprofsys-configure` | Configure CMake build with presets and options |
| `rocprofsys-build` | Build, test, and install the project |

## Workflow Dispatcher

When user asks about rocprofsys, determine intent and route:

| User Request | Action |
|--------------|--------|
| "configure rocprofsys" | Invoke `rocprofsys-configure` |
| "build rocprofsys" | Check if configured, then invoke `rocprofsys-build` |
| "clean build rocprofsys" | Remove build dir, configure, then build |
| "debug build" | Configure with debug preset, then build |
| "release build" | Configure with release preset, then build |
| "run tests" | Build, then run ctest |
| "install rocprofsys" | Build, then install to prefix |

## Finding the Project

Since the project may be in different locations (worktrees, different branches), always find it dynamically:

**Common locations:**
- `/home/amd/worktree/rocm-systems/*/projects/rocprofiler-systems`
- `~/rocm-systems/projects/rocprofiler-systems`
- Current directory (if already in project)

**Detection strategy:**
1. Check if current directory is inside rocprofiler-systems
2. Search common worktree locations
3. Ask user for project path

## CMake Presets

The project uses CMakePresets.json with these standard configurations:

| Preset | Build Type | Use For | Testing | Install Prefix |
|--------|-----------|---------|---------|----------------|
| `ci` | Release | CI builds | ON | /opt/rocprofiler-systems |
| `debug` | Debug | Development | ON | /opt/rocprofiler-systems |
| `debug-optimized` | RelWithDebInfo | Debug with perf | ON | /opt/rocprofiler-systems |
| `release` | Release | Production | OFF | /opt/rocprofiler-systems |

## Key CMake Options

| Option | Default | Description |
|--------|---------|-------------|
| `ROCPROFSYS_BUILD_DYNINST` | OFF | Build Dyninst from source |
| `ROCPROFSYS_BUILD_TBB` | OFF | Build TBB from source |
| `ROCPROFSYS_BUILD_BOOST` | OFF | Build Boost from source |
| `ROCPROFSYS_BUILD_ELFUTILS` | OFF | Build elfutils from source |
| `ROCPROFSYS_BUILD_TESTING` | ON | Enable tests |
| `ROCPROFSYS_USE_PYTHON` | ON | Enable Python support |
| `ROCPROFSYS_USE_MPI` | OFF | Enable full MPI support |
| `ROCPROFSYS_USE_PAPI` | ON | Enable PAPI hardware counters |

## Common Environment Variables

### Runtime Variables

| Variable | Values | Description |
|----------|--------|-------------|
| `ROCPROFSYS_TRACE` | `0` or `1` | Enable Perfetto trace output |
| `ROCPROFSYS_TRACE_LEGACY` | `true` or `false` | Use legacy Perfetto implementation |
| `ROCPROFSYS_USE_ROCPD` | `0` or `1` | Enable RocPD SQLite output |
| `ROCPROFSYS_OUTPUT_PATH` | `<directory>` | Output directory for traces |
| `ROCPROFSYS_AMD_SMI_METRICS` | `all`, `power`, `temp`, etc. | GPU metrics to collect |
| `ROCPROFSYS_SAMPLING_AINICS` | `all`, `none` | Enable NIC/AINIC sampling |
| `AMDSMI_FAKE_AINIC` | `0` or `1` | Simulate AINIC devices for testing |

### Example Usage

```bash
# Standard Perfetto trace with GPU metrics
ROCPROFSYS_TRACE=1 \
ROCPROFSYS_AMD_SMI_METRICS="all" \
bin/rocprof-sys-run -- ./my-app

# Legacy Perfetto mode
ROCPROFSYS_TRACE=1 \
ROCPROFSYS_TRACE_LEGACY=true \
ROCPROFSYS_AMD_SMI_METRICS="all" \
bin/rocprof-sys-run -- ./my-app

# RocPD database output
ROCPROFSYS_USE_ROCPD=1 \
ROCPROFSYS_AMD_SMI_METRICS="all" \
bin/rocprof-sys-run -- ./my-app

# NIC/AINIC metrics with fake devices
AMDSMI_FAKE_AINIC=1 \
ROCPROFSYS_TRACE=1 \
ROCPROFSYS_SAMPLING_AINICS="all" \
bin/rocprof-sys-run -- ./my-app
```

## Common Issues

| Issue | Solution |
|-------|----------|
| "Cannot find Dyninst" | Configure with `-DROCPROFSYS_BUILD_DYNINST=ON` |
| "CMake version too old" | Install CMake 3.21+ via pip: `pip install cmake` |
| "Out of memory during build" | Reduce parallel jobs: `cmake --build build -j4` |
| "Tests failing" | Build with debug preset, run specific test |
| "Wrong project path" | Ensure in `projects/rocprofiler-systems/` subdirectory |
| "No counter tracks in Perfetto" | Ensure using standard mode (not legacy), check `ROCPROFSYS_AMD_SMI_METRICS` |
| "Legacy mode: missing counters" | Workload too short (<0.5s), use standard mode or longer workload |

## Integration with Other Skills

| After This Skill | Use |
|------------------|-----|
| Code changes made | `git-commit` to commit changes |
| Feature added | `planning-feature` to plan implementation |
| Bug found | `planning-bugfix` to plan fix |
| Ready to test | `testing-testplan` for test plan |
| Ready for PR | `git-prepare-pull-request` |
| Profiler crashes/errors | `debugging-rocprof-sys` to debug profiler issues |
| Verify PMC metrics | `verify_pmc_metrics` to validate GPU/SDMA/NIC output |
| AMD SMI API work | `library-amd-smi` for AMD SMI C++ API guidance |

## Process

1. **Determine user intent**
   - What does the user want to do with rocprofsys?
   - Configure? Build? Test? Install? Debug?

2. **Find project location**
   - Check current directory
   - Search common locations
   - Ask user if needed

3. **Route to appropriate skill**
   - Configuration needs → `rocprofsys-configure`
   - Build needs → `rocprofsys-build`
   - Both → configure first, then build

4. **Provide context**
   - Show current build status (if any)
   - Suggest next steps
   - Link to documentation if needed

## Example Interactions

**User:** "Build rocprofsys"
**Action:** Check if configured → if not, invoke `rocprofsys-configure` → then invoke `rocprofsys-build`

**User:** "Debug build of rocprofiler-systems"
**Action:** Invoke `rocprofsys-configure` with debug preset → invoke `rocprofsys-build`

**User:** "Clean and rebuild rocprofsys"
**Action:** Remove build directory → invoke `rocprofsys-configure` → invoke `rocprofsys-build`

**User:** "How do I configure rocprofsys?"
**Action:** Invoke `rocprofsys-configure` skill

## Output

This skill produces:
- Guidance on which sub-skill to use
- Project status information
- Next steps recommendations

No files are created by this dispatcher skill.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Trying to build without configuring | Always configure first |
| Using wrong project path (monorepo root vs project dir) | Navigate to `projects/rocprofiler-systems/` |
| Not specifying preset | Use a preset or set CMAKE_BUILD_TYPE |
| Assuming project is in fixed location | Always find dynamically with git worktrees |
