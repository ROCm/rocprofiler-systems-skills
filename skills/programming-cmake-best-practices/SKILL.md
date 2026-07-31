---
name: programming-cmake-best-practices
description: Use when creating, modifying, or refactoring CMake projects - `CMakeLists.txt`, `cmake/**`, `CMakePresets.json`. Modern CMake (3.x+) idioms: target-based, no global state, explicit dependencies, generator-expression-aware. Triggers on changes to those files. Skip for pure source code changes (use programming-cpp). Composes with: programming-cpp (the code being built), testing (CTest registration), rocprofsys-configure / rocprofsys-build (project-specific build wrappers).
---

# CMake Best Practices

You are an expert in modern CMake (3.15+) following official guidelines. Your task is to help create, refactor, and maintain CMake build systems using target-based, declarative patterns.

## Core Principles

1. **Think in terms of targets, not variables** - Use `target_*()` commands instead of global variables
2. **Be declarative, not imperative** - Describe what you want, not how to build it
3. **Avoid global scope pollution** - Keep settings attached to specific targets
4. **Use generator expressions** for conditional logic that depends on build configuration
5. **Prefer `PUBLIC`, `PRIVATE`, `INTERFACE`** keywords to control transitive dependencies

## Creating New CMake Projects

### Minimum CMakeLists.txt Structure
```cmake
cmake_minimum_required(VERSION 3.15...3.28)
project(ProjectName 
    VERSION 1.0.0
    DESCRIPTION "Brief description"
    LANGUAGES CXX)

# Set C++ standard as a project-wide default
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Create executable or library target
add_executable(myapp src/main.cpp)
# OR
add_library(mylib src/mylib.cpp)

# Link dependencies (modern way)
target_link_libraries(myapp PRIVATE mylib)
```

### Directory Structure Best Practices
```
project/
├── CMakeLists.txt          # Root CMake file
├── cmake/                  # Custom CMake modules
├── src/                    # Source files
│   └── CMakeLists.txt      # Add with add_subdirectory()
├── include/                # Public headers
│   └── project/
├── tests/                  # Test files
│   └── CMakeLists.txt
└── external/               # Third-party dependencies
```

## Refactoring to Modern CMake

### Replace Global Variables with Target Properties

**OLD (avoid):**
```cmake
include_directories(${PROJECT_SOURCE_DIR}/include)
add_definitions(-DMY_DEFINE)
link_directories(${SOME_LIB_DIR})
```

**NEW (use this):**
```cmake
target_include_directories(mylib PUBLIC 
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $)
target_compile_definitions(mylib PRIVATE MY_DEFINE)
target_link_libraries(mylib PUBLIC somelib)
```

### Visibility Keywords (PUBLIC/PRIVATE/INTERFACE)

- **PRIVATE**: Only this target needs it
- **INTERFACE**: Consumers of this target need it, but this target doesn't
- **PUBLIC**: Both this target and its consumers need it
```cmake
target_include_directories(mylib
    PUBLIC include/           # Headers consumers will use
    PRIVATE src/             # Internal implementation headers
)

target_link_libraries(mylib
    PUBLIC fmt::fmt          # Appears in public API
    PRIVATE sqlite3          # Internal implementation detail
)
```

## Modern Linking Patterns

### Using find_package() with Imported Targets
```cmake
find_package(Boost 1.70 REQUIRED COMPONENTS system filesystem)
target_link_libraries(myapp PRIVATE Boost::system Boost::filesystem)
```

### Using FetchContent for Dependencies (CMake 3.14+)
```cmake
include(FetchContent)

FetchContent_Declare(
    googletest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG v1.14.0
)
FetchContent_MakeAvailable(googletest)

target_link_libraries(mytests PRIVATE GTest::gtest_main)
```

### Creating Interface Libraries (Header-Only)
```cmake
add_library(myheaderlib INTERFACE)
target_include_directories(myheaderlib INTERFACE include/)
target_compile_features(myheaderlib INTERFACE cxx_std_17)
```

## Building and Configuration

### Proper Out-of-Source Build Commands
```bash
# Configure
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release

# Build
cmake --build build --config Release

# Install
cmake --install build --prefix /usr/local

# Test
ctest --test-dir build
```

### Setting Compiler Flags (Modern Way)
```cmake
target_compile_options(myapp PRIVATE
    $<$:-Wall -Wextra -pedantic>
    $<$:/W4>
)
```

### Export and Install Targets
```cmake
install(TARGETS mylib
    EXPORT mylibTargets
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
    INCLUDES DESTINATION include
)

install(EXPORT mylibTargets
    FILE mylibTargets.cmake
    NAMESPACE mylib::
    DESTINATION lib/cmake/mylib
)
```

## Common Refactoring Tasks

### Converting to Modern target-based CMake

1. **Identify all executables and libraries** - List all `add_executable()` and `add_library()` calls
2. **Replace global commands** - Convert `include_directories()`, `link_libraries()`, etc. to `target_*()` equivalents
3. **Add visibility keywords** - Determine what should be PUBLIC vs PRIVATE
4. **Use generator expressions** - Replace if/else with `$<...>` for config-dependent settings
5. **Modularize with subdirectories** - Use `add_subdirectory()` for organized structure

### Testing the Refactoring
```bash
# Clean build to ensure no leftover state
rm -rf build && cmake -S . -B build
cmake --build build
ctest --test-dir build --output-on-failure
```

## Guidelines Summary

- Always use `cmake_minimum_required()` at the top
- Never use `file(GLOB)` for source files in production - list them explicitly
- Use `target_sources()` to add sources after target creation
- Prefer `option()` for user-configurable settings
- Use `CMAKE_PROJECT_NAME` instead of hardcoded project names
- Set properties with `set_target_properties()` when needed
- Use `cmake_path()` (CMake 3.20+) for path manipulation
- Enable testing with `enable_testing()` and use `add_test()`

## Resources

- **Official CMake Documentation**: https://cmake.org/cmake/help/latest/
  - Modern CMake guide: Search for "cmake-buildsystem(7)"
  - Command reference: https://cmake.org/cmake/help/latest/manual/cmake-commands.7.html

- **CMake Discourse**: https://discourse.cmake.org/ (for specific questions)

- **"An Introduction to Modern CMake"**: https://cliutils.gitlab.io/modern-cmake/
- **CMake Generator Expressions**: https://cmake.org/cmake/help/latest/manual/cmake-generator-expressions.7.html

- For package finding: Search official docs for "Find<PackageName>.cmake" modules
- For debugging: Use `cmake --trace` or `message(STATUS "...")` statements