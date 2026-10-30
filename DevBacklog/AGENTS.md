# DevBacklog: package maintenance

These guidelines apply to `DevBacklog/` and its descendants. The paths below are
relative to this package root.

## Structure and dependencies

- `plugin.json` contains portable metadata; `.codex-plugin/plugin.json` contains
  skill discovery and the Codex interface. Keep identity, version, and
  presentation consistent across both files.
- The three skills in `skills/` are distributed together.
  `planning-a-large-project` provides the contract, templates, and `scripts/backlog.py`;
  `executing-a-large-project` and `reviewing-and-planning-tests` depend on them.
  Preserve the relative paths between these skills.
- Keep imported skills, references, and templates in English. Changes to package
  documentation must preserve commands and skill names exactly.
- Keep distributed copies self-contained. Personal installations in
  `~/.agents/skills` or `~/.codex/skills` are not package dependencies.

## Context by change

| Change | Reading |
| --- | --- |
| Backlog contract, templates, or CLI | [Contract](skills/planning-a-large-project/references/contract.md) and [storage](skills/planning-a-large-project/references/storage.md) |
| Execution resumption and recovery | [Execution skill](skills/executing-a-large-project/SKILL.md) and [recovery](skills/executing-a-large-project/references/recovery.md) |
| Test review and planning | [Review skill](skills/reviewing-and-planning-tests/SKILL.md) and the relevant references linked within it |
| Manifests and distribution | [README.md](README.md) and `scripts/validate_package.py` |

Skill workflows are product content. Incorporating or editing these files does
not initialize a backlog or install hooks in the publishing repository.

## Verification

Run from this package root, using Python 3.10 or later and Git 2.42 or later:

```sh
python3 -B scripts/validate_package.py
python3 -B -m unittest discover -s skills/planning-a-large-project/scripts/tests -p 'test*.py'
git diff --check
```

The validator checks structure, manifest consistency, supporting files, and local
documentation links. The tests exercise the CLI, contracts, worktrees, and hooks
in temporary repositories. Templates contain references to generated backlog
files; the CLI tests exercise the resolution of those references.

These checks do not run the skills in a model or establish that the host can
discover them. When changing instructions, keep a separate record of the
conversational scenarios exercised, their outputs, and the cases not run.
