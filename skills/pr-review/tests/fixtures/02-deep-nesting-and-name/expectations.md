# Expectations: 02-deep-nesting-and-name

## Must-find

| File:Line | Rule | Severity | Detection by |
|-----------|------|----------|--------------|
| request_router.cpp:8 | Dim 1 - "and"/"or" in name: `parse_and_validate_and_dispatch()` does three things. Propose split: `parse_body_or_400()`, `validate_or_401()`, `route_or_404()`, then a 6-line orchestrator. | Must Fix (80) | code-smells-agent (QUALITY.md Dim 1 weak verb + Dim 3 multi-responsibility) |
| request_router.cpp:8-49 | Dim 2 - nesting depth 7 (>>4 hard limit) | Must Fix (80) | code-smells-agent (QUALITY.md Dim 2) |
| request_router.cpp:8-49 | Dim 2 - function length 42 lines past the hard 40-line Should-Fix limit; with the depth hit, elevate to Must Fix | Must Fix (80) | code-smells-agent (QUALITY.md Dim 2) |
| request_router.cpp:8-49 | Dim 3 - three or more SRP symptoms: phase-shaped body, three disjoint subsystems (parse / validate / route), "and" in name. Pair with the named-split proposal above. | Must Fix (80) | code-smells-agent (QUALITY.md Dim 3) |
| request_router.cpp:13 | Dim 4 - magic number `1024` (body size limit). Replace with `constexpr std::size_t MAX_BODY_BYTES = 1024;`. | Should Fix (50) | code-smells-agent (QUALITY.md Dim 4) |
| request_router.cpp:14,25 | Dim 4 - magic strings `"POST"` / `"GET"` used as branch keys. Replace with named constants or an enum. | Should Fix (50) | code-smells-agent (QUALITY.md Dim 4) |
| request_router.cpp:* | Status codes `404`, `400`, `405`, `413`, `401` are magic numbers. Replace with `kStatusNotFound` etc. | Should Fix (50) | code-smells-agent (QUALITY.md Dim 4) |
| request_router.cpp:* | Flow-clarity: arrow shape, no guard clauses, no early return. Suggest `if (!req.is_well_formed()) return Response{400};` pattern. | Should Fix (50) | code-smells-agent (QUALITY.md Dim 2 flow-clarity) |

## May-find

- Hot path (request dispatch matches the `dispatch_*` name pattern):
  Agent 7 should classify `hot` and bump severities.
- `req.method() == "POST"` repeated string comparison in hot path.

## Verdict

REQUEST CHANGES.
