# Ledger contract — version 3

Read after STATE at the start of every session; the planning, executing and reviewing skills share it.
`scripts/ledger.py` in this skill checks the mechanical rules. Run it as
`python3 -B <skill dir>/scripts/ledger.py <command> --ledger <ledger>`.

## Files and owners

Each fact has one owner; no file copies another file's facts.

| File | Owns | Read |
| --- | --- | --- |
| `STATE.md` | Where work stands and the one next action | First, every session |
| `PROTOCOL.md` | Authority, storage, authorization, delivery, stop classes, check profiles, session rules, user instructions | Before acting |
| `PLAN.md` | Outcome, exclusions, requirements, phases | When selecting work or replanning |
| `tasks/index.json` | Each task's phase, dependencies, status, successor and checkpoint | Through `ledger.py query` |
| `tasks/<ID>.md` | One task's contract, step checkboxes and resume record | For the active task |
| `checkpoints/<ID>.md` | Review, check results and acceptance at one task boundary | Latest for the active task |
| `research/`, `evidence/` | Domain records, bulk tables, check summaries, scripts | When a task or checkpoint links them |

`ledger.py init` writes STATE, PROTOCOL, PLAN, the index and the preparation task from `assets/templates/`.
For new tasks and checkpoints, copy `task.md` and `checkpoint.md` from there. Requirement coverage comes from
each task's `requirements:` line. When PLAN's phase table outgrows its budget, move it to `phases.md`.

## STATE

STATE is the cursor, not a history. It holds exactly these lines, once each:

| Key | Value |
| --- | --- |
| `contract` | `3 sha256:<12 hex>` of this file |
| `ledger` | `<name> — <objective>` |
| `lifecycle` | `planning`, `ready`, `executing`, `blocked`, `complete` or `archived` |
| `storage` | `orphan-worktree ledger/<name> at <path>`, `directory <path>` or `external <where>` |
| `code` | `<path> @ <branch> <sha12> clean` (or `dirty:<hash12>`), `observed <UTC time>`; `none` outside git |
| `plan` | `revision <n>` |
| `cursor` | `<phase> / <task> / <step> — <status>`, using the index's status |
| `accepted` | Latest accepted checkpoint and its date, or `none` |
| `recovery` | Latest recovery checkpoint, or `none` |
| `pending` | A pending decision or approval with its scope and source, or `none` |
| `operations` | Running operations with ID, log path and last observed status, or `none` |
| `next` | One action, with its blocker or release condition |
| `read` | Comma-separated files the next action needs |

## Statuses

| Status | Meaning |
| --- | --- |
| `planned` | Contract exists; entry conditions not established |
| `ready` | Entry conditions hold for the observed inputs |
| `in_progress` | Work started; the unfinished step is recorded |
| `review` | Outputs exist; checks or review incomplete |
| `awaiting_acceptance` | Review passed; an approval or delivery is pending |
| `done` | A checkpoint with acceptance proves the exit and delivery conditions |
| `blocked` | A named condition prevents progress; its release condition is recorded |
| `needs_replan` | An invalidated assumption requires a revised contract |

A task starts after its entry conditions are checked and `in_progress` is saved. It ends only when its
checks, review and delivery condition are recorded in an accepted checkpoint; a checked box or a produced
file is not enough. Step IDs start with the task's ID.

## Checkpoints and acceptance

Write a checkpoint at every task boundary, even within one session. Review the actual result against the
task's scope, its checks, domain constraints, regressions and the successor's entry conditions. Resolve
findings, or keep the task open with an owner and next action. Its `acceptance:` line is one of:

- `pending`;
- `human "<the user's words, verbatim>" (<source>, <date>)`: positive and scoped to this artifact. A refusal,
  a question, silence, green checks or an agent's review is not acceptance;
- `policy <stop class>`: PROTOCOL's stop class lets work continue without a human.

Each stop class in PROTOCOL names a condition, such as the paths a task touches, and whether it stops for a
human; when several match, the one that stops wins. Project-specific rules belong there. Accepted
checkpoints are never edited: a correction is a new checkpoint naming the claim it supersedes.

## Write order

Evidence → task record → checkpoint → index → STATE last; then run `validate` and fix every error. Before a
long or externally visible operation, save its intent and inputs. A recovery checkpoint never advances the
accepted frontier.

## Content rules

- Budgets: STATE 2 KB, PROTOCOL 4 KB, PLAN 8 KB, a task or checkpoint 4 KB, a line 400 characters. STATE,
  PROTOCOL and PLAN never link a file over 16 KB. A task that does says how to read a slice of it, such as
  `ledger.py query --csv <file> --where <column>=<value>`.
- Write a sentence once. Text that several tasks share belongs in PROTOCOL or one linked record.
- A check result is its command, exit code, counts and the sha256 of its full log; keep full logs only for
  failures. Store reproducible data as generator, seed and hash. Never store ledger copies, older versions
  or build output. A file over 1 MB needs a reason in `evidence/large-files.txt`.
- Bulk tables are CSV. Above 20 rows they carry `basis` (`script`, `read`, `executed` or `inferred`) and
  `verified_by`. An `inferred` value is a hypothesis and never drives a change. A value that every row
  would repeat is stated once, outside the table.
- PROTOCOL states policy; a fact about the environment carries `observed: <date or revision>`. Every claim
  in a checkpoint points to evidence that resolves.

## Scale, changes and completion

Replanning keeps completed evidence, invalidates affected dependents, increments the plan revision and
records why. New scope needs the user's authorization. A child ledger is recorded in its parent with its
path, owner, input and output contract, and the parent waits for its accepted checkpoint. One session at
a time writes a ledger's cursor; authorized parallel work splits task ownership and reconciles before
acceptance. At closeout, verify phase and final gates and requirement coverage, move durable decisions
to their maintained homes, and write a closeout checkpoint. Archive by default; delete only on explicit
instruction, after every needed fact has another home.

## Legacy ledgers

`validate` stops with `state.contract` when STATE names another contract version. Keep the files and their
history, map their facts onto this contract, add only the cursor, index or checkpoint needed to resume, and
record the mapping in a checkpoint.
