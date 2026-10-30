# Backlog storage

Read when creating a backlog, moving one, or when `backlog.py doctor` reports a problem.

## Profiles

| Profile | Use | Location |
| --- | --- | --- |
| `orphan-worktree` | Default for git projects | Branch `backlog/<name>` in its own worktree, by default `<repo parent>/backlog-<name>` |
| `directory` | Projects without git, or when the user declines separation | Any directory |
| `external` | A tracker or document system holds the backlog | Recorded in STATE |

An orphan branch shares no history with code, so git refuses to merge it into a code branch. No code
checkout ever contains a backlog file, which means searches, scripts and commits on the code side cannot
reach it.

## Create

`python3 -B <skill dir>/scripts/backlog.py init --name <name> --code <repo> [--path <dir>] --objective "<outcome>"`

It runs `git worktree add --orphan -b backlog/<name> <dir>`, writes the templates, adds `/.backlog/` to the
repository's `info/exclude`, and validates the result. It never commits. It requires git 2.42 or newer.

## Work in two places

- Analyze, build and test code in the code worktree named on STATE's `code:` line.
- Write backlog files only in the backlog worktree. Commit them on the backlog branch when PROTOCOL's `delivery:`
  line allows it.
- Updates flow one way, from code to backlog. `backlog.py sync --backlog <backlog> --write` records the code
  branch, commit, uncommitted-change hash and time in STATE. Nothing is merged in either direction.
- At acceptance, `sync --pin <task>` creates `refs/backlog/<name>/<task>` at the accepted commit, so rebasing
  the code branch cannot lose it. `git push`, `--all` and `--tags` never send `refs/backlog/*`.

## Guards

With the user's approval, `init --install-hooks` installs two hooks that every worktree of the repository
shares. It refuses to replace a hook it did not write.
An existing `core.hooksPath` must be absolute so every worktree uses the same hooks.

- `pre-commit` rejects added or modified `.backlog/` paths on branches outside `backlog/*`, and Python bytecode
  on every branch. Deleting old backlog files is still allowed.
- `pre-push` rejects pushing `backlog/*` branches or `refs/backlog/*` to any remote other than the private one
  named in `git config backlog.allowedRemote`. It also rejects any pushed commit that touches `.backlog/`.

A commit that already carries backlog files stays blocked from pushing until its history is rewritten;
deleting the files in a new commit does not remove them from history. Agents never pass `--no-verify`.

`backlog.py doctor --backlog <backlog>` reports an error when:
- the backlog branch shares history with code;
- the code branch tracks `.backlog/` paths;
- a `.backlog/` directory exists in the code worktree;
- the backlog contains bytecode.

It warns about other branches that track backlog paths, and about missing hooks or exclude entries.

## Move an in-tree backlog

With the user's approval:

1. Run `init` for a new orphan backlog.
2. Copy the old backlog's files into the new worktree and map them as a legacy backlog (see the contract).
3. Commit them on the backlog branch.
4. The user removes `.backlog/` from code branches in an ordinary commit, and rewrites history before pushing
   any branch whose commits added backlog files.
