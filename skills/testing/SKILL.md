---
name: testing
description: Decides what tests are needed (unit / internal-integration / CTest-pytest / CLI e2e / format-validation), composes existing testing-* skills to write them, and on failure runs a structured triage to decide whether the test or the code is wrong. Use this skill ANY time a code change requires test coverage - for new features, bug fixes, and refactors. Routes to testing-gtest-gmock, testing-pytest, and testing-testplan as needed. Do NOT bypass straight to those skills; this dispatcher exists to enforce test-first discipline and prevent tailoring tests to existing-but-wrong code.
---

# testing (dispatcher)

Wraps the language/framework testing skills with three behaviors that the
underlying skills don't enforce on their own:

1. **Test scope decision** - works out which test types are needed for a
   given change before writing any of them.
2. **Test-first dispatch** - assertions express the *requirement*, not the
   current code behavior.
3. **Failure triage** - when a test fails, decides whether the test or the
   code needs to change *before* editing either.

When invoked from the workflow-session skill, `testing` runs at two points:
during **Implementation** (writing tests for new code) and during
**Verification** (running the full suite + triaging failures).

## Test scope decision

Before writing any test, answer these in order. Do not skip - each step
narrows the next.

### Step 1 - what does the change touch?

Map the changed files / symbols to a scope tier. A single change can need
multiple tiers.

| Change touches | Required test tiers |
|----------------|---------------------|
| Pure internal logic (private function, internal data structure) | **Unit** (gtest in `source/lib/.../tests/` or pytest in the appropriate `tests/` dir) |
| Cross-module call paths (e.g. `core/` → `rocpd/`) | Unit + **internal integration** (gtest fixtures that wire multiple internal libs together) |
| Public C/C++ API in `source/lib/rocprof-sys-user/` | Unit + **API contract** test (header + linkage check) |
| CLI tool behavior in `source/bin/<tool>/` | Unit + **CLI e2e** via the CTest+pytest harness |
| Python bindings or Python-visible API | Unit + **Python tests** via CTest+pytest |
| Instrumentation / runtime behavior (rocm, hip, sampling, OMPT, ...) | **CTest+pytest end-to-end** - instrumentation needs real workload runs, unit tests are insufficient |
| File I/O, IPC, external service calls | Unit + **integration** (real I/O, isolated tmpdir) |
| Trace/output formats (Perfetto `.proto`, ROCpd `.db`, Timemory JSON) | **Format validation** via the `rocprofsys-validator` MCP (snapshot + compare) |
| Performance-critical hot path | Unit + (where feasible) **benchmark** test. If no benchmark fits, document why in the implementation doc rather than skip silently. |
| External submodules under `external/` | Typically **none** (vendored third-party). Document the deliberate skip. |

### Step 2 - what category of change?

Stack a category-driven test on top of the scope-driven ones.

| Category | Additional test |
|----------|-----------------|
| **Bug fix** | A **regression test** that fails before the fix and passes after. Name it after the bug or include a `// regression: ...` comment pointing to the issue/PR. Without this test, the fix doesn't pass Verification. |
| **New feature** | Tests express each acceptance criterion from `04-implementation.md` directly. One test per criterion is the minimum. |
| **Refactor (no behavior change)** | (a) Existing tests still pass unchanged, (b) **behavioral baseline** captured pre-refactor and compared post-refactor via `rocprofsys-validator` (slice 4+), (c) new unit tests for newly-exposed seams. |
| **Public API change** | **Contract test** asserting the new shape (signatures, types, error modes). For binary-compat surfaces, an ABI check belongs in `tests/`. |

### Step 3 - write the decision down

Before writing any test, record the scope decision in
`04-implementation.md` (or the test plan, if `testing-testplan` produced
one). Format:

```markdown
## Test scope

- Unit: <files / fixtures planned>
- Internal integration: <or "none - change is purely internal">
- CTest+pytest: <or "none - no instrumentation/runtime behavior">
- Format validation: <or "none - no format change">
- Regression: <bug-fix only - name the test, link the bug>
- Skipped: <tier> - <reason>
```

Every tier is either planned or explicitly skipped with reason. No silent
omissions.

## Test plan composition

When the change is non-trivial (e.g., new feature touching multiple files,
or refactor crossing module boundaries), invoke `testing-testplan` BEFORE
writing tests. The plan output drives which specific tests to write.

For trivial changes (bug fix in a single function), skip the plan - go
straight to the test.

Heuristic: if step 1 of the scope decision lists more than one tier, you
probably want a plan.

## Test writing - dispatch

After the scope decision, dispatch to language/framework-specific skills:

| Test tier | Dispatch to |
|-----------|-------------|
| C++ unit / internal integration | `testing-gtest-gmock` |
| Python tests / CTest+pytest harness | `testing-pytest` |
| CLI e2e via CTest+pytest | `testing-pytest` (the harness drives the binary) |
| Format validation | Use `mcp__rocprofsys-validator__*` directly; no skill needed |

**Test-first bias** - when invoking the dispatched skill, the prompt MUST
emphasise: assertions express **the requirement** (from
`02-requirements.md` or `04-implementation.md`), not the current code
behavior. If you find yourself reading the implementation to figure out
what to assert, stop. Re-read the requirement.

## Failure triage protocol

When a test fails (during Implementation or Verification), do NOT edit
either the test or the code yet. First, run this triage:

### Triage questions

Answer in order. The first "yes" gives the fix-direction tag.

1. **Does the test correctly express the requirement?**
   - Re-read the relevant criterion in `02-requirements.md` or
     `04-implementation.md`.
   - If the test asserts something the requirement does NOT say (or
     contradicts it): tag `fix-test`. The test is wrong.

2. **Is the code violating the requirement?**
   - The test expresses the requirement correctly, and the code's
     behavior does not match. Tag `fix-code`. The code is wrong.

3. **Is the test brittle?**
   - The test depends on implementation details (private state, internal
     ordering, specific data structures) that aren't part of the
     requirement.
   - Tag `refactor-test`. Rewrite the test to assert the requirement
     directly, not the implementation detail.

4. **Is the requirement ambiguous, contradictory, or missing?**
   - The requirement doesn't unambiguously say what the right behavior is.
   - Tag `escalate`. Surface to the user. Do NOT pick a side.

### Output the tag before any edit

Emit the tag explicitly to the user (or log it in `04-implementation.md`
under "Triage decisions") before making any change. The tag is the
justification for the next edit. No edit without a tag.

### Anti-pattern to refuse

If you find yourself thinking "I'll just relax this assertion so the test
passes" - STOP. That is the exact anti-pattern this skill exists to
prevent. The triage must be done. If after the triage the answer is
genuinely `fix-test`, the assertion change is justified. If not, you're
fixing the wrong thing.

## Coverage check at Verification gate

When invoked at the Verification gate, this skill additionally verifies:

1. **Acceptance criteria → test mapping is total.** Every criterion in
   `04-implementation.md` has at least one test asserting it. Unmapped
   criteria fail the gate - they are NOT "we'll add this later" deferrals.
2. **All planned scope tiers exist.** The "Test scope" section from the
   implementation doc lists the planned tiers; verify each tier has tests
   in place (or an explicit skip with reason).
3. **All tests pass.** Run the relevant ctest filter; failures must come
   with a triage tag.

If any of these fail, Verification gate stays at `gate-pending`.

## Composition with other skills

- **testing-testplan** - invoked for non-trivial changes during Step 2 of
  scope decision.
- **testing-gtest-gmock** - invoked for C++ unit and integration tests.
- **testing-pytest** - invoked for Python and CTest+pytest harness tests.
- **rocprofsys-validator MCP** - invoked directly for format validation
  and behavioral snapshots/comparisons.
- **workflow-session** - invokes `testing` during Implementation (write
  tests) and Verification (run + triage).

## What this skill does NOT do

- Does not run benchmarks for performance regressions outside the
  behavioral baseline (that's a future concern; document in
  implementation doc).
- Does not write its own assertion DSL or test framework.
- Does not modify itself or any other skill.
- Does not skip the triage to "make tests pass." That is the bug it
  exists to prevent.
