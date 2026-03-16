---
name: rocprofsys-build
description: Build, test, and install rocprofiler-systems after configuration
---

# Build ROCm Systems Profiler

Builds the rocprofiler-systems project after configuration, optionally runs tests and installs.

## When to Use

Use this skill when:
- Project is already configured (CMake cache exists)
- User wants to compile rocprofsys
- User wants to run tests
- User wants to install rocprofsys
- User asks "build rocprofsys" or "compile rocprofiler-systems"

## Prerequisites

**Before using this skill:**
- Project must be configured (use `rocprofsys-configure` first)
- Build directory must exist with CMakeCache.txt
- Build system (Ninja or Make) must be available

**Check if configured:**
```bash
# Look for CMakeCache.txt in build directory
if [ -f build/debug/CMakeCache.txt ]; then
    echo "Configured with debug preset"
elif [ -f build/release/CMakeCache.txt ]; then
    echo "Configured with release preset"
else
    echo "Not configured - run rocprofsys-configure first"
fi
```

## Process

### Phase 1: Verify Configuration

1. **Find project directory**
   - Same logic as `rocprofsys-configure`
   - Must be in `projects/rocprofiler-systems/`

2. **Find build directory**
   - Check for standard locations: `build/debug`, `build/release`, etc.
   - Or ask user which build directory to use

3. **Validate build is configured**
   - Check for `CMakeCache.txt`
   - Check for build system files (`build.ninja` or `Makefile`)
   - If missing → invoke `rocprofsys-configure` first

**Report to user:**
- Build directory found
- Build type (Debug, Release, etc.)
- Configuration details (enabled features)

### Phase 2: Determine Build Scope

Ask user what they want to build:

Use **AskUserQuestion**:

```markdown
header: "Build Scope"
question: "What do you want to build?"
options:
  - label: "Full build (Recommended)"
    description: "Build all targets"
  - label: "Specific target"
    description: "Build a specific library or executable"
  - label: "Build and test"
    description: "Build everything and run tests"
  - label: "Build and install"
    description: "Build, test, and install to prefix"
```

### Phase 3: Determine Parallelism

Building rocprofsys can be memory-intensive. Determine parallel job count:

**Strategy:**
1. Check available memory
2. Suggest job count based on memory/cores
3. Let user override

```bash
# Check system memory (GB)
TOTAL_MEM=$(free -g | awk '/^Mem:/{print $2}')

# Check CPU cores
TOTAL_CORES=$(nproc)

# Heuristic: ~4GB per parallel job for rocprofsys
SAFE_JOBS=$((TOTAL_MEM / 4))
MAX_JOBS=$((SAFE_JOBS > TOTAL_CORES ? TOTAL_CORES : SAFE_JOBS))

# Suggest to user
echo "Recommended: -j${MAX_JOBS}"
```

Use **AskUserQuestion**:

```markdown
header: "Parallel Jobs"
question: "How many parallel build jobs?"
options:
  - label: "Auto (Recommended: -j8)"
    description: "Based on system memory and cores"
  - label: "Conservative (-j4)"
    description: "Safer for systems with limited memory"
  - label: "Maximum (-j$(nproc))"
    description: "Use all CPU cores (may run out of memory)"
  - label: "Custom"
    description: "Specify job count manually"
```

### Phase 4: Build

**Build command:**

```bash
cmake --build <build-dir> -j <jobs> [--target <target>]
```

**Examples:**

```bash
# Full build with 8 jobs
cmake --build build/debug -j8

# Build specific target
cmake --build build/debug -j8 --target rocprof-sys-run

# Verbose output (for debugging build issues)
cmake --build build/debug -j8 --verbose

# Clean and rebuild
cmake --build build/debug -j8 --clean-first
```

**Show build progress:**
- Ninja shows progress by default: `[123/456] Building CXX object...`
- Make needs `-j` for parallel build

**Monitor for issues:**
- Compiler errors
- Linker errors
- Out of memory errors
- Missing dependencies

### Phase 5: Handle Build Errors (if any)

If build fails, diagnose and help user:

**Common build errors:**

| Error Type | Symptoms | Solution |
|------------|----------|----------|
| Out of memory | `c++: fatal error: Killed` | Reduce parallel jobs: `-j2` or `-j4` |
| Missing headers | `fatal error: xyz.h: No such file` | Missing dependency, reconfigure with `BUILD_<DEP>=ON` |
| Linker errors | `undefined reference to` | Dependency issue, rebuild dependencies |
| Template errors | Long C++ template errors | Usually code issue, read error carefully |
| External dependency failure | Error in `external/dyninst/` | Clean build, try again, or use system package |

**Steps to diagnose:**
1. Read error message (usually at end of output)
2. Identify which source file/target failed
3. Check if dependency issue or code issue
4. Suggest fix based on error type

**If build fails repeatedly:**
- Try clean rebuild: remove build directory, reconfigure
- Check system dependencies
- Verify compiler version (GCC 7+)
- Check disk space
- Reduce parallelism

### Phase 6: Run Tests (Optional)

If user selected "Build and test" or explicitly wants to run tests:

```bash
# Run all tests
cd <build-dir>
ctest --output-on-failure

# Run tests in parallel
ctest -j8 --output-on-failure

# Run specific test
ctest -R <test-name> --output-on-failure

# Verbose test output
ctest -V
```

**Monitor test results:**
- How many passed/failed
- Which tests failed
- Test output for failures

**Report to user:**
- Test summary (X/Y passed)
- Failed tests with output
- Next steps if tests fail

### Phase 7: Install (Optional)

If user selected "Build and install":

```bash
# Install to prefix (may need sudo)
cmake --install <build-dir>

# Install to custom prefix
cmake --install <build-dir> --prefix /custom/path

# Install specific component
cmake --install <build-dir> --component <component>
```

**Check install prefix:**
- Default: `/opt/rocprofiler-systems` (usually needs sudo)
- Can be changed during configure: `-DCMAKE_INSTALL_PREFIX=...`

**Verify installation:**
```bash
# Check installed binaries
ls <install-prefix>/bin/rocprof-sys-*

# Check installed libraries
ls <install-prefix>/lib/librocprof-sys*

# Check setup script
cat <install-prefix>/share/rocprofiler-systems/setup-env.sh
```

**Setup environment:**
```bash
# Option 1: Source setup script
source /opt/rocprofiler-systems/share/rocprofiler-systems/setup-env.sh

# Option 2: Manual
export PATH=/opt/rocprofiler-systems/bin:$PATH
export LD_LIBRARY_PATH=/opt/rocprofiler-systems/lib:$LD_LIBRARY_PATH
```

### Phase 8: Report Results

**On success:**
- Build completed successfully
- Build time
- Number of targets built
- Test results (if run)
- Install location (if installed)
- Next steps (how to use rocprofsys)

**On failure:**
- What failed (build/test/install)
- Error summary
- Suggested fixes
- Whether to retry

## Build Examples

### Example 1: Quick Build

```bash
cd /path/to/projects/rocprofiler-systems
cmake --build build/debug -j8
```

### Example 2: Build with Tests

```bash
cd /path/to/projects/rocprofiler-systems
cmake --build build/debug -j8
cd build/debug
ctest --output-on-failure
```

### Example 3: Build and Install

```bash
cd /path/to/projects/rocprofiler-systems
cmake --build build/release -j8
sudo cmake --install build/release
```

### Example 4: Incremental Build (after code changes)

```bash
cd /path/to/projects/rocprofiler-systems
cmake --build build/debug -j8
# Only rebuilds changed files
```

### Example 5: Clean Rebuild

```bash
cd /path/to/projects/rocprofiler-systems
cmake --build build/debug -j8 --clean-first
```

### Example 6: Build Specific Target

```bash
cd /path/to/projects/rocprofiler-systems
cmake --build build/debug -j8 --target rocprof-sys-run
```

## Output

This skill produces:

**Build artifacts:**
```
projects/rocprofiler-systems/
└── build/
    └── debug/                          # Or release, etc.
        ├── source/
        │   ├── bin/
        │   │   └── rocprof-sys-run/
        │   │       └── rocprof-sys-run    # Executable
        │   └── lib/
        │       └── rocprof-sys/
        │           └── librocprof-sys.so  # Library
        └── ...
```

**Test results:**
- CTest output
- Test logs in `build/debug/Testing/`

**Installation (if installed):**
```
/opt/rocprofiler-systems/
├── bin/
│   ├── rocprof-sys-run
│   ├── rocprof-sys-instrument
│   └── ...
├── lib/
│   ├── librocprof-sys.so
│   └── ...
├── include/
│   └── rocprofiler-systems/
└── share/
    └── rocprofiler-systems/
        └── setup-env.sh
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Building without configuring | Run `rocprofsys-configure` first |
| Too many parallel jobs | Reduce to `-j4` or `-j2` if out of memory |
| Building in wrong directory | Must be in project root, build dir is specified with `-B` or `--build` |
| Not running tests | Always run tests after build, especially for changes |
| Installing without sudo | Use `sudo cmake --install` if prefix is `/opt` |
| Not checking test results | Review failed tests before proceeding |
| Ignoring build warnings | Some warnings indicate real issues |

## Troubleshooting

### Issue: "make: *** No targets specified"

**Cause:** Not in configured build directory or wrong command

**Solution:**
```bash
# Use cmake --build, not make directly
cmake --build build/debug
```

### Issue: "c++: fatal error: Killed signal terminated program"

**Cause:** Out of memory

**Solution:**
```bash
# Reduce parallel jobs
cmake --build build/debug -j2

# Or add swap space
```

### Issue: "ninja: error: loading 'build.ninja': No such file"

**Cause:** Build directory not configured

**Solution:**
```bash
# Run configure first
cmake --preset debug
# Then build
cmake --build build/debug
```

### Issue: Tests failing

**Steps:**
1. Run single test with verbose output: `ctest -R <test-name> -V`
2. Check test log: `cat build/debug/Testing/Temporary/LastTest.log`
3. Run test binary directly: `./build/debug/tests/<test-binary>`
4. Check for missing runtime dependencies
5. Check test environment (GPU available, etc.)

### Issue: Install fails with permission denied

**Solution:**
```bash
# Use sudo for system paths
sudo cmake --install build/release

# Or configure with user prefix
cmake -B build/release -DCMAKE_INSTALL_PREFIX=$HOME/rocprofsys
cmake --install build/release  # No sudo needed
```

## Integration with Other Skills

| After Build | Use |
|-------------|-----|
| Build successful | Test the installation, run examples |
| Build failed | Review errors, reconfigure if needed |
| Tests failed | Debug failed tests, fix code |
| Ready to commit | `git-commit` to commit changes |
| Ready for PR | `git-prepare-pull-request` |

## Build Targets Reference

**Common targets:**
- `all` (default) - Build everything
- `rocprof-sys-run` - Main profiler executable
- `rocprof-sys-instrument` - Binary instrumentation tool
- `rocprof-sys-avail` - Available metrics tool
- `tests` - Build all tests (without running)

**To see all targets:**
```bash
cmake --build build/debug --target help
```

## Notes

- **Incremental builds:** CMake tracks dependencies, only rebuilds changed files
- **Build cache:** Object files cached in build directory for fast rebuilds
- **Parallel builds:** Ninja is faster than Make for parallel builds
- **Memory usage:** Building with all cores can use 20-30GB RAM
- **Build time:** Full build: 10-30 minutes (depends on parallelism, dependencies)
- **Incremental build:** Usually < 1 minute for small changes
- **Clean build:** Use when switching branches or changing major options
