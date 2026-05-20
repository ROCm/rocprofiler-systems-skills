# Quality Code - Definition

Reference loaded by the `pr-review` skill (Code Smells Agent) to judge
function-level quality during a review.

A piece of code is **quality** when a competent reader of the
codebase can answer all of the following with "yes" after reading
the function once, top to bottom, without scrolling or jumping:

1. The name tells me what it does and what it returns.
2. I can hold the whole control flow in my head.
3. It does one thing. The "and" word never appears in an honest
   one-sentence summary.
4. Every literal that carries meaning has a name.

The four dimensions below operationalize that bar. Each has a hard
threshold (auto-flag) and a soft threshold (flag with rationale).
Severity uses the same scale as the rest of `pr-review` (Critical /
Must Fix / Should Fix / Nitpick).

---

## Dimension 1: Naming <-> Behavior Match

The function name is a contract. The body must honor it.

### Rules

| Rule | Violation |
|---|---|
| Verb-noun for actions, noun/adjective for queries | `userData()` that writes a file; `saveUser()` that returns a parsed struct |
| `get_*` / `is_*` / `has_*` / `find_*` / `peek_*` are pure | Side effects inside (mutates state, logs, allocates persistent resources, I/O) |
| `set_*` / `update_*` / `apply_*` / `commit_*` mutate | No-op or pure return |
| Boolean-returning name matches polarity | `is_valid()` that returns `true` on invalid; `has_error()` that returns `false` when there is an error |
| Plural name returns a collection; singular returns one | `parse_tokens()` returning a single token; `get_user()` returning a vector |
| Async / blocking marked in name where idiomatic | `load_*` blocks for 5 seconds without `_sync` / `_blocking` suffix in a codebase that uses such suffixes |
| `*_unchecked` / `*_unsafe` / `*_raw` accurately mark contract relaxations | Name claims "unchecked" but still asserts; name omits "unsafe" but skips bounds checks |
| Negations not stacked | `is_not_invalid()`, `disable_disabled_path()` |
| Acronyms / abbreviations consistent with codebase | `ParseHTTPResponse` next to `parseHttpResponse` in the same file |

### Severity

- **Must Fix**: getter mutates, polarity inverted, plural/singular mismatch, lying `*_unchecked`
- **Should Fix**: weak verb (`doStuff`, `handle`, `process` with no qualifier when the body is specific)
- **Nitpick**: stylistic case inconsistency

### Anti-pattern - "manager / handler / processor"

`FooManager::handle()` or `BarProcessor::process()` tell the reader
nothing. Flag as Should Fix and ask for a verb-noun rename based on
what the body actually does.

---

## Dimension 2: Cognitive Complexity

The reader should not need a whiteboard.

### Hard limits (auto-flag)

| Metric | Should Fix | Must Fix |
|---|---|---|
| Nesting depth (any `if`/`for`/`while`/`switch`/`try`) | > 3 | > 4 |
| Cyclomatic complexity (branches + 1) | > 10 | > 15 |
| Distinct early-exit points without guard structure | > 5 unstructured | mixed with deep nesting |
| Lines per function (excluding signature, braces, blanks) | > 40 | > 80 |
| Boolean operands in a single conditional | > 3 unnamed | > 4 |

### Flow-clarity rules

| Rule | Violation |
|---|---|
| Prefer guard clauses + early return over `else` after `return` | `if (ok) { ... } else { return X; }` with a 30-line `then` branch |
| One level of abstraction per function | Mixes low-level byte twiddling with high-level orchestration calls |
| Loop body is a paragraph, not a chapter | 60-line `for` body |
| Conditions extracted to named predicates when > 3 operands | `if (a && b && (c \|\| d) && !e)` instead of `if (request_is_ready(...))` |
| State machines have a single, obvious switch over the state enum | Branches on state scattered across the function |
| No "arrow" shape (deeply right-shifted code) | Code that drifts past column 60 from nesting alone |

### Severity

- **Must Fix**: any hard-limit Must-Fix breach, or unclear flow that
  reviewer cannot trace in one read
- **Should Fix**: soft-limit breach, OR cognitive load could be
  cut by extracting one helper
- **Nitpick**: stylistic - condition could be named but is small enough

### Note

These are **defaults**. Project memory may raise thresholds where
justified (e.g. parser dispatch tables). Lowering is also allowed.
Document deviations in `agents/code-smells.md` memory.

---

## Dimension 3: Single Responsibility per Function

A function does one thing if its honest one-sentence summary uses
**no "and"**. "Parse the header **and** validate the signature
**and** dispatch" = three functions.

### Symptoms of >1 responsibility

| Symptom | Example |
|---|---|
| Section comments inside the body | `// --- step 1: parse ---`, `// --- step 2: validate ---` |
| Local "phase" variables with values like `PHASE_PARSE`, `PHASE_VALIDATE` | A loop that branches on what phase it is in |
| Two unrelated parameter groups | `(parser_state*, validator_state*, dispatch_table*)` |
| Body splits into chunks separated by blank lines, each chunk operating on disjoint locals | The blank lines are the seams |
| Mix of read and write to disjoint subsystems | Reads from config, writes to log, calls renderer |
| Return value used differently by different callers | Half the callers want the parsed result, half want only the error code |
| Function is named with "and" or "or" or generic verb | `parse_and_validate`, `init_or_reload`, `do_request` |

### When to suggest a split

Suggest a split when **two or more** symptoms above are present, OR
when nesting depth and length both breach Dimension 2 hard limits.

### How to suggest

Always pair the split suggestion with a proposed decomposition:

```
Current: dispatch_request(req)  // 120 lines, depth 5
Suggest:
  parse_request_header(req)     -> ParsedHeader
  validate_header(parsed)       -> Result<Validated, Error>
  route_to_handler(validated)   -> Response
  dispatch_request(req) becomes a 6-line pipeline
```

Reviewer must propose names for the extracted functions, not just say
"split this".

### Severity

- **Must Fix**: function is unreviewable as-is AND has >=3 symptoms
- **Should Fix**: 2 symptoms, OR 1 symptom + a Dimension-2 hard limit
- **Nitpick**: 1 symptom alone, function still readable

---

## Dimension 4: Magic Numbers and Strings

A literal carries meaning when the reader has to ask "why this
value?". Replace with a named constant whose name answers the
question.

### Always flag (Should Fix)

| Pattern | Fix |
|---|---|
| Numeric thresholds: timeouts, retries, buffer sizes, limits | `constexpr int MAX_RETRIES = 5;` |
| Bit masks and shifts whose meaning is not obvious from context | `constexpr uint32_t FLAG_READY = 1u << 3;` |
| Port numbers, version numbers, protocol constants | `constexpr int DEFAULT_PORT = 8080;` |
| Polling intervals, sleep durations | `constexpr auto POLL_INTERVAL = 100ms;` |
| Format strings reused in multiple call sites | Promote to named constant |
| Error / status strings that branch logic | `constexpr std::string_view STATUS_OK = "ok";` then compare against the constant |

### Do NOT flag

| Pattern | Reason |
|---|---|
| `0`, `1`, `-1`, `2` used arithmetically (increments, indices, halving) | Universally understood |
| Empty / nullopt / default literals: `""`, `{}`, `std::nullopt`, `nullptr` | Self-evident |
| Test fixture data | Magic-by-design, often the test name documents intent |
| `100` in a percentage calculation alongside a `%` symbol or comment | Domain-obvious |
| Loop-local accumulators starting at `0` | Loop body explains it |

### Severity

- **Must Fix**: numeric literal that controls security / correctness
  (crypto key length, signature size, timeout that affects safety)
- **Should Fix**: any default-flag literal above
- **Nitpick**: a duplicated literal used twice in nearby lines that
  the reader can trivially see is the same

### Heuristic

If a future change would require updating the literal in two places
to stay consistent, it must be a named constant **now**.

---

## How the Code Smells Agent applies this

The agent loads this file as part of its skill setup, then for each
changed function:

1. Run all four dimensions in order.
2. Collect findings with severity per the tables above.
3. Cite the dimension number in each finding (Dim 1 / Dim 2 / Dim 3 / Dim 4).
4. For Dim 3 splits and Dim 1 renames, **propose** the new structure
   or name; do not stop at "rename this".
5. Defer to project-memory overrides where present.

A function is acceptable when **all four** dimensions pass at the
Should-Fix bar or better. A function fails review when **any one**
dimension has a Must-Fix breach.
