---
name: planning-a-large-project
description: Use when a substantial project needs a researched, phased plan that can survive multiple sessions, when an existing project ledger needs replanning after requirements or dependencies change, or when an existing ledger must move out of a code branch.
---

# Planning a large project

Prepare a ledger that another session can execute without conversation history. Planning fixes the
evidence, task boundaries and sequence; execution follows `executing-a-large-project`.

## Start or resume

1. Read the [contract](references/contract.md). For an existing ledger, read its `STATE.md` first and keep
   its progress.
2. For a new ledger in a git project, read [storage](references/storage.md) and create the ledger on its own
   orphan branch: `python3 -B <skill dir>/scripts/ledger.py init --name <name> --code <repo> --objective "<outcome>"`,
   where `<skill dir>` is this skill's directory. Ask the user before adding `--install-hooks`, because it
   writes into the repository's hooks. Outside git, use `--profile directory --path <dir>`.
3. Record the requested outcome, exclusions and existing authorization in PROTOCOL. Ask only about decisions
   that change scope or correctness; record assumptions and blocked work.

Analyze, build and test code only in the code worktree. Write ledger files only in the ledger directory.

## Preparation gates

`init` creates task PREP-01 with one step per gate; work through it like any other task.

| Gate | Complete when |
| --- | --- |
| Baseline | Actual artifacts, environment, dependencies and baseline checks are recorded; inherited failures are separate. |
| Study | Correctness-sensitive requirements have authoritative sources; conflicts and unavailable evidence have stated consequences. |
| Design | Reuse candidates have dispositions; outputs, owners, interfaces and acceptance methods are defined. |
| Decompose | Each task has a contract copied from `assets/templates/task.md` and an index row with dependencies and a successor. |
| Readiness | The first task can start, later uncertainty has gated tasks, and STATE alone leads a fresh session to it. |

Detail only the tasks that can start next. Distant work gets an expansion task whose output is the next batch
of task contracts. Choose phases by deliverable, not by a fixed count. For domain-governed work, read
[specialization](references/specialization.md).

Bulk-generated facts (inventories, mappings, classifications) carry `basis` and `verified_by` columns. An
inferred value is a hypothesis: the task that consumes it verifies it first.

## Finish planning

1. Run `ledger.py validate --ledger <ledger>` until it reports no errors.
2. Read STATE as a fresh session would: it must name one next action and the files needed for it.
3. Write the planning checkpoint, update the index, then write STATE last with lifecycle `ready`.
4. If execution was also requested, continue with `executing-a-large-project`; otherwise report the ledger
   path and its next action.

## Common mistakes

- Several next actions in STATE: STATE holds one cursor, and the index holds the queue.
- A dependency recorded as "available" without checking it: verify it against the actual system first.
- Copying a sibling task's contract: step IDs must start with the task's own ID, and `validate` rejects them otherwise.
