# Scoring rubric

One score per fixture, one verdict per scenario. Aggregate weekly.

## Per fixture

```
fixture: <id>
date: <YYYY-MM-DD>

planted_issues:    <N>     # count of must-find rows in expectations.md
red_found:         <r>     # planted issues the baseline agent flagged
red_correct_sev:   <rs>    # of those, severity within one level
green_found:       <g>     # planted issues the skill-loaded agent flagged
green_correct_sev: <gs>    # of those, severity within one level
green_false_pos:   <fp>    # findings the agent invented that are not bugs

coverage_delta:    g - r           # higher is better; >= 0.5 * N is healthy
severity_acc:      gs / g          # 1.0 is target
noise:             fp / (g + fp)   # < 0.2 is healthy
```

## Per scenario

```
scenario: <id>
date: <YYYY-MM-DD>

choice_correct:       Y / N
cited_rule:           Y / N + which rule, verbatim
new_rationalization:  none | "<quoted excuse>"
verdict:              PASS | PARTIAL | FAIL
```

## Aggregate weekly

Append one row per fixture and one per scenario to
`results/<YYYY-WW>-summary.md`. Track:

- Coverage delta per fixture over time (should go up after each
  skill iteration, stay up after each refactor).
- Scenario PASS rate (target 100 %).
- Rationalization-table growth (slowing growth = stabilizing skill).

## Anti-metrics

Do NOT chase:

- Total finding count (lazy agents find fewer; over-eager agents
  invent more; neither is "good").
- Fixture count growth (more fixtures != better; need to plant
  *distinct* failure modes).
- GREEN runtime (the skill is meant to be thorough).
