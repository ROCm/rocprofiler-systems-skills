# Expectations: 07-cmake-rules

## Must-find

| File:Line | Rule | Severity | Detection by |
|-----------|------|----------|--------------|
| CMakeLists.txt:1 | `cmake_minimum_required(VERSION 3.5)` is too old; 3.5 is from 2016 and predates many modern features (target properties, generator expressions). Bump to 3.16+ (or whatever the project actually needs). | Should Fix (50) | language-rules-agent (programming-cmake-best-practices) |
| CMakeLists.txt:5-6 | Deprecated global `include_directories()`. Use `target_include_directories(widget PUBLIC include)` with `PUBLIC`/`PRIVATE`/`INTERFACE` semantics. | Must Fix (80) | language-rules-agent |
| CMakeLists.txt:8 | Deprecated `link_directories()`. Use `target_link_directories(widget PRIVATE /opt/legacy/lib)` or, better, find the library with `find_package` / `find_library`. | Must Fix (80) | language-rules-agent |
| CMakeLists.txt:10 | Global `set(CMAKE_CXX_FLAGS ...)` leaks to every target including dependencies. Use `target_compile_options(widget PRIVATE -O3 -Wall)`. Also `-O3` should be controlled by build type (`CMAKE_BUILD_TYPE=Release`), not hard-coded. | Must Fix (80) | language-rules-agent |
| CMakeLists.txt:12 | `file(GLOB SOURCES ...)` is fragile - CMake will not re-run when new files are added until you re-invoke cmake. Either list sources explicitly OR add `CONFIGURE_DEPENDS`. | Should Fix (50) | language-rules-agent |
| CMakeLists.txt:16 | `target_link_libraries(widget pthread dl)` without visibility (PUBLIC/PRIVATE/INTERFACE). For libraries this is the most important visibility choice. Specify it. Also: `Threads::Threads` via `find_package(Threads REQUIRED)` is the modern way for pthread. | Must Fix (80) | language-rules-agent |
| CMakeLists.txt:21-23 | `add_definitions(-DWIDGET_WINDOWS=1)` is the old global form. Use `target_compile_definitions(widget PUBLIC WIDGET_WINDOWS=1)`. | Should Fix (50) | language-rules-agent |

## May-find

- No `set(CMAKE_CXX_STANDARD 17)` / `target_compile_features(widget PUBLIC cxx_std_17)`. C++ standard unspecified.
- `add_library(widget ${SOURCES})` does not specify `STATIC` / `SHARED` / `OBJECT`. Whether that matters depends on `BUILD_SHARED_LIBS`; worth a note.

## Verdict

REQUEST CHANGES.
