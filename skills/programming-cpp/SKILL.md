---
name: programming-cpp
description: C++ programming skill based on C++ Core Guidelines - use for implementing C++ code
---

# C++ Programming Skill

Use this skill when writing or modifying C++ code.

<IMPORTANT>
Follow the [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines) as the primary reference for best practices.

**C++17 Standard.** This project uses C++17. Use only features available in C++17. Do NOT use C++20 features (concepts, ranges, std::span, etc.).

**Compile-time execution is a PRIORITY.** If code CAN be executed at compile time, it SHOULD be. Use `constexpr`, `if constexpr`, template metaprogramming. Move as much computation as possible from runtime to compile time.

**Performance is critical.** This is performance-sensitive software. Always consider performance implications. Prefer zero-cost abstractions, avoid unnecessary allocations, and be cache-friendly.

**All code MUST be unit testable.** Use Dependency Injection and/or Policy-based design to achieve testability.

**Guidelines override existing code style.** If you see existing code that violates the rules in this skill, apply these guidelines first and ignore the current project style. Do NOT propagate bad patterns just because they exist in the codebase.
</IMPORTANT>

## Philosophy (from C++ Core Guidelines)

- **P.1**: Express ideas directly in code
- **P.2**: Write in ISO Standard C++
- **P.3**: Express intent
- **P.4**: Ideally, a program should be statically type safe
- **P.5**: Prefer compile-time checking to run-time checking
- **P.6**: What cannot be checked at compile time should be checkable at run time
- **P.9**: Don't waste time or space
- **P.10**: Prefer immutable data to mutable data
- **P.11**: Encapsulate messy constructs, rather than spreading through the code

## Interfaces

- **I.1**: Make interfaces explicit
- **I.2**: Avoid non-const global variables
- **I.3**: Avoid singletons
- **I.4**: Make interfaces precisely and strongly typed
- **I.11**: Never transfer ownership by a raw pointer (`T*`) or reference (`T&`)
- **I.13**: Do not pass an array as a single pointer

## Functions

- **F.1**: "Package" meaningful operations as carefully named functions
- **F.2**: A function should perform a single logical operation
- **F.3**: Keep functions short and simple
- **F.4**: If a function might have to be evaluated at compile time, declare it `constexpr`
- **F.6**: If your function must not throw, declare it `noexcept`
- **F.7**: For general use, take `T*` or `T&` arguments rather than smart pointers
- **F.15**: Prefer simple and conventional ways of passing information
- **F.16**: For "in" parameters, pass cheaply-copied types by value and others by reference to `const`
- **F.17**: For "in-out" parameters, pass by reference to non-`const`
- **F.20**: For "out" output values, prefer return values to output parameters
- **F.21**: To return multiple "out" values, prefer returning a struct or tuple
- **F.26**: Use a `unique_ptr<T>` to transfer ownership where a pointer is needed
- **F.27**: Use a `shared_ptr<T>` to share ownership

## Classes and Class Hierarchies

- **C.1**: Organize related data into structures (`struct`s or `class`es)
- **C.2**: Use `class` if the class has an invariant; use `struct` if the data members can vary independently
- **C.4**: Make a function a member only if it needs direct access to the representation of a class
- **C.7**: Don't define a class or enum and declare a variable of its type in the same statement
- **C.9**: Minimize exposure of members
- **C.20**: If you can avoid defining default operations, do
- **C.21**: If you define or `=delete` any copy, move, or destructor function, define or `=delete` them all (Rule of 0/5)
- **C.35**: A base class destructor should be either public and virtual, or protected and non-virtual
- **C.47**: Define and initialize data members in the order of member declaration
- **C.48**: Prefer default member initializers to member initializers in constructors for constant initializers
- **C.49**: Prefer initialization to assignment in constructors
- **C.80**: Use `=default` if you have to be explicit about using the default semantics
- **C.82**: Don't call virtual functions in constructors and destructors
- **C.128**: Virtual functions should specify exactly one of `virtual`, `override`, or `final`
- **C.131**: Avoid trivial getters and setters
- **C.149**: Use `unique_ptr` or `shared_ptr` to avoid forgetting to `delete` objects created using `new`

## Resource Management

- **R.1**: Manage resources automatically using resource handles and RAII
- **R.2**: In interfaces, use raw pointers to denote individual objects (only)
- **R.3**: A raw pointer (`T*`) is non-owning
- **R.4**: A raw reference (`T&`) is non-owning
- **R.5**: Prefer scoped objects, don't heap-allocate unnecessarily
- **R.10**: Avoid `malloc()` and `free()`
- **R.11**: Avoid calling `new` and `delete` explicitly
- **R.12**: Immediately give the result of an explicit resource allocation to a manager object
- **R.13**: Perform at most one explicit resource allocation in a single expression statement
- **R.20**: Use `unique_ptr` or `shared_ptr` to represent ownership
- **R.21**: Prefer `unique_ptr` over `shared_ptr` unless you need to share ownership
- **R.22**: Use `make_shared()` to make `shared_ptr`s
- **R.23**: Use `make_unique()` to make `unique_ptr`s

## Error Handling

- **E.1**: Develop an error-handling strategy early in a design
- **E.2**: Throw an exception to signal that a function can't perform its assigned task
- **E.3**: Use exceptions for error handling only
- **E.6**: Use RAII to prevent leaks
- **E.13**: Never throw while being the direct owner of an object
- **E.14**: Use purpose-designed user-defined types as exceptions (not built-in types)
- **E.16**: Destructors, deallocation, `swap`, and exception type copy/move construction must never fail
- **E.17**: Don't try to catch every exception in every function
- **E.18**: Minimize the use of explicit `try`/`catch`
- **E.25**: If you can't throw exceptions, simulate RAII for resource management

## Performance (CRITICAL)

**This is performance-critical software.** Apply these rules from [C++ Core Guidelines - Performance](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#S-performance):

### Core Performance Rules

- **Per.1**: Don't optimize without reason
- **Per.2**: Don't optimize prematurely
- **Per.3**: Don't optimize something that's not performance critical
- **Per.4**: Don't assume that complicated code is necessarily faster than simple code
- **Per.5**: Don't assume that low-level code is necessarily faster than high-level code
- **Per.6**: Don't make claims about performance without measurements
- **Per.7**: Design to enable optimization
- **Per.10**: Rely on the static type system
- **Per.11**: Move computation from run time to compile time
- **Per.19**: Access memory predictably (cache-friendly)

### Memory & Allocation

```cpp
// BAD: Allocations in hot path
void process_items(const std::vector<item>& items) {
    for (const auto& item : items) {
        auto result = std::make_unique<result_t>();  // Allocation per iteration!
        // ...
    }
}

// GOOD: Pre-allocate or reuse
void process_items(const std::vector<item>& items) {
    result_t result;  // Stack allocation, reused
    for (const auto& item : items) {
        result.reset();
        // ...
    }
}

// GOOD: Reserve capacity
std::vector<int> results;
results.reserve(items.size());  // Avoid reallocations
```

### Avoid Unnecessary Copies

```cpp
// BAD: Unnecessary copy
void process(std::vector<int> data) { }  // Copies entire vector

// GOOD: Pass by const reference
void process(const std::vector<int>& data) { }

// GOOD: Pass by value if you need to modify/own it (enables move)
void take_ownership(std::vector<int> data) {
    m_data = std::move(data);
}

// BAD: Return by const reference from temporary
const std::string& get_name() { return m_name; }  // OK
const std::string& bad() { return std::string("temp"); }  // Dangling!

// GOOD: Return by value (RVO/NRVO applies)
std::string get_computed_name() {
    std::string result = compute();
    return result;  // Move or RVO, no copy
}
```

### Move Semantics

```cpp
// Use std::move when transferring ownership
std::vector<int> source = get_data();
process(std::move(source));  // source is now empty

// Implement move constructor/assignment for heavy classes
class heavy_resource {
public:
    heavy_resource(heavy_resource&& other) noexcept
        : m_data(std::exchange(other.m_data, nullptr)) {}
    
    heavy_resource& operator=(heavy_resource&& other) noexcept {
        if (this != &other) {
            delete m_data;
            m_data = std::exchange(other.m_data, nullptr);
        }
        return *this;
    }
};
```

### Cache-Friendly Code

```cpp
// BAD: Cache-unfriendly (pointer chasing)
struct node {
    node* next;
    int data;
};

// GOOD: Cache-friendly (contiguous memory)
std::vector<int> data;  // Contiguous, prefetch-friendly

// BAD: Column-major access in row-major array
for (int col = 0; col < cols; ++col)
    for (int row = 0; row < rows; ++row)
        matrix[row][col] = 0;  // Cache miss every access!

// GOOD: Row-major access
for (int row = 0; row < rows; ++row)
    for (int col = 0; col < cols; ++col)
        matrix[row][col] = 0;  // Sequential access
```

### Compile-Time vs Runtime

```cpp
// Prefer constexpr for compile-time computation
constexpr int factorial(int n) {
    return n <= 1 ? 1 : n * factorial(n - 1);
}
constexpr int fact_10 = factorial(10);  // Computed at compile time

// Use if constexpr for compile-time branching
template<typename T>
void process(T value) {
    if constexpr (std::is_integral_v<T>) {
        // Integer-specific code
    } else {
        // Other types
    }
}

// Prefer templates over virtual for known types (no vtable lookup)
template<typename Handler>
void process(Handler& h) { h.handle(); }  // Inlined, no virtual call
```

### Avoid Performance Pitfalls

| Pitfall | Solution |
|---------|----------|
| `std::endl` in loops | Use `'\n'` (no flush) |
| `std::map` for small sets | Use `std::vector` + linear search for < 20 elements |
| String concatenation in loops | Use `std::ostringstream` or pre-reserve |
| Unnecessary `shared_ptr` | Use `unique_ptr` (no atomic refcount) |
| Virtual calls in hot loops | Use CRTP or templates |
| `std::function` in hot path | Use templates or function pointers |
| Exceptions for control flow | Use return values or `std::optional` |
| Copying in range-for | Use `const auto&` |

### Performance Checklist

- [ ] No allocations in hot paths (pre-allocate, object pools)
- [ ] Pass large objects by `const&`, small by value
- [ ] Use `std::move` when transferring ownership
- [ ] Containers sized with `reserve()` when size is known
- [ ] Cache-friendly data access patterns
- [ ] `constexpr` for compile-time computations
- [ ] No unnecessary virtual calls in hot paths
- [ ] Measured and profiled before micro-optimizing

## Testability (REQUIRED)

**All C++ code must be designed for unit testing.** Use these patterns:

### Dependency Injection (Runtime)

Inject dependencies through constructor or setter instead of creating them internally:

```cpp
// BAD: Hard to test - creates its own dependency
class order_processor {
    database m_db;  // Creates concrete database
public:
    void process(const order& o) {
        m_db.save(o);  // Can't mock this
    }
};

// GOOD: Testable - dependency injected via interface
class i_database {
public:
    virtual ~i_database() = default;
    virtual void save(const order& o) = 0;
};

class order_processor {
    i_database& m_db;  // Injected dependency
public:
    explicit order_processor(i_database& db) : m_db(db) {}
    void process(const order& o) {
        m_db.save(o);  // Can be mocked in tests
    }
};

// Test with mock
class mock_database : public i_database {
public:
    void save(const order& o) override { /* verify call */ }
};
```

### Policy-Based Design (Compile-time)

Use templates with policy classes for compile-time dependency injection:

```cpp
// Policy-based design - zero runtime overhead
template<typename DatabasePolicy>
class order_processor {
    DatabasePolicy m_db;
public:
    void process(const order& o) {
        m_db.save(o);
    }
};

// Production policy
struct production_database {
    void save(const order& o) { /* real implementation */ }
};

// Test policy
struct mock_database {
    void save(const order& o) { /* mock implementation */ }
};

// Usage
using prod_processor = order_processor<production_database>;
using test_processor = order_processor<mock_database>;
```

### When to Use Which

| Pattern | Use When... |
|---------|-------------|
| **Dependency Injection** | Need runtime polymorphism, plugins, or when interface is natural |
| **Policy-Based Design** | Need maximum performance (no virtual calls), behavior known at compile time |
| **Both** | Complex systems may combine both approaches |

### Testability Checklist

- [ ] No hidden dependencies (file system, network, database, time, random)
- [ ] Dependencies injected via constructor or template parameter
- [ ] Pure functions where possible (same input → same output)
- [ ] Side effects isolated and injectable
- [ ] Classes have single responsibility (easier to test)

## Code Style & Attributes (REQUIRED)

### Early Return

**Use early return to reduce nesting and improve readability:**

```cpp
// BAD: Deep nesting
std::optional<result> process(const input& in) {
    if (in.is_valid()) {
        if (auto data = fetch_data(in)) {
            if (data->size() > 0) {
                return compute(*data);
            }
        }
    }
    return std::nullopt;
}

// GOOD: Early return (guard clauses)
std::optional<result> process(const input& in) {
    if (!in.is_valid())
        return std::nullopt;
    
    auto data = fetch_data(in);
    if (!data)
        return std::nullopt;
    
    if (data->empty())
        return std::nullopt;
    
    return compute(*data);
}
```

### const Correctness

**Mark everything `const` that doesn't need to change:**

```cpp
// Variables
const int max_size = 100;
const auto& item = container[0];  // const reference

// Parameters
void process(const std::string& input);  // Won't modify input

// Member functions
class data_holder {
public:
    int get_value() const { return m_value; }  // Doesn't modify object
    const std::string& get_name() const { return m_name; }
private:
    int m_value;
    std::string m_name;
};

// Pointers
const int* ptr_to_const;      // Can't modify *ptr
int* const const_ptr;         // Can't modify ptr itself
const int* const both_const;  // Can't modify either
```

### constexpr

**Use `constexpr` for compile-time evaluation:**

```cpp
// Constants
constexpr int max_buffer_size = 1024;
constexpr double pi = 3.14159265359;

// Functions that CAN be evaluated at compile time
constexpr int square(int x) { return x * x; }
constexpr int size = square(10);  // Computed at compile time

// Classes with constexpr constructors
struct point {
    constexpr point(int x, int y) : m_x(x), m_y(y) {}
    constexpr int x() const { return m_x; }
    constexpr int y() const { return m_y; }
private:
    int m_x, m_y;
};
constexpr point origin{0, 0};  // Compile-time construction
```

### noexcept

**Mark functions `noexcept` when they don't throw:**

```cpp
// Move operations SHOULD be noexcept (enables optimizations)
class resource {
public:
    resource(resource&& other) noexcept;
    resource& operator=(resource&& other) noexcept;
};

// Destructors are implicitly noexcept, but be explicit if needed
~resource() noexcept;

// Swap should be noexcept
void swap(resource& other) noexcept;

// Simple getters that can't fail
int get_size() const noexcept { return m_size; }

// Conditional noexcept
template<typename T>
void process(T& obj) noexcept(noexcept(obj.do_work())) {
    obj.do_work();
}
```

### [[nodiscard]]

**Use `[[nodiscard]]` when ignoring return value is likely a bug:**

```cpp
// Factory functions - result must be used
[[nodiscard]] std::unique_ptr<widget> create_widget();

// Error codes - must check result
[[nodiscard]] error_code save_file(const std::string& path);

// Functions with important return values
[[nodiscard]] bool try_lock();
[[nodiscard]] iterator find(const key_type& key);

// Entire class (C++17) - all methods return important values
class [[nodiscard]] result {
    // ...
};

// Note: [[nodiscard("message")]] requires C++20, use without message in C++17
```

### [[maybe_unused]]

**Use `[[maybe_unused]]` to suppress warnings for intentionally unused variables:**

```cpp
// Parameters unused in some configurations
void log_message([[maybe_unused]] const char* file, 
                 [[maybe_unused]] int line,
                 const std::string& message) {
#ifdef DEBUG
    std::cerr << file << ":" << line << ": " << message << "\n";
#else
    std::cerr << message << "\n";
#endif
}

// Variables used only in assertions
void process(const data& d) {
    [[maybe_unused]] bool valid = validate(d);
    assert(valid);  // Only used in debug builds
    // ...
}

// RAII guards where variable name isn't used
void critical_section() {
    [[maybe_unused]] std::lock_guard lock(m_mutex);
    // lock is "unused" but its lifetime matters
}
```

### Attributes Summary

| Attribute | Use When |
|-----------|----------|
| `const` | Value/object won't be modified |
| `constexpr` | Can be evaluated at compile time |
| `noexcept` | Function guaranteed not to throw |
| `[[nodiscard]]` | Ignoring return value is likely a bug |
| `[[maybe_unused]]` | Intentionally unused (suppress warning) |

## C++17 Features (USE THESE)

This project uses **C++17**. Use these features:

### Type Deduction & Inference
- **`auto`** for type inference when type is obvious
- **Structured bindings**: `auto [key, value] = map.begin();`
- **Class template argument deduction**: `std::pair p{1, 2.0};`

### Control Flow
- **`if constexpr`** for compile-time branching (PRIORITY!)
- **`if`/`switch` with initializer**: `if (auto it = map.find(key); it != map.end())`

### Standard Library
- **`std::optional<T>`** for optional values (no more nullptr/sentinel)
- **`std::variant<Ts...>`** for type-safe unions
- **`std::string_view`** for read-only string parameters (zero-copy!)
- **`std::any`** for type-safe void* (use sparingly)
- **`std::invoke`** for uniform callable invocation
- **`std::apply`** for tuple unpacking to function calls

### Compile-Time (PRIORITY)
- **`constexpr if`** - compile-time branching
- **`constexpr` lambdas** - lambdas can be constexpr
- **`inline` variables** - define variables in headers
- **Fold expressions** - `(args + ...)` for variadic templates

### Attributes
- **`[[nodiscard]]`** - warn if return value ignored
- **`[[maybe_unused]]`** - suppress unused warnings
- **`[[fallthrough]]`** - intentional switch fallthrough

### Filesystem
- **`std::filesystem`** - portable path/file operations

### Parallel Algorithms
- **Execution policies**: `std::execution::par`, `std::execution::seq`

```cpp
// C++17 examples
auto [iter, success] = map.insert({key, value});  // Structured binding

if constexpr (std::is_integral_v<T>) {  // Compile-time if
    // Only compiled for integral types
}

std::optional<int> find_value(int key);  // Optional return

std::string_view get_name();  // Zero-copy string view
```

### NOT Available (C++20+) - DO NOT USE
- ~~`std::span`~~ - scan project for existing span implementation, otherwise use pointer + size
- ~~Concepts~~ - use SFINAE or `static_assert`
- ~~Ranges~~ - use STL algorithms
- ~~`std::format`~~ - use `fmt` library or streams (if available in project)
- ~~Coroutines~~ - not available
- ~~`[[nodiscard("message")]]`~~ - use `[[nodiscard]]` without message
- ~~`gsl::span`~~ - GSL library is NOT used in this project

**For span-like functionality:**
1. First, search the codebase for existing span implementation (e.g., `span`, `array_view`, `buffer_view`)
2. If found, use the project's existing implementation
3. If not found, use pointer + size parameters:
   ```cpp
   // Instead of span
   void process(const T* data, size_t size);
   
   // Or use iterator pair
   template<typename Iterator>
   void process(Iterator begin, Iterator end);
   ```

## Naming Conventions

Follow project conventions. If none exist, use:

- `snake_case` for functions, variables, namespaces
- `PascalCase` for types (classes, structs, enums, type aliases)
- `SCREAMING_SNAKE_CASE` for macros and constants
- `m_` or `_` prefix for member variables
- Avoid Hungarian notation

## Documentation & Comments

### Doxygen Style (REQUIRED)

Use Doxygen-style comments for all public APIs:

```cpp
/**
 * Calculates the sum of two integers.
 * @param a The first integer.
 * @param b The second integer.
 * @return The sum of a and b.
 */
int add(int a, int b) {
    return a + b;
}

/**
 * Represents a network connection to a remote server.
 * 
 * This class manages the lifecycle of a TCP connection,
 * including automatic reconnection on failure.
 */
class connection {
public:
    /**
     * Establishes a connection to the specified host.
     * @param host The hostname or IP address.
     * @param port The port number.
     * @throws connection_error If the connection cannot be established.
     */
    void connect(std::string_view host, uint16_t port);

    /**
     * Sends data over the connection.
     * @param data Pointer to the data buffer.
     * @param size Number of bytes to send.
     * @return Number of bytes actually sent.
     */
    [[nodiscard]] size_t send(const void* data, size_t size);
};
```

### Common Doxygen Tags

| Tag | Usage |
|-----|-------|
| `@param name` | Document a function parameter |
| `@return` | Document return value |
| `@throws exception` | Document exceptions thrown |
| `@note` | Additional notes |
| `@warning` | Important warnings |
| `@see` | Cross-reference to related items |
| `@deprecated` | Mark as deprecated |
| `@code` / `@endcode` | Code example block |

### When NOT to Document

Don't add Doxygen comments for:
- Trivial getters/setters (self-explanatory)
- Private implementation details
- Obvious code (let the code speak)

```cpp
// ❌ UNNECESSARY - obvious getter
/**
 * Gets the name.
 * @return The name.
 */
const std::string& get_name() const { return m_name; }

// ✅ GOOD - just the code, it's self-explanatory
const std::string& get_name() const { return m_name; }
```

### Inline Comments

**IMPORTANT: Avoid meaningless comments.** Only add inline comments when the code's intent is not self-evident. Most code should be self-documenting through clear naming and structure.

```cpp
// ❌ BAD - restates the obvious
i++; // Increment i
int sum = a + b; // Add a and b
std::vector<int> numbers; // Vector of numbers
result.clear(); // Clear the result

// ❌ BAD - obvious operations
for (auto& item : items) { // Loop through items
    process(item); // Process each item
}

// ✅ GOOD - explains why, not what
i++; // Skip the header row
timeout *= 2; // Exponential backoff
buffer.reserve(1024); // Avoid reallocations in hot path

// ✅ GOOD - explains non-obvious behavior
result |= 0x80; // Set MSB for negative flag per protocol spec
constexpr int offset = 3; // Account for metadata bytes in packet header
```

**When to add comments:**
- Explaining **why**, not what (design decisions, workarounds, non-obvious algorithms)
- Clarifying complex business logic or domain-specific requirements
- Documenting assumptions or preconditions
- Explaining performance optimizations
- Noting TODOs or FIXMEs (sparingly)

**When NOT to add comments:**
- Describing what the code obviously does
- Repeating variable or function names
- Explaining standard language features or library calls
- Commenting every line or block

## Eliminating if/else Branching

**Long if/else chains are a code smell.** Replace with these patterns:

### When to Refactor

| Smell | Threshold |
|-------|-----------|
| if/else chain | 3+ branches |
| switch statement | 5+ cases |
| Deep nesting | 3+ levels |
| Type-based branching | Any `dynamic_cast` chain |

### Pattern 1: Polymorphism (Strategy/State)

**Use when:** Behavior varies by type, need extensibility.

```cpp
// BAD: if/else chain
void process(int type, Data& data) {
    if (type == 1) {
        handleType1(data);
    } else if (type == 2) {
        handleType2(data);
    } else if (type == 3) {
        handleType3(data);
    }
}

// GOOD: Polymorphism
class Handler {
public:
    virtual ~Handler() = default;
    virtual void process(Data& data) = 0;
};

class Type1Handler : public Handler {
    void process(Data& data) override { /* handle type 1 */ }
};

// Usage - no if/else
void process(Handler& handler, Data& data) {
    handler.process(data);
}
```

### Pattern 2: Lookup Table / Map

**Use when:** Mapping values to values, simple dispatch.

```cpp
// BAD: if/else for value mapping
std::string getStatusText(int code) {
    if (code == 200) return "OK";
    else if (code == 404) return "Not Found";
    else if (code == 500) return "Server Error";
    return "Unknown";
}

// GOOD: Lookup table
const std::unordered_map<int, std::string> STATUS_TEXT = {
    {200, "OK"},
    {404, "Not Found"},
    {500, "Server Error"}
};

std::string getStatusText(int code) {
    auto it = STATUS_TEXT.find(code);
    return it != STATUS_TEXT.end() ? it->second : "Unknown";
}
```

### Pattern 3: Command Map (Function Dispatch)

**Use when:** Different actions based on command/type.

```cpp
// BAD: if/else dispatch
void execute(const std::string& cmd, Context& ctx) {
    if (cmd == "start") start(ctx);
    else if (cmd == "stop") stop(ctx);
    else if (cmd == "pause") pause(ctx);
    else if (cmd == "resume") resume(ctx);
}

// GOOD: Command map
using CommandFn = std::function<void(Context&)>;
const std::unordered_map<std::string, CommandFn> COMMANDS = {
    {"start",  [](Context& ctx) { start(ctx); }},
    {"stop",   [](Context& ctx) { stop(ctx); }},
    {"pause",  [](Context& ctx) { pause(ctx); }},
    {"resume", [](Context& ctx) { resume(ctx); }}
};

void execute(const std::string& cmd, Context& ctx) {
    if (auto it = COMMANDS.find(cmd); it != COMMANDS.end()) {
        it->second(ctx);
    }
}
```

### Pattern 4: std::variant + std::visit

**Use when:** Type-safe union, different handling per type.

```cpp
// BAD: dynamic_cast chain
double getArea(Shape* shape) {
    if (auto* c = dynamic_cast<Circle*>(shape)) {
        return 3.14159 * c->radius * c->radius;
    } else if (auto* r = dynamic_cast<Rectangle*>(shape)) {
        return r->width * r->height;
    } else if (auto* t = dynamic_cast<Triangle*>(shape)) {
        return 0.5 * t->base * t->height;
    }
    return 0;
}

// GOOD: std::variant + std::visit
using Shape = std::variant<Circle, Rectangle, Triangle>;

double getArea(const Shape& shape) {
    return std::visit([](const auto& s) -> double {
        using T = std::decay_t<decltype(s)>;
        if constexpr (std::is_same_v<T, Circle>) {
            return 3.14159 * s.radius * s.radius;
        } else if constexpr (std::is_same_v<T, Rectangle>) {
            return s.width * s.height;
        } else {
            return 0.5 * s.base * s.height;
        }
    }, shape);
}
```

### Pattern 5: Early Return (Guard Clauses)

**Use when:** Validation or precondition checks cause deep nesting.

```cpp
// BAD: Deep nesting
Result process(Request* req) {
    if (req != nullptr) {
        if (req->isValid()) {
            if (req->hasPermission()) {
                if (req->data.size() > 0) {
                    return doActualWork(req);
                }
            }
        }
    }
    return Result::Error;
}

// GOOD: Early return (flat structure)
Result process(Request* req) {
    if (!req) return Result::Error;
    if (!req->isValid()) return Result::InvalidRequest;
    if (!req->hasPermission()) return Result::Forbidden;
    if (req->data.empty()) return Result::EmptyData;

    return doActualWork(req);
}
```

### Pattern 6: Null Object

**Use when:** Eliminating null checks throughout code.

```cpp
// BAD: Null checks everywhere
void logMessage(Logger* logger, const std::string& msg) {
    if (logger != nullptr) {
        logger->log(msg);
    }
}

// GOOD: Null Object pattern
class NullLogger : public Logger {
    void log(const std::string&) override { /* intentionally empty */ }
};

// Always have valid logger - no null checks needed
Logger& getLogger() {
    static NullLogger nullLogger;
    return currentLogger ? *currentLogger : nullLogger;
}

void logMessage(Logger& logger, const std::string& msg) {
    logger.log(msg);  // No null check needed
}
```

### Pattern 7: Template + if constexpr

**Use when:** Compile-time type-based branching.

```cpp
// BAD: Runtime type checking
void serialize(const std::any& value, std::ostream& out) {
    if (value.type() == typeid(int)) {
        out << std::any_cast<int>(value);
    } else if (value.type() == typeid(std::string)) {
        out << std::any_cast<std::string>(value);
    }
}

// GOOD: Compile-time branching (when types known)
template<typename T>
void serialize(const T& value, std::ostream& out) {
    if constexpr (std::is_integral_v<T>) {
        out << value;
    } else if constexpr (std::is_same_v<T, std::string>) {
        out << '"' << value << '"';
    } else {
        static_assert(always_false<T>, "Unsupported type");
    }
}
```

### Pattern Summary

| Pattern | Best For | Overhead |
|---------|----------|----------|
| **Polymorphism** | Extensible behavior, OOP design | Virtual call |
| **Lookup table** | Value mapping | Map lookup |
| **Command map** | Action dispatch | Map + function call |
| **std::variant** | Type-safe unions, closed set | Visit overhead |
| **Early return** | Validation, preconditions | None |
| **Null Object** | Eliminating null checks | None |
| **if constexpr** | Compile-time branching | None (compile-time) |

### When NOT to Refactor

Keep simple if/else when:
- Only 2 branches
- Logic is truly simple and clear
- Refactoring would add complexity without benefit
- Performance-critical hot path where map lookup is slower than branch

## Code Style Checklist

Before submitting C++ code:

### Correctness & Safety
- [ ] No raw `new`/`delete` - use smart pointers
- [ ] No raw owning pointers - use `unique_ptr` or `shared_ptr`
- [ ] RAII for all resources
- [ ] `const` correctness (mark `const` what doesn't change)
- [ ] `constexpr` for compile-time constants and functions
- [ ] `noexcept` on move ops, destructors, swap, simple getters
- [ ] `[[nodiscard]]` on factory functions and error codes
- [ ] `[[maybe_unused]]` for intentionally unused variables
- [ ] Early return pattern (reduce nesting with guard clauses)
- [ ] Virtual destructor for base classes (or protected non-virtual)
- [ ] Rule of 0/5 followed
- [ ] Clear ownership semantics

### Performance
- [ ] No allocations in hot paths
- [ ] Large objects passed by `const&`
- [ ] `std::move` used for ownership transfer
- [ ] Containers pre-sized with `reserve()` when possible
- [ ] Cache-friendly access patterns
- [ ] `constexpr` for compile-time computations
- [ ] No unnecessary virtual calls in critical paths

### Testability
- [ ] **Unit testable** - dependencies injected (DI or Policy-based design)
- [ ] No hidden dependencies (time, random, file system, network)
- [ ] Pure functions where possible

### Style & Documentation
- [ ] No implicit conversions that could be surprising
- [ ] No magic numbers - use named constants
- [ ] Public APIs documented with Doxygen (`/** */`)
- [ ] Inline comments explain **why**, not what (avoid obvious/meaningless comments)
- [ ] No comments on trivial code (getters, setters, obvious operations)

## References

- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines)
- [CppReference](https://en.cppreference.com/)
- [Effective Modern C++ by Scott Meyers](https://www.oreilly.com/library/view/effective-modern-c/9781491908419/)
