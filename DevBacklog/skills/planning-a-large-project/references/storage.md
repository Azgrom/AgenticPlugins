# Ledger storage

Read when creating a ledger, moving one, or when `ledger.py doctor` reports a problem.

## Profiles

| Profile | Use | Location |
| --- | --- | --- |
| `orphan-worktree` | Default for git projects | Branch `ledger/<name>` in its own worktree, by default `<repo parent>/ledger-<name>` |
| `directory` | Projects without git, or when the user declines separation | Any directory |
| `external` | A tracker or document system holds the ledger | Recorded in STATE |

An orphan branch shares no history with code, so git refuses to merge it into a code branch. No code
checkout ever contains a ledger file, which means searches, scripts and commits on the code side cannot
reach it.

## Create

`python3 -B <skill dir>/scripts/ledger.py init --name <name> --code <repo> [--path <dir>] --objective "<outcome>"`

It runs `git worktree add --orphan -b ledger/<name> <dir>`, writes the templates, adds `/.ledger/` to the
repository's `info/exclude`, and validates the result. It never commits. It requires git 2.42 or newer.

## Work in two places

- Analyze, build and test code in the code worktree named on STATE's `code:` line.
- Write ledger files only in the ledger worktree. Commit them on the ledger branch when PROTOCOL's `delivery:`
  line allows it.
- Updates flow one way, from code to ledger. `ledger.py sync --ledger <ledger> --write` records the code
  branch, commit, uncommitted-change hash and time in STATE. Nothing is merged in either direction.
- At acceptance, `sync --pin <task>` creates `refs/ledger/<name>/<task>` at the accepted commit, so rebasing
  the code branch cannot lose it. `git push`, `--all` and `--tags` never send `refs/ledger/*`.

## Guards

With the user's approval, `init --install-hooks` installs two hooks that every worktree of the repository
shares. It refuses to replace a hook it did not write.
An existing `core.hooksPath` must be absolute so every worktree uses the same hooks.

- `pre-commit` rejects added or modified `.ledger/` paths on branches outside `ledger/*`, and Python bytecode
  on every branch. Deleting old ledger files is still allowed.
- `pre-push` rejects pushing `ledger/*` branches or `refs/ledger/*` to any remote other than the private one
  named in `git config ledger.allowedRemote`. It also rejects any pushed commit that touches `.ledger/`.

A commit that already carries ledger files stays blocked from pushing until its history is rewritten;
deleting the files in a new commit does not remove them from history. Agents never pass `--no-verify`.

`ledger.py doctor --ledger <ledger>` reports an error when:
- the ledger branch shares history with code;
- the code branch tracks `.ledger/` paths;
- a `.ledger/` directory exists in the code worktree;
- the ledger contains bytecode.

It warns about other branches that track ledger paths, and about missing hooks or exclude entries.

## Move an in-tree ledger

With the user's approval:

1. Run `init` for a new orphan ledger.
2. Copy the old ledger's files into the new worktree and map them as a legacy ledger (see the contract).
3. Commit them on the ledger branch.
4. The user removes `.ledger/` from code branches in an ordinary commit, and rewrites history before pushing
   any branch whose commits added ledger files.
