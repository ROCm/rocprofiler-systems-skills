---
name: programming-cpp-constexpr
description: Use when moving computation from runtime to compile time — precomputed lookup tables, compile-time constants, type-based template dispatch, or zero-cost conditional branching with if constexpr; use when a function or value could be evaluated before the binary runs
---

# C++ constexpr — Compile-Time Computation (C++17)

Move work to compile time: zero runtime cost, no dependencies, trivially testable.

## Core Forms

### constexpr variable

```cpp
constexpr int cache_line_bytes = 64;
constexpr double pi = 3.14159265358979;
```

### constexpr function

Evaluated at compile time when all arguments are compile-time constants; falls back to runtime otherwise:

```cpp
constexpr int square(int x) { return x * x; }

constexpr int a = square(8);  // compile time
int b = square(n);            // runtime — n is not constexpr
```

### if constexpr (C++17)

Compile-time branch — the non-taken branch is not compiled, not just skipped:

```cpp
template <typename T>
auto process(T val) {
    if constexpr (std::is_integral_v<T>)            return val * 2;
    else if constexpr (std::is_floating_point_v<T>) return val * 2.0;
    else                                            static_assert(false, "unsupported type");
}
```

Prefer `if constexpr` over tag dispatch or SFINAE — same result, far more readable.

### Compile-time lookup table

```cpp
constexpr auto build_lut() {
    std::array<int, 256> t{};
    for (int i = 0; i < 256; ++i) t[i] = i * i;
    return t;
}
constexpr auto lut = build_lut();  // built entirely at compile time

int val = lut[x];  // pure array access at runtime — zero computation
```

## When to Use

| Situation | Use |
|---|---|
| Constant known at compile time | `constexpr` variable |
| Pure function on compile-time inputs | `constexpr` function |
| Template branch on type property | `if constexpr` |
| Precomputed mapping / LUT | `constexpr` function returning `std::array` |
| Enforce compile-time evaluation | assign result to `constexpr` variable |

## Testing

`constexpr` functions are pure — no side effects, no dependencies — so no mocking is ever needed.

```cpp
// Compile-time: catches bugs before the binary exists
static_assert(square(8) == 64);
static_assert(lut[4] == 16);

// Runtime: works with GTest unchanged
TEST(Square, PositiveInput) { EXPECT_EQ(square(8), 64); }
```

## Forcing Compile-Time Evaluation

Assigning to a `constexpr` variable forces compile-time evaluation — the compiler errors if it cannot:

```cpp
constexpr int result = expensive_fn(args);  // fails to compile if args are not constexpr
```

This is the C++17 equivalent of `consteval` (C++20 — not available).

## Common Mistakes

| Mistake | Fix |
|---|---|
| Calling non-`constexpr` function inside `constexpr` function | Mark the callee `constexpr` or extract the computation |
| `if constexpr` outside a template | Only valid in a template context |
| Assuming `constexpr` function always runs at compile time | Assign to a `constexpr` variable to enforce it |
| Using `consteval` / `constinit` | C++20 only — use `constexpr` variable assignment in C++17 |
| Mutating state inside `constexpr` function | Allowed in C++14+ but the function must remain pure (no I/O, no globals) |
