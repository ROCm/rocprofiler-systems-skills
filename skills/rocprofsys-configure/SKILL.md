---
name: rocprofsys-configure
description: Configure rocprofiler-systems build with CMake presets and custom options
---

# Configure ROCm Systems Profiler Build

Configures the rocprofiler-systems project using CMake with presets or custom options.

## When to Use

Use this skill when:
- User wants to configure rocprofsys build
- Setting up build for first time
- Switching between debug/release builds
- Changing CMake options (dependencies, features)
- User asks "how do I configure rocprofsys?"

## Before You Start

**Prerequisites:**
- CMake 3.21 or higher
- GCC 7+ compiler (or Clang if Dyninst is pre-installed)
- Ninja or Make build system

**Check prerequisites:**
```bash
cmake --version    # Should be >= 3.21
gcc --version      # Should be >= 7.0
ninja --version    # Optional but recommended
```

## Process

### Phase 1: Find Project Location

Since rocprofiler-systems is in a monorepo and may use git worktrees, find it dynamically.

**Strategy:**
1. Check if current directory is inside the project
2. Search common worktree locations
3. Ask user for location

```bash
# Check current directory
if [ -f "CMakeLists.txt" ] && grep -q "rocprofiler-systems" CMakeLists.txt; then
    PROJECT_DIR="."
# Search worktrees
elif [ -d "/home/amd/worktree/rocm-systems" ]; then
    PROJECT_DIR=$(find /home/amd/worktree/rocm-systems -type d -name "rocprofiler-systems" | grep "projects/rocprofiler-systems$" | head -1)
# Ask user
else
    # Use AskUserQuestion to get path
fi
```

**Validation:**
- Must be the `projects/rocprofiler-systems/` directory (not monorepo root)
- Must contain `CMakeLists.txt` and `CMakePresets.json`

### Phase 2: Choose Configuration Strategy

Ask user what type of build they want:

| Option | Preset | Use For |
|--------|--------|---------|
| Debug | `debug` | Development with debugging symbols |
| Release | `release` | Production, optimized build |
| Debug-Optimized | `debug-optimized` | Debug symbols + optimizations |
| CI | `ci` | CI/CD builds with all features |
| Custom | None | User specifies all options manually |

Use **AskUserQuestion** to present options:

```markdown
header: "Build Type"
question: "Which build configuration do you want?"
options:
  - label: "Debug (Recommended for development)"
    description: "Debug build with tests enabled"
  - label: "Release"
    description: "Optimized production build"
  - label: "Debug-Optimized"
    description: "Optimized with debug symbols"
  - label: "CI"
    description: "Full CI build configuration"
  - label: "Custom"
    description: "Specify options manually"
```

### Phase 3: Select Build Directory

**Options:**
1. **Use preset default** (recommended)
   - Debug → `build/debug`
   - Release → `build/release`
   - Debug-Optimized → `build/debug-optimized`
   - CI → `build/ci`

2. **Custom directory**
   - User specifies (e.g., `build/my-build`)

**Ask user if they want to change default:**
- If no, use preset default
- If yes, ask for custom path

### Phase 4: Configure Dependencies

The project has complex dependencies. Determine which to build from source:

**Key dependencies:**
- Dyninst (required for instrumentation)
- TBB (required by Dyninst)
- Boost (required by Dyninst)
- Elfutils (required by Dyninst)
- Libiberty (required by Dyninst)

**Strategy:**
1. Try system packages first (faster)
2. If missing, build from source

Use **AskUserQuestion**:

```markdown
header: "Dependencies"
question: "How should dependencies be handled?"
options:
  - label: "Auto-detect (Recommended)"
    description: "Use system packages if available, build from source if missing"
  - label: "Build all from source"
    description: "Build Dyninst and all dependencies from source (slower but reliable)"
  - label: "Use system packages only"
    description: "Fail if system packages are missing"
```

If "Build from source" selected, set:
```cmake
-DROCPROFSYS_BUILD_DYNINST=ON
-DROCPROFSYS_BUILD_TBB=ON
-DROCPROFSYS_BUILD_BOOST=ON
-DROCPROFSYS_BUILD_ELFUTILS=ON
-DROCPROFSYS_BUILD_LIBIBERTY=ON
```

### Phase 5: Optional Features

Ask about optional features:

| Feature | CMake Option | Default |
|---------|--------------|---------|
| Python support | `ROCPROFSYS_USE_PYTHON` | ON |
| MPI support | `ROCPROFSYS_USE_MPI` | OFF |
| PAPI hardware counters | `ROCPROFSYS_USE_PAPI` | ON |
| Testing | `ROCPROFSYS_BUILD_TESTING` | ON |

**Only ask if user selected "Custom" or explicitly wants to change features.**

### Phase 6: Run CMake Configure

**With preset:**
```bash
cd /path/to/projects/rocprofiler-systems
cmake --preset <preset-name>
```

**With custom options:**
```bash
cd /path/to/projects/rocprofiler-systems
cmake -B <build-dir> \
  -DCMAKE_BUILD_TYPE=<Debug|Release|RelWithDebInfo> \
  -DCMAKE_INSTALL_PREFIX=/opt/rocprofiler-systems \
  -DROCPROFSYS_BUILD_DYNINST=<ON|OFF> \
  -DROCPROFSYS_BUILD_TBB=<ON|OFF> \
  -DROCPROFSYS_BUILD_BOOST=<ON|OFF> \
  -DROCPROFSYS_USE_PYTHON=<ON|OFF> \
  -DROCPROFSYS_BUILD_TESTING=<ON|OFF> \
  -G Ninja
```

**Show configuration command to user before running.**

### Phase 7: Validate Configuration

After CMake runs, check for:

1. **Configuration success**
   - CMake should exit with code 0
   - Should see "Build files have been written to..."

2. **Expected features enabled**
   - Check CMake output for enabled features
   - Verify dependencies found or built

3. **Common warnings**
   - Missing optional dependencies (PAPI, MPI)
   - Version mismatches
   - Compiler warnings

**Report to user:**
- Configuration status (success/failure)
- Enabled features
- Any warnings or issues
- Build directory location
- Next step: use `rocprofsys-build` skill

## Configuration Examples

### Example 1: Quick Debug Build (Recommended for Development)

```bash
cd /path/to/projects/rocprofiler-systems
cmake --preset debug
```

### Example 2: Release Build with All Dependencies from Source

```bash
cd /path/to/projects/rocprofiler-systems
cmake --preset release \
  -DROCPROFSYS_BUILD_DYNINST=ON \
  -DROCPROFSYS_BUILD_TBB=ON \
  -DROCPROFSYS_BUILD_BOOST=ON \
  -DROCPROFSYS_BUILD_ELFUTILS=ON \
  -DROCPROFSYS_BUILD_LIBIBERTY=ON
```

### Example 3: Custom Configuration

```bash
cd /path/to/projects/rocprofiler-systems
cmake -B build/my-custom-build \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DCMAKE_INSTALL_PREFIX=$HOME/rocprofsys-install \
  -DROCPROFSYS_BUILD_DYNINST=ON \
  -DROCPROFSYS_BUILD_TBB=ON \
  -DROCPROFSYS_BUILD_BOOST=ON \
  -DROCPROFSYS_USE_PYTHON=ON \
  -DROCPROFSYS_USE_MPI=ON \
  -DROCPROFSYS_BUILD_TESTING=ON \
  -G Ninja
```

## Output

This skill produces:
- Configured build directory with CMake cache
- `build/<preset>/CMakeCache.txt`
- Build system files (Ninja or Makefiles)

**Typical output structure:**
```
projects/rocprofiler-systems/
└── build/
    └── debug/                    # Or release, debug-optimized, etc.
        ├── CMakeCache.txt
        ├── CMakeFiles/
        ├── build.ninja           # If using Ninja
        └── ...
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Configuring in wrong directory | Must be in `projects/rocprofiler-systems/`, not monorepo root |
| Using monorepo build directory | Build dir must be inside the project, not at monorepo level |
| Missing dependencies | Use `-DROCPROFSYS_BUILD_<DEP>=ON` to build from source |
| CMake version too old | Install CMake 3.21+: `pip install --user cmake` |
| In-source build | Always use out-of-source: `-B build/...` |
| Forgetting generator | Specify `-G Ninja` for faster builds |
| Not checking configuration output | Always review CMake output for warnings |

## Troubleshooting

### Issue: "Could not find Dyninst"

**Solution:**
```bash
cmake --preset debug -DROCPROFSYS_BUILD_DYNINST=ON \
  -DROCPROFSYS_BUILD_TBB=ON \
  -DROCPROFSYS_BUILD_BOOST=ON \
  -DROCPROFSYS_BUILD_ELFUTILS=ON \
  -DROCPROFSYS_BUILD_LIBIBERTY=ON
```

### Issue: "CMake 3.21 or higher is required"

**Solution:**
```bash
pip install --user cmake==3.21.0
export PATH=$HOME/.local/bin:$PATH
```

### Issue: "Wrong project directory"

**Symptom:** CMakeLists.txt doesn't mention rocprofiler-systems

**Solution:** Navigate to `projects/rocprofiler-systems/` subdirectory within monorepo

### Issue: "Configuration failed with errors"

**Steps:**
1. Read error message carefully
2. Check for missing system dependencies
3. Try building dependencies from source
4. Check compiler version (GCC 7+)
5. Remove build directory and try again

## Integration with Other Skills

| After Configuration | Use |
|---------------------|-----|
| Build configured | `rocprofsys-build` to compile |
| Need to reconfigure | Remove build directory, run this skill again |
| Configuration failed | Check docs, install deps, try again |

## Notes

- **Monorepo awareness:** Always verify you're in `projects/rocprofiler-systems/`, not the monorepo root
- **Git worktrees:** Support multiple worktrees with different branches
- **Build isolation:** Each branch/worktree can have its own build directory
- **Preset modification:** Can override preset options with `-D` flags
- **Incremental changes:** Can reconfigure without removing build directory (most of the time)
- **Clean slate:** When changing major options (build type, dependencies), safer to remove build directory first
