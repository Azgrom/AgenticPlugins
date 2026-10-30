"""Git operations for ledger storage: orphan worktrees, code identity, pins, guards and separation checks."""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

HOOK_MARKER = "ledger-guard"
HOOK_NAMES = ("pre-commit", "pre-push")
MIN_GIT = (2, 42)
NAME = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


class StorageError(Exception):
    """A problem in the environment that the user must resolve."""


def git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True)
    if check and result.returncode != 0:
        raise StorageError(f"git {' '.join(args)} failed in {cwd}: {result.stderr.strip()}")
    return result


def git_bytes(cwd: Path, *args: str) -> bytes:
    result = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True)
    if result.returncode != 0:
        raise StorageError(f"git {' '.join(args)} failed in {cwd}: {result.stderr.decode(errors='replace').strip()}")
    return result.stdout


def git_path(cwd: Path, name: str) -> Path:
    """Absolute path of a git-managed file (hooks, info/exclude), honoring worktrees and core.hooksPath."""
    if name == "hooks":
        configured = git(cwd, "config", "--path", "--get", "core.hooksPath", check=False).stdout.strip()
        if configured:
            path = Path(configured)
            return path if path.is_absolute() else toplevel(cwd) / path
    return Path(git(cwd, "rev-parse", "--path-format=absolute", "--git-path", name).stdout.strip())


def toplevel(path: Path) -> Path:
    return Path(git(path, "rev-parse", "--show-toplevel").stdout.strip())


def worktree_paths(code: Path) -> list[Path]:
    records = git(code, "worktree", "list", "--porcelain", "-z").stdout.split("\0")
    return [Path(record.removeprefix("worktree ")).resolve()
            for record in records if record.startswith("worktree ")]


def require_git_version() -> None:
    output = subprocess.run(["git", "--version"], capture_output=True, text=True, check=True).stdout
    match = re.search(r"(\d+)\.(\d+)", output)
    if not match or (int(match[1]), int(match[2])) < MIN_GIT:
        raise StorageError("git 2.42 or newer is required for 'git worktree add --orphan'")


def create_orphan_worktree(code: Path, name: str, path: Path | None,
                           hooks_source: Path | None) -> tuple[Path, list[str]]:
    """Create branch ledger/<name> with no shared history, checked out in its own worktree."""
    if not NAME.match(name):
        raise StorageError(f"ledger name {name!r} must match {NAME.pattern}")
    require_git_version()
    top = toplevel(code)
    branch = f"ledger/{name}"
    worktrees = git(top, "worktree", "list", "--porcelain").stdout.splitlines()
    if (f"branch refs/heads/{branch}" in worktrees
            or git(top, "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}", check=False).returncode == 0):
        raise StorageError(f"branch {branch} already exists")
    target = (path or top.parent / f"ledger-{name}").resolve()
    if any(target.is_relative_to(root) for root in worktree_paths(top)):
        raise StorageError(f"{target} is inside an existing worktree; choose a separate ledger directory")
    if target.exists() and any(target.iterdir()):
        raise StorageError(f"{target} exists and is not empty")
    if hooks_source is not None:
        check_hooks_installable(top)
    git(top, "worktree", "add", "--orphan", "-b", branch, str(target))
    ensure_exclude(top)
    messages = [f"created branch {branch} with no shared history, checked out at {target}"]
    if hooks_source is not None:
        messages += install_hooks(top, hooks_source)
    return target, messages


def ensure_exclude(top: Path) -> None:
    exclude = git_path(top, "info/exclude")
    exclude.parent.mkdir(parents=True, exist_ok=True)
    text = exclude.read_text(encoding="utf-8") if exclude.is_file() else ""
    if "/.ledger/" not in text.splitlines():
        separator = "" if not text or text.endswith("\n") else "\n"
        exclude.write_text(text + separator + "/.ledger/\n", encoding="utf-8")


def check_hooks_installable(top: Path) -> None:
    configured = git(top, "config", "--path", "--get", "core.hooksPath", check=False).stdout.strip()
    if configured and not Path(configured).is_absolute():
        raise StorageError("core.hooksPath is relative; configure an absolute shared hooks directory before --install-hooks")
    hooks = git_path(top, "hooks")
    for name in HOOK_NAMES:
        target = hooks / name
        if target.exists() and HOOK_MARKER not in target.read_text(encoding="utf-8", errors="replace"):
            raise StorageError(f"{target} exists and is not a {HOOK_MARKER} hook; merge it by hand")


def install_hooks(top: Path, source: Path) -> list[str]:
    check_hooks_installable(top)
    hooks = git_path(top, "hooks")
    hooks.mkdir(parents=True, exist_ok=True)
    messages = []
    for name in HOOK_NAMES:
        target = hooks / name
        shutil.copyfile(source / name, target)
        target.chmod(0o755)
        messages.append(f"installed {target}")
    return messages


def code_identity(code: Path) -> dict[str, str]:
    top = toplevel(code)
    branch = git(top, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    sha = git(top, "rev-parse", "HEAD").stdout.strip()
    state = "clean"
    if git(top, "status", "--porcelain", "--untracked-files=all").stdout.strip():
        digest = hashlib.sha256(git_bytes(top, "diff", "HEAD", "--binary"))
        untracked = git_bytes(top, "ls-files", "--others", "--exclude-standard", "-z").split(b"\0")
        for name in sorted(item for item in untracked if item):
            digest.update(name + b"\0" + hashlib.sha256((top / name.decode()).read_bytes()).digest())
        state = "dirty:" + digest.hexdigest()[:12]
    observed = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {"path": str(top), "branch": branch, "sha": sha, "state": state, "observed": observed}


def code_line(identity: dict[str, str]) -> str:
    return (f"{identity['path']} @ {identity['branch']} {identity['sha'][:12]} {identity['state']}, "
            f"observed {identity['observed']}")


def pin(code: Path, name: str, task: str, sha: str) -> str:
    ref = f"refs/ledger/{name}/{task}"
    git(toplevel(code), "update-ref", ref, sha)
    return ref


def doctor(ledger: Path, storage: str, code_path: str | None, name: str) -> list[tuple[str, str]]:
    results: list[tuple[str, str]] = []
    for path in sorted(ledger.rglob("*")):
        if path.name == "__pycache__" or path.suffix == ".pyc":
            results.append(("ERROR", f"bytecode in the ledger: {path}"))
    profile = storage.split()[0] if storage.split() else ""
    if profile != "orphan-worktree":
        results.append(("WARN", f"storage profile {profile or 'unknown'}: separation checks skipped"))
        return results
    expected = f"ledger/{name}"
    branch = git(ledger, "symbolic-ref", "--quiet", "--short", "HEAD", check=False).stdout.strip()
    if branch != expected:
        results.append(("ERROR", f"the ledger worktree is on {branch or 'a detached HEAD'}, expected {expected}"))
    if not code_path:
        results.append(("ERROR", "STATE's code: line names no code worktree"))
        return results
    code = Path(code_path)
    if not code.is_dir():
        results.append(("ERROR", f"code worktree {code} not found"))
        return results
    return results + separation(ledger, code, expected)


def separation(ledger: Path, code: Path, expected: str) -> list[tuple[str, str]]:
    results: list[tuple[str, str]] = []
    for root in worktree_paths(code):
        if root != ledger.resolve() and ledger.resolve().is_relative_to(root):
            results.append(("ERROR", f"the ledger directory {ledger} is inside worktree {root}"))
    ledger_head = git(ledger, "rev-parse", "--verify", "--quiet", "HEAD", check=False).stdout.strip()
    code_head = git(code, "rev-parse", "HEAD").stdout.strip()
    if ledger_head:
        base = git(code, "merge-base", ledger_head, code_head, check=False)
        if base.returncode == 0:
            results.append(("ERROR", f"the ledger branch shares history with code (merge base {base.stdout.strip()[:12]})"))
    tracked = git(code, "ls-files", "--", ".ledger").stdout.splitlines()
    if tracked:
        results.append(("ERROR", f"the code branch tracks {len(tracked)} path(s) under .ledger/"))
    if (code / ".ledger").exists():
        results.append(("ERROR", f"{code / '.ledger'} exists inside the code worktree"))
    for ref in git(code, "for-each-ref", "--format=%(refname:short)", "refs/heads").stdout.splitlines():
        if ref.startswith("ledger/"):
            continue
        count = len(git(code, "ls-tree", "-r", "--name-only", ref, "--", ".ledger").stdout.splitlines())
        if count:
            results.append(("WARN", f"branch {ref} tracks {count} path(s) under .ledger/"))
    for hooks in sorted({git_path(code, "hooks"), git_path(ledger, "hooks")}):
        for name in HOOK_NAMES:
            target = hooks / name
            if (not target.is_file() or not os.access(target, os.X_OK)
                    or HOOK_MARKER not in target.read_text(encoding="utf-8", errors="replace")):
                results.append(("WARN", f"the {name} hook is not installed or executable at {target}; use a shared hooks directory"))
    exclude = git_path(code, "info/exclude")
    if not exclude.is_file() or "/.ledger/" not in exclude.read_text(encoding="utf-8").splitlines():
        results.append(("WARN", "'/.ledger/' is missing from info/exclude"))
    remote = git(ledger, "config", "--get", f"branch.{expected}.remote", check=False).stdout.strip()
    allowed = git(code, "config", "--get", "ledger.allowedRemote", check=False).stdout.strip()
    if remote and remote != allowed:
        results.append(("WARN", f"the ledger branch tracks remote {remote}, which is not ledger.allowedRemote"))
    return results
