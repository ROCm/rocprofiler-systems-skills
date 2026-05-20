# RED baseline: 06-python-rules

date: 2026-05-20
phase: RED (no pr-review skill loaded)
agent: general-purpose subagent, single pass
agent_id (transient): addf9c3c48c5ee258

## Verbatim findings from baseline

| File:Line | Severity | Description | Suggested Fix |
|---|---|---|---|
| parser.py:7 | Must Fix | Mutable default arguments `tags=[]` and `opts={}`. | Use `tags=None, opts=None` and initialize inside. |
| parser.py:10 | Must Fix | Bare `except:` swallows all exceptions. | Catch `json.JSONDecodeError` explicitly. |
| parser.py:21 | Must Fix | `data["items"]` raises `KeyError`. | `data.get("items", [])`. |
| parser.py:13-14 | Should Fix | Mutating the caller-supplied `tags` list. | Build a local list and return it. |
| parser.py:16 | Should Fix | Manual `%`-formatting eagerly builds the string. | Use lazy logging. |
| parser.py:22 | Should Fix | `item.upper()` assumes `item` is a string. | Guard with `isinstance(item, str)`. |
| parser.py:27 | Must Fix | `open()` without context manager. | Use `with open(...)`. |
| parser.py:35 | Must Fix | `Cache.get` ignores `ttl`. | Compare `time.monotonic() - ts > self.ttl`. |
| parser.py:34 | Nitpick | No `set`/`delete` methods. | Add `set(key, value)`. |
| parser.py:7 | Nitpick | Parameters lack type hints. | Add type hints + docstring. |
| parser.py:21 | Nitpick | `item is not None and item != ""` redundant. | Replace with `if item:`. |

Verdict: REQUEST CHANGES.

## Score vs expectations.md

| Planted issue | Found in RED? | Notes |
|---------------|---------------|-------|
| Mutable defaults | FOUND, Must Fix | matches |
| Bare except | FOUND, Must Fix | matches |
| Missing type hints | FOUND as Nitpick | severity downgrade vs Should Fix |
| Old % formatting | FOUND as Should Fix (with lazy-logging framing) | matches |
| Manual loop -> comprehension | NOT found explicitly | baseline focused on type-safety + logging form, missed the comprehension nudge |
| Verbose truthiness | FOUND as Nitpick | matches |
| `open()` without context manager | FOUND, Must Fix | matches |
| `Cache.get` dead TTL | FOUND, Must Fix | matches AND identified the same "name promises X" framing |
| `tags.append(k)` discards `v` | PARTIAL - flagged the mutation, did not propose `tags.extend(data.keys())` | minor framing miss |

## What RED reveals (signal for the skill)

1. Baseline is strong on Python textbook issues (mutable defaults,
   bare except, context managers). These are NOT differentiators.
2. **Baseline missed the comprehension nudge** (manual `for ... +
   if` -> `[x.upper() for x in items if x]`). GREEN with Agent 6
   (simplify) should catch this.
3. Baseline downgraded "missing type hints" to Nitpick. The
   pr-review skill rates this Should Fix per programming-python. If
   GREEN keeps it Nitpick, that is a real divergence worth
   capturing - either the skill or the agent is misaligned.
4. Baseline DID NOT propose the `tags.extend(data.keys())`
   simplification, only flagged the mutation side. The simplify
   axis is a real gap baseline doesn't fill.

## RED quality

- Coverage of planted issues: 8 / 9 (one partial).
- Severity accuracy: 1 mis-grade (type hints Nitpick vs Should Fix).
- Noise: 1 invented finding (`data["items"]` KeyError) is
  legitimate but was not in the planted list - bonus, not noise.

## Next step

Run GREEN. Watch for:
1. Does Agent 6 (simplify) propose the comprehension?
2. Does Agent 4 grade type hints as Should Fix?
3. Does Agent 3 (Dim 1 naming) make the `Cache.get` TTL framing
   sharper (the baseline already nailed it)?
