# Expectations: 09-simplify-reuse

Agent 6 (simplify-agent) primary; some overlap with Agent 4
(STL algorithms rule).

## Must-find

| File:Line | Rule | Severity | Detection by |
|-----------|------|----------|--------------|
| csv_loader.cpp:26-33 | `count_non_empty`: manual loop reimplements `std::count_if`. `return static_cast<std::int32_t>(std::count_if(rows.begin(), rows.end(), [](const auto& r){ return !r.empty(); }));`. Also: `rows[i].size() > 0` -> `!rows[i].empty()`. Also: `count = count + 1` -> `++count`. | Should Fix (50) | simplify-agent + language-rules-agent (STL algorithms) |
| csv_loader.cpp:36-47 | `uppercase_all`: manual loop reimplements `std::transform` over rows + `std::transform` over chars. Suggest `std::ranges::transform` + `std::toupper` (with `static_cast<unsigned char>` to avoid UB). | Should Fix (50) | simplify-agent + language-rules-agent |
| csv_loader.cpp:50-57 | `contains`: manual loop reimplements `std::find` / `std::ranges::find`. `return std::find(rows.begin(), rows.end(), needle) != rows.end();` or in C++23 `std::ranges::contains`. | Should Fix (50) | simplify-agent + language-rules-agent |
| csv_loader.cpp:11-24 | `split_line`: O(N^2) string growth via `current += line[i]` (no `reserve`); also reinvents tokenization. Use `std::ranges::views::split(',') | std::ranges::to<std::vector<std::string>>()` (C++23) or `std::string_view`-based split for hot use. Reserve `current` to avoid repeated re-alloc. | Should Fix (50) | simplify-agent + performance-agent (Dim 1 container growth) |
| csv_loader.cpp:13-22, 27-31, 37-44, 50-55 | All four functions use `for (std::size_t i = 0; i < v.size(); i++) ... v[i]` instead of range-for. `for (const auto& r : rows)`. | Should Fix (50) | simplify-agent |

## May-find

- `r[j] >= 'a' && r[j] <= 'z'` assumes ASCII; locale-dependent in
  principle. Use `std::toupper(static_cast<unsigned char>(r[j]))`.
- `out.push_back(current)` in `split_line` could use `emplace_back(std::move(current))` then reset, avoiding the copy.

## Verdict

REQUEST CHANGES (none individually critical, but four simplify
issues + an O(N^2) growth in `split_line` together warrant a fix
pass).
