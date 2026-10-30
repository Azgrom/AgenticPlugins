# Recovery and session handoff

Read when resuming after an interruption, when STATE disagrees with the task record or the artifacts, for a
legacy ledger, or before ending a session.

## Reconcile before continuing

Start from STATE, PROTOCOL, the active task and its latest checkpoints. Inspect the actual artifacts. In git,
run `ledger.py sync` and compare its `code:` line with STATE's and the checkpoint's; a commit subject or a
branch name does not establish completion. Outside git, use the revision, checksum or receipt method in
PROTOCOL. Record what is observed, unknown and contradicted. An older check result still applies only if its
inputs and outputs are demonstrably unchanged; otherwise rerun it.

| Observation | Action |
| --- | --- |
| STATE and artifacts agree | Resume the named step after checking its entry conditions. |
| Output exists but no accepted checkpoint | Keep the output; run the missing checks and the review. |
| A checkpoint newer than STATE | Validate it against the artifacts, then repair the index and STATE; do not redo accepted work. |
| STATE says done but the checkpoint is missing or incomplete | Reopen the review, recover or rerun the checks, and write a correction checkpoint. |
| Artifacts changed after acceptance | Reopen the affected checks and dependents; keep the earlier checkpoints. |
| A handoff disagrees with the ledger | Trust artifacts and checkpoints; a handoff adds no authority. |
| A child ledger or required file is missing | Recover it from durable storage, or block the dependent work. |
| An operation's effect is unknown | Inspect its ID, service state and outputs before resuming, waiting or retrying. |
| `validate` reports `state.contract` (legacy) | Follow the contract's legacy section; never rewrite history. |

An uncommitted workspace is not a blocker by itself: establish who owns the changes and whether the task
allows them. Stop for the user only for a material conflict, a missing decision or an authorization boundary,
and record the blocker with its release condition.

## Long operations

Before an operation that can outlive the session, save its intent, inputs, output location, task and step,
and whether it is safe to repeat. Once it is launched, save its job or process ID and its log path. A launch,
a partial file or a disconnection is not success. At session end, record the operation's last observed status
and time, its completion signal, and the first check for the next session. Never restart an operation with
unknown effects just because the old session ended; if its status cannot be observed, block the dependent work.

## Persist, then hand off

Follow the write order: evidence, task record, checkpoint, index, STATE last. Run `validate`, then read back
STATE and the checkpoint it names, and confirm that the files on `read:` exist.

A handoff message, or an optional `HANDOFF.md` pointing to STATE, contains only: the ledger location and
branch, the checkpoint and whether it is accepted or a recovery, the current task and step, one next action,
and any pending checks, approvals or operations. Every fact in it must already be in the ledger. Never claim
that another session started without observing it. Keep credentials out of the ledger and out of handoffs.
