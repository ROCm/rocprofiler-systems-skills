# Expectations: 06-python-rules

## Must-find

| File:Line | Rule | Severity | Detection by |
|-----------|------|----------|--------------|
| parser.py:8 | Mutable default arguments: `tags=[]`, `opts={}`. Shared across calls; classic Python footgun. `tags=None` + `tags = [] if tags is None else tags`. | Must Fix (80) | language-rules-agent (programming-python) |
| parser.py:11 | Bare `except:` swallows everything including `KeyboardInterrupt`, `SystemExit`. Use `except json.JSONDecodeError:` (the actual error from `json.loads`). | Must Fix (80) | language-rules-agent |
| parser.py:8, 28, 32 | Missing type hints on every public function. `def parse_payload(raw: str, tags: list[str] | None = None, opts: dict | None = None) -> list[str] | None:`. | Should Fix (50) | language-rules-agent |
| parser.py:17 | Old-style `%` formatting where f-string would do. `f"loaded {len(data)} items with opts={opts}"`. | Should Fix (50) | language-rules-agent |
| parser.py:20-23 | Manual loop where list comprehension is clearer: `[item.upper() for item in data["items"] if item]`. | Should Fix (50) | simplify-agent + language-rules-agent (comprehensions) |
| parser.py:22 | Verbose truthiness: `item is not None and item != ""`. For strings, `if item:` covers both. | Nitpick (20) | simplify-agent |
| parser.py:28-31 | `open()` without context manager - file may leak on error path. Use `with open(path, "a") as f: ...`. The function signature is awkward (returns the open handle) - rethink. | Must Fix (80) | language-rules-agent (context managers) |
| parser.py:41 | `Cache.get` unpacks `(value, ts)` but discards `ts` - TTL is never checked despite being constructed with one. Either honor the TTL or remove it. | Must Fix (80) | code-smells-agent (Dim 1 naming mismatch: name promises cache semantics but TTL is dead) |
| parser.py:14-15 | `for k, v in data.items(): tags.append(k)` discards `v`. Use `tags.extend(data.keys())` or `tags.extend(data)`. Plus the mutating-default problem above means this corrupts the shared `tags` list. | Should Fix (50) | code-smells-agent + simplify-agent |

## May-find

- `data["items"]` raises `KeyError` if missing; the function silently returns whatever `data` had before the lookup, but here it would propagate as exception. Consider `data.get("items", [])`.
- `log.info(msg)` with pre-formatted message defeats lazy logging. Use `log.info("loaded %s items with opts=%s", len(data), opts)`.

## Verdict

REQUEST CHANGES.
