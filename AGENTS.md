# Repository guidance

## Scope

Tutor is a portable tutoring plugin: Markdown instructions, JSON contracts and
fixtures, and Python validation scripts. Treat repository maintenance separately
from activating the tutor. Preserve the Portuguese language of tutor-facing
instructions and the existing language of code and identifiers.

## Read before changing

- For tutor behavior or routing, read `skills/instructions/SKILL.md` and
  `skills/instructions/references/CORE.md`, then only the modules relevant to the
  change. CORE defines the tutor's invariants; keep detailed policy in its owning
  module rather than duplicating it in the entry point.
- For module additions, moves, or removals, update the applicable routing links
  and `skills/instructions/lookup/knowledge-index.json`. Entry-point and index
  paths resolve from the skill root; links inside reference modules resolve from
  the containing file.
- For record changes, consult the relevant documentation in
  `skills/instructions/references/schemas/` and keep schemas, fixtures, and
  validator checks aligned. Schemas describe contracts, not an implemented
  persistence service.
- For tutor changes and release validation, read
  `skills/instructions/references/evals/acceptance_tests.md`. When executing
  behavioral cases, also read `evaluation_protocol.md` in that directory.

## Editing constraints

- Preserve direct, on-demand tutoring, including academic help outside exams.
  ENEM is an explicit specialization, not the assumed context of every request.
- Keep factual provenance, source-access limits, and optional student records
  consistent with CORE and the relevant policy modules.
- Treat `skills/instructions/references/instructions.zip` as a legacy artifact;
  active instructions belong in the extracted Markdown modules. Do not add it to
  active routing or unpack it for routine context gathering.
- Packaging has two distinct manifests: `plugin.json` and
  `.codex-plugin/plugin.json`; skill presentation also lives in
  `skills/instructions/agents/openai.yaml`. Inspect all relevant surfaces for
  metadata changes, preserving their different structures. Change identity,
  author details, prompts, assets, and versions only within the requested scope.
- The Python validator uses the standard library and supports an explicit subset
  of JSON Schema keywords. A new schema keyword requires corresponding validator
  support and meaningful acceptance/rejection coverage.

## Verification

Run these commands from the repository root:

```sh
python3 -B skills/instructions/scripts/validate_package.py
python3 -B -m unittest discover -s skills/instructions/scripts -p 'test*.py'
git diff --check
```

Report failures as observed, distinguishing existing failures from regressions.
The package validator checks packaging constraints as well as contracts, including
manifest text limits and the package directory name. Inspect the failing assertion
before changing metadata or weakening a check.

Offline checks do not execute the tutor's behavioral cases or verify host
activation. For behavior changes, execute the relevant P0 cases using the
evaluation protocol and record actual outputs; label unexecuted cases NOT_RUN or
BLOCKED. Keep structural checks, behavioral evaluation, and host activation
results separate in completion reports.
