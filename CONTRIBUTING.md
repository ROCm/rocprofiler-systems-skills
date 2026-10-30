# Contributing to rocprofiler-systems-skills

Radisha (`rocprofiler-systems-skills`) is a library of AI skills. Contributions
are new skills, fixes to existing skills, and documentation. File an issue when
something is missing or wrong, or open a pull request that closes the gap.

---

> **Security vulnerabilities** — do not open a public GitHub issue. See
> [SECURITY.md](SECURITY.md).

---

## Developer policies

These policies apply to all activity in this project.

### Governance

This project is covered by the
[ROCm Project Governance](https://github.com/ROCm/ROCm/blob/develop/GOVERNANCE.md),
which also defines the code of conduct.

### Licensing

Code contributions are covered by the [MIT License](LICENSE).

### Communication channels

Issue tracking and code contributions are managed on GitHub:
[ROCm/rocprofiler-systems-skills](https://github.com/ROCm/rocprofiler-systems-skills).

---

## Development workflows

### Issue tracking

Before filing a new issue, search
[existing issues](https://github.com/ROCm/rocprofiler-systems-skills/issues).

- If your issue is already listed, comment with any extra detail.
- When in doubt, file a new issue. Maintainers will mark duplicates.
- Include the skill name, whether you used Claude Code or Cursor, what you asked
  the assistant to do, and what it did instead.
- Check your issue regularly. Maintainers may ask follow-up questions.

### Adding or changing a skill

Skills are flat directories. The directory name is the skill name:

```text
skills/<skill-name>/SKILL.md
```

Examples: `skills/planning-feature/SKILL.md`, `skills/git-commit/SKILL.md`.

Use a category prefix when one fits: `planning-`, `programming-`, `testing-`,
`git-`, `exploration-`, `radisha-`. Standalone utilities (`ask`, `watch`) have
no prefix.

1. Add or edit `skills/<skill-name>/SKILL.md`.
2. Set frontmatter `name` to the directory name and `description` to when the
   skill should run.
3. Write detailed, actionable instructions.
4. Test the skill before committing.
5. If the skill is new or renamed, update this catalog in the same change:
   - `README.md`: category table, detailed section, and directory tree
   - `skills/radisha-help/SKILL.md`: skill list
   - Related skills, when the new skill needs a "when not to use" note
6. Open a pull request.

`radisha-create-skill` is the checklist for a brand-new skill, including
conflict checks against existing skills.

### Style

- Skill files are Markdown: clear headings, numbered steps, and tables where a
  comparison is easier to scan.
- Python helpers follow PEP 8, with type hints on functions. See `programming-python`.
- Do not commit secrets, tokens, passwords, or credentials.

### Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```text
<type>(<scope>): <subject>

<body>

<footer>
```

- Subject: imperative mood, capitalized, no trailing period, at most 50 characters.
- Body: why the change was made, wrapped at 72 characters.
- Footer: issue references (`Fixes #123`) and breaking changes when needed.
- Common types: `feat`, `fix`, `refactor`, `docs`, `test`, `ci`, `chore`.

```text
docs(contributing): align the guide with the README
```

### Pull requests

All contributions go through a pull request. Do not commit directly to protected
branches. Use a feature branch, and keep each change focused.

Before submitting:

- The change addresses an existing issue or a clear gap.
- You tested the skill, or ran the relevant Python tests when you changed a helper script.
- New or renamed skills update `README.md` and `skills/radisha-help/SKILL.md`.
- Required GitHub Actions checks pass, including the pull-request security scan.

The pull request description must include:

1. **Motivation** — why the change is needed.
2. **Technical Details** — what changed and how.
3. **Test Plan** — how you checked it.

Size:

- Under 400 lines is the target.
- 400–800 lines is acceptable for a change that cannot be split cleanly.
- Over 800 lines must be split.

A pull request needs approval from the CODEOWNERS in `.github/CODEOWNERS`
(`@ROCm/rocprof-sys`) and green required status checks.

### Testing

- Exercise a changed skill with the assistant before you open the pull request.
  Confirm it triggers on the cases in its description and stays out of the cases
  it should not handle.
- Python helpers have tests next to the script (for example
  `skills/therock-first-build-with-commit/test_find_first_build.py`). Run those
  tests when you change the script.
- Documentation-only edits do not need a new test suite. Say in the Test Plan
  what you read and compared.

### Security requirements

Contributors must not:

- Commit secrets, tokens, passwords, or credentials.
- Introduce vulnerable dependencies without justification.
- Bypass security controls or required security reviews.

Pull requests are scanned by `.github/workflows/pr-security-scan.yml`.
