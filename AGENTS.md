# SolverPy Monorepo Agent Guide

This repository contains three Python packages:

| Package | Source root | Purpose |
|---|---|---|
| `solverpy` | `packages/solverpy/src/solverpy/` | Core solver API, plugins, evaluation, database, reporting |
| `solverpy-learn` | `packages/solverpy-learn/src/solverpy_learn/` | ML builders, tuning, training data, iterative learning loops |
| `solverpy-grackle` | `packages/solverpy-grackle/src/solverpy_grackle/` | Grackle configuration portfolio optimization |

## Read Project Guidance

Before changing code, read the guidance relevant to the task:

- Root [`CLAUDE.md`](CLAUDE.md) for repository architecture and conventions.
- [`TODO.md`](TODO.md) and [`DONE.md`](DONE.md) for current and completed work.
- [`COMMITS.md`](COMMITS.md) for commit-message structure.
- [`BUILD.md`](BUILD.md) for package and documentation commands.
- [`talkers.md`](talkers.md) for talker lifecycle methods and call sites.
- [`packages/solverpy-grackle/CLAUDE.md`](packages/solverpy-grackle/CLAUDE.md)
  and its `TODO.md` when working on Grackle.

Some older documentation contains stale names or architecture. When documents
conflict, prefer package-specific guidance, newer lifecycle notes, current tests,
and the current source code. Verify assumptions against the implementation.

## Development Environment

The active packages in user site-packages are symlinks into this checkout:

- `solverpy` -> `packages/solverpy/src/solverpy`
- `solverpy_learn` -> `packages/solverpy-learn/src/solverpy_learn`
- `solverpy_grackle` -> `packages/solverpy-grackle/src/solverpy_grackle`

Source edits are immediately active. Do not reinstall packages after changes.

## Code And Testing

- Use 3-space indentation and the repository's YAPF/PEP8 style.
- Prefer single expressive words for function, method, and variable names.
  Avoid underscores merely to connect phrase words. Use underscores mainly for
  stable common prefixes that group related operations, with the shared subject
  first, such as `model_build`, `model_prepare`, `chunk_path`, `chunk_files`,
  `raw_path`, and `raw_files`. Prefer this grouped-prefix style over mixed
  verb-first phrases such as `build_model` and `prepare_model`.
- Follow existing module, type-annotation, setup, plugin, and talker patterns.
- Keep changes scoped and preserve unrelated working-tree changes.
- Run focused `pytest` tests for changed behavior, broadening according to risk.
- Use `pytest`, not `python -m pytest`.
- Slow, learning, and Grackle tests are excluded by default through root pytest
  configuration; run them explicitly when the task requires them.
- `SOLVERPY_DB` should remain relative for ENIGMA/eprover workflows.
- Preserve the intentional multiprocessing context split: normal evaluation
  uses `forkserver`, ATP evaluation inside tuning
  uses `spawn`, and selected data-loading/compression paths use `fork`.

For documentation work, follow the mkdocs/mkdocstrings conventions in the
repository and inspect `.claude/skills/document-code/SKILL.md`.

## Grackle Rules

- New or updated Grackle runners must use `solverpy`; follow the current
  `SolverPyRunner`-based implementations.
- New or updated parameter domains must subclass `GrackleDomain` or
  `CustomDomain`.
- Consult the Grackle package's `CLAUDE.md` and `TODO.md`; parts of its older
  README and root guidance describe pre-migration architecture.

## Commits And Versioning

Use Conventional Commit-style subjects:

```text
<type>[optional scope]: <description>
```

Match recent repository history: use a concise subject and an explanatory body
for non-trivial changes. When an AI assistant materially authors a commit, add
the appropriate `Co-Authored-By` trailer for the assistant that actually did the
work. Do not falsely attribute work to Claude or another assistant.

This repository uses a custom exclamation-mark version policy, not standard
Conventional Commits SemVer behavior:

- `type:` creates no version tag.
- `type!:` bumps PATCH.
- `type!!:` bumps MINOR.
- `type!!!:` bumps MAJOR.

Never introduce `!`, `!!`, or `!!!` in a commit type without explicit agreement
from the user for that specific version bump.

The active `.git/hooks/post-commit` hook:

1. Regenerates `CHANGELOG.md`.
2. Amends the new commit to include it.
3. Creates version tags when the commit type contains agreed exclamation marks.

Therefore:

- Never edit `CHANGELOG.md` or version tags manually.
- Expect the commit hash printed by the initial `git commit` to change after the
  hook amends it.
- Inspect the final `HEAD` before reporting or pushing.
- Do not commit or push unless the user asks.

## Working Tree

Generated or experiment files may be present. Do not add, remove, or modify
unrelated files. In particular, treat existing untracked files under `scripts/`
and files such as `talkers.html` as user-owned unless the task explicitly
targets them.
