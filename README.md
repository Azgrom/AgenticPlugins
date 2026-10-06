# Tutor

Tutor is an instruction-based AI tutoring plugin for exam preparation and academic
study. This repository contains its modular instructions, plugin metadata,
structured record contracts, and evaluation material. It is intended for
contributors, reviewers, and developers inspecting or adapting the tutor.

The tutoring instructions are primarily written in Brazilian Portuguese. They
cover conceptual explanations, question analysis, written and practical
assessments, critical reading, and research guidance at undergraduate, master's,
and doctoral levels. ENEM, public examinations, and professional certifications
have dedicated profiles; academic tutoring also works outside an exam context.

## Architecture

The package exposes one skill, [instructions](skills/instructions/SKILL.md). Its
entry point routes requests to focused reference modules:

1. [CORE](skills/instructions/references/CORE.md) defines the shared mission,
   precedence rules, and factual and operational constraints.
2. Operational policies and knowledge modules supply the guidance needed for the
   specific request. They are loaded conditionally to keep unrelated material out
   of the active context.
3. JSON schemas define optional records for evidence, assessments, student state,
   checkpoints, and academic reviews. Fixtures and Python checks exercise these
   contracts separately from the tutor's conversational behavior.

The [knowledge index](skills/instructions/lookup/knowledge-index.json) records
reference paths and their loading conditions. The legacy ZIP is retained as an
inactive artifact; the extracted Markdown modules contain the active guidance.

This repository does not provide a standalone application, model runtime,
database, or tool backend. Model execution, external-source access, memory, and
other capabilities depend on the host. The schemas alone do not implement
persistence, and local validation does not establish host compatibility.

## Repository layout

| Location | Responsibility |
| --- | --- |
| [plugin.json](plugin.json) | Plugin identity and OpenAI interface metadata |
| [.codex-plugin/plugin.json](.codex-plugin/plugin.json) | Codex plugin manifest and skill discovery |
| [skills/instructions/SKILL.md](skills/instructions/SKILL.md) | Skill entry point and conditional routing |
| [agents/openai.yaml](skills/instructions/agents/openai.yaml) | Skill presentation metadata |
| [references/operations](skills/instructions/references/operations/) | Evidence, context, state, tools, and response policies |
| [references/knowledge](skills/instructions/references/knowledge/) | Teaching methods, research guidance, curricula, and exam profiles |
| [references/schemas](skills/instructions/references/schemas/) | JSON schemas and record-contract documentation |
| [references/evals](skills/instructions/references/evals/) | Acceptance criteria, behavioral cases, and synthetic fixtures |
| [scripts](skills/instructions/scripts/) | Offline package validation and academic contract tests |

## Design constraints

- **Direct, on-demand tutoring.** A clear question should receive an answer without
  mandatory onboarding, profiling, or an unsolicited study plan.
- **Explicit provenance.** Official questions, published samples, licensed
  practice, authored exercises, and user-provided material have distinct origins.
  Generated practice must not be represented as a historical exam question.
- **Evidence proportional to the claim.** Bibliographic metadata, inspected text,
  and support for a conclusion are separate checks. Research guidance must retain
  uncertainty and disclose limits of source access.
- **Context-specific assessment.** Exam rules, scoring systems, and student
  records remain tied to their relevant context. Internal teaching defaults are
  not official scoring rules.
- **Optional records.** Tutoring does not require a parallel student database.
  Structured history and checkpoints are used only when explicitly requested.

The authoritative details live in CORE and the policy modules linked by the skill
entry point.

## Local validation

The validation scripts use Python 3 and its standard library. From the repository
root, run:

```sh
python3 -B skills/instructions/scripts/validate_package.py
python3 -B -m unittest discover -s skills/instructions/scripts -p 'test*.py'
git diff --check
```

The package validator checks Markdown references, the knowledge index, manifest
constraints, schemas, fixtures, and record integrity. Its schema validator supports
only the explicitly implemented JSON Schema keywords; it is not a general Draft
2020-12 implementation. The unit tests exercise the academic review contract,
including source resolution, access levels, and unsupported conclusions.

Structural checks, behavioral evaluation, and host activation are separate forms
of verification. The Python scripts do not run a tutor model or execute the
behavioral cases. For those, follow the
[acceptance criteria](skills/instructions/references/evals/acceptance_tests.md)
and [evaluation protocol](skills/instructions/references/evals/evaluation_protocol.md),
capture actual responses, and report unexecuted cases as `NOT_RUN` or `BLOCKED`.
Fixtures are synthetic test material, not authenticated exam content or research
evidence.

## Contributing

Start with [AGENTS.md](AGENTS.md) for repository editing and verification guidance.
For behavior changes, read the skill entry point, CORE, and the affected modules.
Keep detailed policy in its owning module and update routing links and the
knowledge index when adding, moving, or removing references.

Schema changes should include aligned fixtures and validator coverage for both
accepted and rejected records. Metadata changes should account for both plugin
manifests and the skill presentation metadata. Preserve the Portuguese language
of tutor-facing instructions and keep identity or branding changes scoped to the
intended contribution.

In a pull request, explain the behavior or contract being changed, list the checks
and relevant behavioral cases actually executed, and distinguish existing failures
from regressions. Report host activation separately when it has been tested.

## License

[MIT](LICENSE).
