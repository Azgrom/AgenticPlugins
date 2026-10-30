---
name: executing-a-large-project
description: Use when continuing a substantial project with an existing phased backlog, resuming interrupted work from STATE.md, or handing a project task to another session.
---

# Executing a large project

Advance one verified task boundary at a time.

## Start every session

1. Read the backlog's `STATE.md`. If several candidates exist, establish the authoritative one first. If no
   backlog exists, use `planning-a-large-project`.
2. Read the [contract](../planning-a-large-project/references/contract.md), then the files on STATE's `read:`
   line. Read anything else only when the active task links it. Query the index and bulk tables with
   `backlog.py query` instead of opening them.
3. Run `python3 -B <tool> validate --backlog <backlog>`, where `<tool>` is the path on PROTOCOL's `authority:`
   line, and also `doctor` when storage is `orphan-worktree`. Reconcile STATE, the task record and the actual
   artifacts before changing anything. Follow [recovery](references/recovery.md) when they disagree, after an
   interruption, or for a legacy backlog.

Run code analysis, builds and tests in the code worktree named on STATE's `code:` line. Write backlog files
only in the backlog directory. Never stage backlog files in the code worktree.

## Execute the task

| Point | Required action |
| --- | --- |
| Entry | Confirm predecessor acceptance, inputs, baseline and permissions; save `in_progress` in the index and STATE. |
| Work | Follow the ordered steps and domain requirements; check off steps and record operation IDs as work happens. |
| Review | Compare the actual outputs with the task's exit, its checks, its scope and the successor's entry conditions. |
| Acceptance | Apply PROTOCOL's stop classes, write the checkpoint, update the index, then write STATE last. |

At every task boundary:

1. Record check results bound to the outputs being accepted; a result from before the last edit does not count.
2. For Git code, run `backlog.py sync --backlog <backlog> --write`; add `--pin <task>` at acceptance.
   Otherwise record PROTOCOL's artifact revision, checksum or receipt.
3. Write the checkpoint from `assets/templates/checkpoint.md`, and quote any human approval verbatim. When a
   stop class requires a human, the task stays `awaiting_acceptance` and work on it waits for the user's answer.
4. Update the index, then STATE, then run `validate` and fix every error.

Failed checks keep the task in `review` or `blocked`. After acceptance, check the successor's entry conditions
and continue within PROTOCOL's authorization and session rule. If a contract is missing or wrong,
reopen planning for that work. Preserve unrelated changes.

## End a session or finish the project

Before context runs short, save a recovery or boundary checkpoint as described in
[recovery](references/recovery.md): the unfinished step, the artifact identity, running operations and the
next action. When every task is accepted, follow the contract's closeout. A session ending is not project
completion.

## Common mistakes

- "The handoff says it is done": check the claim against artifacts and checkpoints first.
- Opening a large evidence file to find one row: use `backlog.py query --csv <file> --where <column>=<value>`.
