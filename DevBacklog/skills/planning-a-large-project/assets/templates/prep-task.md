# PREP-01 — Prepare the plan

Loaded when: executing or reviewing PREP-01. Up: [STATE](../STATE.md)

outcome: PLAN, PROTOCOL, task contracts and index ready for the first executable task
requirements: none
entry: the user's request, recorded under PROTOCOL's authorization
owns: STATE.md, PLAN.md, PROTOCOL.md, tasks/, research/, evidence/, checkpoints/
excludes: project artifacts outside the ledger
context: planning-a-large-project SKILL.md — preparation gates
checks: python3 -B <<TOOL>> validate --ledger . → 0 errors
exit: checkpoint checkpoints/PREP-01.md; successor none

## Steps

- [ ] PREP-01.1 Baseline — done when artifacts, environment, dependencies and baseline checks are recorded
- [ ] PREP-01.2 Study — done when correctness-sensitive requirements have sources and conflicts have consequences
- [ ] PREP-01.3 Design — done when reuse dispositions, outputs, owners and acceptance methods are recorded
- [ ] PREP-01.4 Decompose — done when every task has a contract and an index row with dependencies and successor
- [ ] PREP-01.5 Readiness — done when validate passes, STATE alone leads to the first task, and the checkpoint is written

## Record

not started
