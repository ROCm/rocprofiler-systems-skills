# Performance - Definition

## Contents

- Bar for performance-safe change (four-question test)
- Dimension 0: Hot-path classification (hot / warm / cold + severity bump rule)
- Dimension 1: Allocation and copy audit (new/malloc, container growth, copies, regex)
- Dimension 2: Algorithmic complexity (N^2 traps, sort-in-loop, recursion)
- Dimension 3: Lock contention and synchronization (lock-across-IO, memory order, lock-free)
- Dimension 4: I/O and syscall patterns (buffering, endl, getenv, blocking syscalls)
- Dimension 5: GPU / profiling / domain-specific
- How the Performance Agent reports + project-memory overrides

Reference loaded by the `pr-review` skill (Performance Agent) to judge
whether a change introduces performance regressions or hot-path
hazards during a review.

A change is **performance-safe** when:

1. The reviewer can name which path it runs on (hot / warm / cold).
2. Hot-path code does not allocate per call, copy large objects per
   call, hold locks across slow operations, or perform synchronous
   I/O.
3. Algorithmic complexity is justified by data size and access
   pattern, not by what was easy to type.
4. Container growth has an upper bound that is reserved up front
   when knowable.

The five dimensions below operationalize that bar. Severity uses the
same scale as the rest of `pr-review` (Critical / Must Fix / Should
Fix / Nitpick), elevated by one level inside hot paths.

---

## Dimension 0: Hot-path classification (always done first)

Every flagged change is classified before severity is assigned.

| Class | Definition | Detection signals |
|---|---|---|
| `hot` | Per-request / per-frame / per-sample / per-event path | Called from inner loops; name matches `on_*`, `dispatch_*`, `tick`, `step`, `poll`, `record`, `process_sample`, `handle_event`; located in files marked hot in project memory; called from benchmark binaries; runs inside profiler callbacks |
| `warm` | O(N) setup/teardown that scales with input size | Per-file, per-connection, per-record init; one-time-per-input parsing |
| `cold` | One-shot init, CLI parsing, error reporting, logging-only | `main()`, constructors of long-lived singletons, error paths, help text |

**Rule:** a finding inside a `hot` function gets severity bumped by
one level (Should Fix -> Must Fix; Nitpick -> Should Fix). A finding
inside a `cold` function gets severity dropped by one level unless
it is a Critical (correctness implication, lock-order inversion,
unbounded recursion).

---

## Cost reference (why the severities below are what they are)

Order-of-magnitude costs on commodity x86-64 hardware. These ground
the "Must Fix vs Should Fix" calls in concrete numbers, not taste.

| Operation | Approx cost | Why it matters |
|---|---|---|
| L1 cache hit | ~1 ns (~4 cycles) | Baseline; never the bottleneck on its own |
| L2 hit | ~3-4 ns | Tolerable in hot path |
| L3 hit | ~10-15 ns | Adds up across iterations |
| Main memory (cache miss) | ~80-120 ns | A single miss erases dozens of ALU ops |
| Branch mispredict | ~10-20 cycles | Why branchy hot loops hurt |
| `new` / `malloc` (uncontended) | ~50-150 ns | Allocator lock, free-list walk, possibly zeroing |
| `new` / `malloc` (contended) | microseconds | Multi-threaded allocator pressure |
| Atomic CAS (uncontended) | ~5-20 ns | Cheap-ish |
| Atomic CAS (contended) | hundreds of ns -> microseconds | Cache-line bouncing |
| `std::mutex` lock/unlock (uncontended) | ~25 ns | OK outside the inner loop |
| `std::mutex` lock/unlock (contended) | microseconds + scheduler entry | Wait time dominates |
| Syscall (cheap, e.g. `gettimeofday` via vDSO) | ~20-30 ns | Acceptable; raw syscall ~300 ns is not |
| `write()` / `read()` syscall (small) | ~300 ns - 1 us | Buffer or batch |
| `open()` / `close()` | ~5-10 us | Never per-record in hot |
| Synchronous DNS / blocking syscall | milliseconds - seconds | Catastrophic on event loops |
| `cudaMemcpy` (sync, small) | ~10-30 us | Round-trip dominated by launch overhead |
| Per-event `printf` / iostream | microseconds + lock + syscall | Triple cost: format + lock + I/O |

**Severity calibration rule**:
- Hot-path operation that adds >= 100 ns per call OR involves a
  syscall, contended lock, or allocation: **Must Fix**.
- Hot-path operation that adds 10-100 ns and is easy to remove:
  **Should Fix**.
- Anything that turns O(N) into O(N^2) when N can grow: **Must Fix**
  regardless of hot/warm/cold (correctness-of-scaling).
- Lock-order inversion or signal-handler unsafety: **Critical** -
  these are correctness bugs that masquerade as perf concerns.

## Dimension 1: Allocation and copy audit

The most common perf regression in C++ is a copy or allocation that
nobody noticed.

### Always flag

| Pattern | hot | warm | cold |
|---|---|---|---|
| `new` / `malloc` / `make_unique` / `make_shared` per call | Must Fix | Should Fix | Nitpick |
| Container growth without `reserve` when N is known or bounded | Must Fix | Should Fix | Nitpick |
| Pass-by-value of non-trivial types (any `std::string`, container, `std::function`, or > 16-byte non-trivial struct) when const-ref would do | Should Fix | Should Fix | Nitpick |
| Implicit temporaries: `std::string(const char*)` per call; `string_view -> string` on a lookup; `int -> string` per record | Must Fix | Should Fix | Nitpick |
| `shared_ptr` where `unique_ptr` or raw observer would suffice | Should Fix | Nitpick | Nitpick |
| Repeated map/set lookups (`m.find(k)` then `m[k]`); use `m.insert_or_assign` / structured bindings on `try_emplace` | Should Fix | Should Fix | Nitpick |
| Capture-by-value of large objects in a local lambda | Should Fix | Nitpick | Nitpick |
| Iterating with `auto` (copy) over heavy elements; should be `const auto&` | Should Fix | Nitpick | Nitpick |
| `std::regex` constructed per call rather than `static const` | Must Fix | Should Fix | Nitpick |
| String building via `+=` / `+` in a loop instead of one `reserve` + `append` or `fmt::format_to(back_inserter, ...)` | Must Fix | Should Fix | Nitpick |

### Do NOT flag

| Pattern | Reason |
|---|---|
| Return-by-value of a container the caller will move-construct | RVO / NRVO covers it |
| `std::move` on a trivially copyable type | Pessimization but not a regression worth a finding; Nitpick at most |
| One-shot allocation in a constructor of a long-lived object | Cold; allocator pressure does not matter |
| Copy of a small (`<= 16` bytes) trivially copyable type | Cheaper than indirection |
| `make_unique` whose owner is a long-lived singleton | One-time cost |

---

## Dimension 2: Algorithmic complexity

Big-O matters when data grows; constant factors matter when N is
fixed. The reviewer must say which.

### Always flag

| Pattern | Severity (in hot) | Severity (elsewhere) |
|---|---|---|
| Nested loop over the same container yielding O(N^2) when O(N log N) or O(N) is feasible | Must Fix | Should Fix |
| Linear search inside a tight loop building the same data (use a hash set / map) | Must Fix | Should Fix |
| `std::sort` inside a loop instead of once before the loop | Must Fix | Should Fix |
| Quadratic string building via repeated concat | Must Fix | Should Fix |
| Unbounded recursion that could overflow on adversarial input | Must Fix everywhere | Must Fix everywhere |
| `std::list` / `std::deque` where `std::vector` would win on cache | Should Fix | Nitpick |
| `std::map` / `std::set` where `std::unordered_map` / flat container would win and ordering is not needed | Should Fix | Nitpick |

### Reviewer responsibility

Always state the input size assumption that drives the verdict
("expected N <= 8" -> O(N^2) is fine; "N can grow with traffic" ->
O(N^2) is not). If the reviewer cannot find an upper bound, treat
unbounded as the default and flag.

---

## Dimension 3: Lock contention and synchronization

Locks are correctness primitives that pay performance bills. They
must be small and short.

### Always flag

| Pattern | Severity |
|---|---|
| Lock held across an I/O call, syscall, or allocation | Must Fix |
| Lock held across a callback / user function pointer / virtual call into client code | Must Fix |
| Lock taken in a destructor of an object that may be destroyed under another lock (lock-order inversion risk) | Critical |
| Repeated acquire/release inside a tight loop; should hoist or batch | Should Fix |
| `std::mutex` where reads dominate and `std::shared_mutex` would let readers proceed in parallel | Should Fix |
| Atomic with `memory_order_seq_cst` where a weaker order is sufficient AND the path is hot | Should Fix |
| `std::condition_variable` `notify_all` where only one waiter can make progress (`notify_one`) | Should Fix |
| Double-checked locking implemented manually (use `std::call_once`) | Must Fix |
| Spinning on an atomic without backoff on a hot path | Should Fix |

### Lock-free escalation

A lock-free claim ("uses atomics, no mutex") only escapes flagging
if the reviewer can cite the memory order at every operation and
the algorithm is recognizable from the literature. Otherwise treat
as Must Fix and ask for a lock or a well-known algorithm.

---

## Dimension 4: I/O and syscall patterns

Syscalls cost microseconds; allocation costs nanoseconds; cache
misses cost hundreds of cycles. Order operations accordingly.

### Always flag

| Pattern | Severity |
|---|---|
| Per-record `write()` / `fwrite()` without buffering | Must Fix in hot |
| `open()` / `close()` per call where a long-lived handle would do | Must Fix in hot |
| Per-call `getenv()` / `localtime()` / `gettimeofday()` / `clock_gettime(REALTIME)` on a hot path; cache or use monotonic | Should Fix |
| `printf` / `std::cout` in hot path without a log-level gate | Must Fix |
| `std::endl` in hot path (flushes); use `'\n'` | Should Fix |
| Synchronous DNS / blocking syscall on a loop thread / event loop | Must Fix |
| `fopen` / `fclose` round-trip per metric / per record | Must Fix in hot |
| `read()` returning short reads without a loop (correctness AND syscall amplification) | Must Fix |

### Buffering rule

Anything I/O in a loop must either go through a buffered wrapper or
batch its writes. The reviewer states the batch size or buffer
capacity.

---

## Dimension 5: GPU / profiling / domain-specific

Apply when the project includes GPU code, profiler instrumentation,
or any latency-sensitive callback.

### Always flag

| Pattern | Severity |
|---|---|
| Per-kernel-launch host allocation in a sampling path | Must Fix |
| String formatting inside a sample callback (use deferred formatting / numeric IDs) | Must Fix |
| Synchronous `cudaMemcpy` / `hipMemcpy` where async + event would suffice | Should Fix |
| Profiler instrumentation that allocates per event | Must Fix |
| Kernel arg construction that copies large host buffers per launch | Should Fix |
| Profile-time work performed in a non-profile build (no `#if` / runtime gate) | Should Fix |
| Signal handler doing anything non-async-signal-safe (allocation, locking, I/O) | Critical |

---

## How the Performance Agent reports

For each finding, the agent must state:

1. **File:line**
2. **Hot/warm/cold classification** and the signal that decided it
3. **Pattern matched** (which dimension and which rule)
4. **Cost in concrete terms** (cycles, cache line, allocator round-trip,
   syscall, contended cache line, ...). "Slow" is not a reason.
5. **Recommended fix** with the specific API or pattern, not just
   "avoid this"
6. **Severity** post-elevation

A change passes the performance review when every finding inside a
hot path is at Should-Fix or lower after applying suggested fixes,
and no Critical findings remain anywhere.

### Project-memory overrides

The agent's memory file
(`~/.claude/projects/<project>/memory/agents/performance.md`) lists:

- Files / functions confirmed hot by past work
- Patterns documented as accepted (with rationale)
- Benchmark binaries and where their results live
- Compiler / library specifics that change the trade-off

Memory overrides defaults. If memory contradicts a recommendation,
follow memory and note the rationale in the finding.
