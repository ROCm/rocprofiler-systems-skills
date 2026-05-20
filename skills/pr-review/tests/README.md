# pr-review skill test campaign

TDD applied to the `pr-review` skill, following the RED-GREEN-REFACTOR
methodology from `obra/superpowers/writing-skills/testing-skills-with-subagents.md`.

**Local-only**: not pushed upstream. Results in `results/` are
session artifacts.

## Contents

- `fixtures/` - canned diffs, each planting a known violation. Tests
  *coverage* (does the agent find what it should?).
- `scenarios/` - pressure scripts with 3+ combined pressures. Tests
  *discipline* (does the agent stay on-process when tempted?).
- `harness/` - how to spawn RED and GREEN subagent runs, and how to
  score the output.
- `results/` - per-run logs (`<date>-<phase>-<fixture-or-scenario>.md`).

## TDD cycle

| Phase | Action | Success criterion |
|-------|--------|-------------------|
| RED | Spawn subagent **without** the pr-review skill on each fixture | Agent misses planted issues, miscalibrates severity, or fails to follow process. Document verbatim. |
| GREEN | Spawn subagent **with** pr-review skill loaded on the same fixtures | Agent finds all planted issues, at the expected severity, with the documented process. |
| REFACTOR | Pressure-test GREEN with `scenarios/` | Agent picks the correct option and cites the skill rule. Capture new rationalizations; close holes in SKILL.md / QUALITY.md / PERFORMANCE.md. |

## How to run one fixture

See `harness/run-fixture.md` for the full command. Quick form:

1. Pick a fixture, e.g. `fixtures/01-getter-mutates/`.
2. Spawn the RED subagent (see `harness/run-red.md`). Save output to
   `results/<date>-RED-01-getter-mutates.md`.
3. Spawn the GREEN subagent (see `harness/run-green.md`). Save to
   `results/<date>-GREEN-01-getter-mutates.md`.
4. Score per `harness/score.md`. Append the score to
   `results/<date>-summary.md`.

## How to run a pressure scenario

See `harness/run-scenario.md`. Spawn a subagent with the pr-review
skill loaded, pass the scenario verbatim, capture the choice + the
rationalization word-for-word.

## When the skill passes

- All fixtures: every planted issue found at the expected severity
  in GREEN; RED misses at least 30 % of them.
- All scenarios: GREEN picks the documented correct option AND cites
  the SKILL.md / QUALITY.md / PERFORMANCE.md rule that made it pick
  that option.

If GREEN fails on a fixture: the agent prompt or the reference doc
(QUALITY.md / PERFORMANCE.md) is missing a rule. Add it; re-run.

If GREEN fails on a scenario: the skill has a loophole. Add an
explicit negation per `testing-skills-with-subagents.md` REFACTOR
phase; re-run.
