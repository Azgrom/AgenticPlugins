"""Orphan-worktree storage: init, sync, doctor and the backlog-guard hooks on temporary git repositories."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

BACKLOG_PY = Path(__file__).resolve().parents[1] / "backlog.py"


class GitCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()
        home = self.root / "home"
        home.mkdir()
        (home / ".gitconfig").write_text("", encoding="utf-8")
        self.env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        self.env.update({
            "HOME": str(home),
            "GIT_CONFIG_GLOBAL": str(home / ".gitconfig"),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "test@example.invalid",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "test@example.invalid",
            "PYTHONDONTWRITEBYTECODE": "1",
        })
        self.code = self.root / "project"
        self.code.mkdir()
        self.git(self.code, "init", "-q", "-b", "main")
        (self.code / "README.md").write_text("code\n", encoding="utf-8")
        self.git(self.code, "add", "README.md")
        self.git(self.code, "commit", "-q", "-m", "initial")
        self.backlog_dir = self.root / "backlog-demo"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def git(self, cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
        result = subprocess.run(["git", "-C", str(cwd), *args], env=self.env, capture_output=True, text=True)
        if check:
            self.assertEqual(result.returncode, 0, f"git {' '.join(args)}: {result.stderr}")
        return result

    def backlog(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "-B", str(BACKLOG_PY), *args], env=self.env,
                              capture_output=True, text=True)

    def init(self, *extra: str) -> Path:
        result = self.backlog("init", "--name", "demo", "--code", str(self.code), "--objective", "demo objective", *extra)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return self.backlog_dir

    def commit_backlog(self) -> None:
        self.git(self.backlog_dir, "add", "-A")
        self.git(self.backlog_dir, "commit", "-q", "-m", "backlog: init")

    def commit_backlog_file_on_code(self) -> None:
        (self.code / ".backlog").mkdir()
        (self.code / ".backlog" / "STATE.md").write_text("old backlog\n", encoding="utf-8")
        self.git(self.code, "add", "-f", ".backlog/STATE.md")
        self.git(self.code, "commit", "-q", "-m", "old backlog")

    def add_remote(self) -> None:
        remote = self.root / "remote.git"
        self.git(self.root, "init", "-q", "--bare", str(remote))
        self.git(self.code, "remote", "add", "origin", str(remote))

    def git_path(self, name: str) -> Path:
        return Path(self.git(self.code, "rev-parse", "--path-format=absolute", "--git-path", name).stdout.strip())


class InitTests(GitCase):
    def test_refuses_backlog_inside_code_even_when_ignored(self) -> None:
        exclude = self.git_path("info/exclude")
        exclude.write_text(exclude.read_text() + "\n/project-backlog/\n", encoding="utf-8")
        target = self.code / "project-backlog"
        result = self.backlog("init", "--name", "nested", "--code", str(self.code), "--path", str(target))
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertFalse(target.exists())
        self.assertNotIn("refs/heads/backlog/nested", self.git(self.code, "worktree", "list", "--porcelain").stdout)

    def test_relative_hooks_path_is_rejected_before_mutation(self) -> None:
        self.git(self.code, "config", "core.hooksPath", ".hooks")
        result = self.backlog("init", "--name", "demo", "--code", str(self.code), "--install-hooks")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("absolute", result.stderr)
        self.assertFalse(self.backlog_dir.exists())
        self.assertFalse((self.code / ".hooks").exists())
        self.assertEqual(self.git(self.code, "config", "core.hooksPath").stdout.strip(), ".hooks")

    def test_creates_orphan_branch_in_separate_worktree(self) -> None:
        backlog = self.init()
        self.assertTrue((backlog / "STATE.md").is_file())
        self.assertEqual(self.git(backlog, "symbolic-ref", "--short", "HEAD").stdout.strip(), "backlog/demo")
        self.commit_backlog()
        self.assertNotEqual(self.git(self.code, "merge-base", "main", "backlog/demo", check=False).returncode, 0)

    def test_leaves_code_worktree_untouched_and_excluded(self) -> None:
        self.init()
        self.assertEqual(self.git(self.code, "status", "--porcelain").stdout, "")
        self.assertFalse((self.code / ".backlog").exists())
        self.assertIn("/.backlog/", self.git_path("info/exclude").read_text(encoding="utf-8").splitlines())

    def test_skeleton_validates(self) -> None:
        result = self.backlog("init", "--name", "demo", "--code", str(self.code), "--objective", "demo objective")
        self.assertIn("validate: 0 errors, 0 warnings", result.stdout)

    def test_refuses_existing_branch(self) -> None:
        self.init()
        result = self.backlog("init", "--name", "demo", "--code", str(self.code), "--path", str(self.root / "other"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("already exists", result.stderr)

    def test_refuses_foreign_hook_before_creating_anything(self) -> None:
        hooks = self.git_path("hooks")
        hooks.mkdir(exist_ok=True)
        (hooks / "pre-commit").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        result = self.backlog("init", "--name", "demo", "--code", str(self.code), "--install-hooks")
        self.assertEqual(result.returncode, 2)
        self.assertIn("not a backlog-guard hook", result.stderr)
        self.assertFalse(self.backlog_dir.exists())
        self.assertEqual((hooks / "pre-commit").read_text(encoding="utf-8"), "#!/bin/sh\nexit 0\n")


class SyncTests(GitCase):
    def test_reports_clean_then_dirty_and_writes_state(self) -> None:
        backlog = self.init()
        head = self.git(self.code, "rev-parse", "HEAD").stdout.strip()[:12]
        self.assertIn(f"main {head} clean", self.backlog("sync", "--backlog", str(backlog)).stdout)
        (self.code / "README.md").write_text("changed\n", encoding="utf-8")
        dirty = self.backlog("sync", "--backlog", str(backlog), "--write")
        self.assertIn("dirty:", dirty.stdout)
        self.assertIn("dirty:", (backlog / "STATE.md").read_text(encoding="utf-8"))

    def test_pin_creates_backlog_ref_at_head(self) -> None:
        backlog = self.init()
        result = self.backlog("sync", "--backlog", str(backlog), "--pin", "T01")
        self.assertEqual(result.returncode, 0, result.stderr)
        pinned = self.git(self.code, "rev-parse", "refs/backlog/demo/T01").stdout.strip()
        self.assertEqual(pinned, self.git(self.code, "rev-parse", "HEAD").stdout.strip())


class DoctorTests(GitCase):
    def test_nested_backlog_worktree_is_diagnosed(self) -> None:
        self.init("--install-hooks")
        self.commit_backlog()
        target = self.code / "nested-backlog"
        self.git(self.code, "worktree", "move", str(self.backlog_dir), str(target))
        result = self.backlog("doctor", "--backlog", str(target))
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("inside", result.stdout)

    def test_non_executable_hook_is_diagnosed(self) -> None:
        self.init("--install-hooks")
        (self.git_path("hooks") / "pre-push").chmod(0o644)
        result = self.backlog("doctor", "--backlog", str(self.backlog_dir))
        self.assertIn("WARN", result.stdout)
        self.assertIn("pre-push", result.stdout)

    def test_checks_effective_hooks_in_both_worktrees(self) -> None:
        self.init("--install-hooks")
        shared_hooks = self.git_path("hooks")
        self.git(self.code, "config", "core.hooksPath", str(shared_hooks.relative_to(self.code)))
        result = self.backlog("doctor", "--backlog", str(self.backlog_dir))
        self.assertIn("WARN", result.stdout)
        self.assertIn("pre-push", result.stdout)

    def test_fresh_setup_with_hooks_passes(self) -> None:
        backlog = self.init("--install-hooks")
        self.commit_backlog()
        result = self.backlog("doctor", "--backlog", str(backlog))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertNotIn("ERROR", result.stdout)
        self.assertNotIn("WARN", result.stdout)

    def test_missing_hooks_only_warn(self) -> None:
        backlog = self.init()
        result = self.backlog("doctor", "--backlog", str(backlog))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("pre-commit hook is not installed", result.stdout)

    def test_backlog_files_on_code_branch_fail(self) -> None:
        self.commit_backlog_file_on_code()
        backlog = self.init()
        result = self.backlog("doctor", "--backlog", str(backlog))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("tracks 1 path(s) under .backlog/", result.stdout)


class HookTests(GitCase):
    def test_pre_commit_blocks_git_quoted_filenames(self) -> None:
        self.init("--install-hooks")
        for name in (".backlog/café.md", ".backlog/notes\nsecret.md", "café.pyc", "cache\nfile.pyc"):
            with self.subTest(path=name):
                path = self.code / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("test\n", encoding="utf-8")
                self.git(self.code, "add", "-f", "--", name)
                result = self.git(self.code, "commit", "-m", "quoted path", check=False)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("backlog-guard", result.stderr)
                self.git(self.code, "reset", "-q", "HEAD", "--", name)

    def test_pre_push_blocks_git_quoted_backlog_filenames(self) -> None:
        self.add_remote()
        path = self.code / ".backlog" / "café\nnotes.md"
        path.parent.mkdir()
        path.write_text("backlog\n", encoding="utf-8")
        self.git(self.code, "add", "-f", ".backlog")
        self.git(self.code, "commit", "-q", "-m", "old backlog")
        self.init("--install-hooks")
        result = self.git(self.code, "push", "origin", "main", check=False)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("backlog-guard", result.stderr)

    def test_absolute_hooks_path_guards_both_worktrees(self) -> None:
        self.add_remote()
        self.git(self.code, "config", "core.hooksPath", str(self.root / "shared-hooks"))
        self.init("--install-hooks")
        self.commit_backlog()
        result = self.git(self.backlog_dir, "push", "origin", "backlog/demo", check=False)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        path = self.backlog_dir / "module.pyc"
        path.write_bytes(b"\x00")
        self.git(self.backlog_dir, "add", "-f", "module.pyc")
        result = self.git(self.backlog_dir, "commit", "-m", "bytecode", check=False)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_pre_commit_blocks_backlog_paths_on_code_branches(self) -> None:
        self.init("--install-hooks")
        (self.code / ".backlog").mkdir()
        (self.code / ".backlog" / "notes.md").write_text("backlog\n", encoding="utf-8")
        self.git(self.code, "add", "-f", ".backlog/notes.md")
        result = self.git(self.code, "commit", "-m", "sneak backlog in", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("backlog-guard", result.stderr)

    def test_pre_commit_blocks_bytecode(self) -> None:
        self.init("--install-hooks")
        (self.code / "pkg" / "__pycache__").mkdir(parents=True)
        (self.code / "pkg" / "__pycache__" / "m.cpython-314.pyc").write_bytes(b"\x00")
        self.git(self.code, "add", "-f", "pkg/__pycache__/m.cpython-314.pyc")
        result = self.git(self.code, "commit", "-m", "bytecode", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("backlog-guard", result.stderr)

    def test_pre_commit_allows_code_and_backlog_branch_commits(self) -> None:
        self.init("--install-hooks")
        (self.code / "README.md").write_text("more code\n", encoding="utf-8")
        self.git(self.code, "commit", "-q", "-am", "code change")
        self.commit_backlog()

    def test_pre_commit_allows_deleting_old_backlog_files(self) -> None:
        self.commit_backlog_file_on_code()
        self.init("--install-hooks")
        self.git(self.code, "rm", "-q", ".backlog/STATE.md")
        self.git(self.code, "commit", "-q", "-m", "remove old backlog")

    def test_pre_push_blocks_backlog_branch(self) -> None:
        self.add_remote()
        self.init("--install-hooks")
        self.commit_backlog()
        result = self.git(self.code, "push", "origin", "backlog/demo", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("backlog-guard", result.stderr)
        self.git(self.code, "push", "-q", "origin", "main")

    def test_pre_push_allows_backlog_branch_to_allowed_remote(self) -> None:
        self.add_remote()
        self.init("--install-hooks")
        self.commit_backlog()
        self.git(self.code, "config", "backlog.allowedRemote", "origin")
        self.git(self.code, "push", "-q", "origin", "backlog/demo")

    def test_pre_push_blocks_commits_touching_backlog_paths(self) -> None:
        self.add_remote()
        self.commit_backlog_file_on_code()
        self.init("--install-hooks")
        result = self.git(self.code, "push", "origin", "main", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("backlog-guard", result.stderr)


if __name__ == "__main__":
    unittest.main()
