# Test-review backlog output

Read when recording findings, decomposing remediation or checking readiness. The planner's contract owns the
file structure, templates and acceptance format; this reference adds the test-specific records and policy.

## Records

Keep one owner per fact; reports link to records instead of copying them.

| Record | Content |
| --- | --- |
| `research/inventory.md` | Every project: manifest or build identity, purpose, dependencies, owner, test roots, discovery and configurations |
| `research/projects/<project>.md` | Existing structure and evidence, obligations, interface findings, priorities and limits, linking the project's rows below |
| `evidence/tests.csv` | One row per existing test: `project, file, line, test, runner, scope, obligation, category, destination, disposition, task, basis, verified_by` |
| `research/obligations.csv` | One row per obligation: `id, project, source, domain, oracle, strength, cases, task, basis, verified_by` |
| `research/coverage.md` | Tool and version, configuration, denominator, statement and branch results, exclusions and unmeasured parts |

The judgment columns of `evidence/tests.csv` stay empty until the project's audit task fills them with
`basis` `read`. Read a project's rows with `backlog.py query --csv evidence/tests.csv --where project=<name>`.

A finding names the contract or circumstance, the observation or absence, the user impact, the project and
surface, the remedy and owner, and the check that would discharge it. Keep these apart: an actual failing
test, a missing assertion, an unsupported claim and an unreviewed surface. A plan is not evidence that its
tests exist.

## Phases and tasks

Each project owns a phase, including projects that need no change. Providers come before consumers. Shared
harness work has one owning project. An integration task belongs to the consuming project and names its
provider gates. Resolve a dependency cycle with a bounded contract or research task.

Order each project's tasks: the audit (which fills the judgment columns and confirms obligations), then the
moves, then new evidence. One independently reviewable result is one task, and commands and assertions are
its steps. Do not merge several reviewable migrations into one task to save stops.

A task names:
- its finding and obligation IDs;
- its owned files and registration;
- its entry gates: child contracts, source versions, tools, oracle provenance, permissions;
- the exact cases, or a link to them;
- the actual repository commands, with working directory and expected result;
- its successor.

When a command or oracle is unknown, the first task discovers and validates it. A production defect found
while adding tests stays a finding until a repair is authorized; never weaken a test to get a passing result.

## Acceptance policy

Write this stop class once in PROTOCOL; tasks do not repeat it:

`- review: every remediation task → stop for human acceptance`

After verification, the executor saves the checkpoint with `acceptance: pending`, sets the task to
`awaiting_acceptance`, makes obtaining acceptance STATE's next action, and stops before the successor. Only
the user's own words, quoted in the checkpoint, accept the task. Changed outputs reopen verification and
acceptance. If the user later changes this policy, record the instruction and its scope under PROTOCOL's
`user instructions:` and add a matching stop class.

## Readiness and closeout

Before marking the backlog ready, check both directions:
- every finding and obligation has an owning task and check;
- every task has inputs, permissions, owned outputs, checks and a successor.

Every project has its report and phase. Categories and registration are concrete. Dependency restrictions and
coverage limits appear in the task files. At closeout, require accepted phase evidence, preserved regressions,
registered tests, declared coverage results and a final obligation review, not merely completed checkboxes.
