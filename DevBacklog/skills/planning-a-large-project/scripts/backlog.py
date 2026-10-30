#!/usr/bin/env python3
"""Backlog helper for the planning-a-large-project contract, version 3.

Run it with `python3 -B` so it never writes bytecode into a backlog or repository.
Commands: init, sync, doctor, validate, query, cost.
Exit codes: 0 ok, 1 checks failed, 2 usage or environment error.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
SKILL = SCRIPTS.parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import backlog_checks as checks  # noqa: E402
import backlog_model as model  # noqa: E402
import backlog_storage as storage  # noqa: E402

TEMPLATES = SKILL / "assets" / "templates"
CONTRACT = SKILL / "references" / "contract.md"
HOOKS = SCRIPTS / "hooks"
EXECUTING_SKILL = SKILL.parent / "executing-a-large-project" / "SKILL.md"


def contract_sha() -> str:
    return hashlib.sha256(CONTRACT.read_bytes()).hexdigest()[:12] if CONTRACT.is_file() else "unknown"


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    with os.fdopen(handle, "w", encoding="utf-8") as stream:
        stream.write(text)
    os.replace(temporary, path)


def fill(template: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        template = template.replace(f"<<{key}>>", value)
    return template


def write_skeleton(backlog: Path, name: str, objective: str, storage_line: str, code_line: str) -> None:
    values = {
        "NAME": name,
        "OBJECTIVE": objective,
        "STORAGE": storage_line,
        "CODE": code_line,
        "CONTRACT_SHA": contract_sha(),
        "TOOL": str(SCRIPTS / "backlog.py"),
    }
    for source, target in (
        ("STATE.md", "STATE.md"),
        ("PROTOCOL.md", "PROTOCOL.md"),
        ("PLAN.md", "PLAN.md"),
        ("prep-task.md", "tasks/PREP-01.md"),
    ):
        atomic_write(backlog / target, fill(model.read_text(TEMPLATES / source), values))
    row = {
        "id": "PREP-01", "phase": "P0", "title": "Prepare the plan", "task": "tasks/PREP-01.md",
        "deps": [], "status": "in_progress", "successor": None, "checkpoint": None,
    }
    atomic_write(backlog / "tasks" / "index.json", json.dumps([row], indent=2) + "\n")
    atomic_write(backlog / ".gitignore", "__pycache__/\n*.pyc\n")


def print_report(report: checks.Report) -> int:
    for finding in report.findings:
        print(finding)
    errors = len(report.errors)
    print(f"validate: {errors} errors, {len(report.findings) - errors} warnings")
    return 1 if errors else 0


def read_state(backlog: Path) -> tuple[str, dict[str, list[str]]]:
    path = backlog / "STATE.md"
    if not path.is_file():
        raise storage.StorageError(f"{path} not found; pass the backlog root with --backlog")
    text = model.read_text(path)
    return text, model.parse_keys(text, stop_at_heading=False)


def cmd_init(args: argparse.Namespace) -> int:
    objective = args.objective or "record the requested outcome"
    if not storage.NAME.match(args.name):
        raise storage.StorageError(f"backlog name {args.name!r} must match {storage.NAME.pattern}")
    if args.profile == "directory":
        if not args.path:
            raise storage.StorageError("--path is required for the directory profile")
        backlog = Path(args.path).resolve()
        if backlog.exists() and any(backlog.iterdir()):
            raise storage.StorageError(f"{backlog} exists and is not empty")
        backlog.mkdir(parents=True, exist_ok=True)
        messages = [f"created directory backlog at {backlog}"]
        storage_line, code_line = f"directory {backlog}", "none"
    else:
        if not args.code:
            raise storage.StorageError("--code <repository> is required for the orphan-worktree profile")
        code = Path(args.code).resolve()
        backlog, messages = storage.create_orphan_worktree(
            code, args.name, Path(args.path) if args.path else None, HOOKS if args.install_hooks else None
        )
        storage_line = f"orphan-worktree backlog/{args.name} at {backlog}"
        code_line = storage.code_line(storage.code_identity(code))
    write_skeleton(backlog, args.name, objective, storage_line, code_line)
    for message in messages:
        print(message)
    return print_report(checks.validate(backlog, TEMPLATES))


def cmd_sync(args: argparse.Namespace) -> int:
    backlog = Path(args.backlog).resolve()
    text, keys = read_state(backlog)
    code = args.code or model.code_path(keys)
    if not code:
        raise storage.StorageError("STATE's code: line names no code worktree; pass --code")
    identity = storage.code_identity(Path(code))
    line = "code: " + storage.code_line(identity)
    print(line)
    if args.write:
        lines = text.splitlines(keepends=True)
        if not any(entry.startswith("code:") for entry in lines):
            raise storage.StorageError("STATE.md has no 'code:' line to replace")
        updated = "".join(line + "\n" if entry.startswith("code:") else entry for entry in lines)
        atomic_write(backlog / "STATE.md", updated)
    if args.pin:
        ref = storage.pin(Path(code), model.backlog_name(keys), args.pin, identity["sha"])
        print(f"pinned {ref} at {identity['sha'][:12]}")
        if identity["state"] != "clean":
            print("warning: the code worktree has uncommitted changes; the pin covers committed work only",
                  file=sys.stderr)
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    backlog = Path(args.backlog).resolve()
    _, keys = read_state(backlog)
    results = storage.doctor(backlog, model.first(keys, "storage") or "", model.code_path(keys), model.backlog_name(keys))
    for level, message in results:
        print(f"{level} doctor: {message}")
    errors = sum(1 for level, _ in results if level == "ERROR")
    print(f"doctor: {errors} errors, {len(results) - errors} warnings")
    return 1 if errors else 0


def cmd_validate(args: argparse.Namespace) -> int:
    return print_report(checks.validate(Path(args.backlog).resolve(), TEMPLATES))


def row_line(row: dict) -> str:
    return f"{row['id']}  {row['status']}  {row['phase']}  {row['title']}"


def task_requirements(backlog: Path, row: dict) -> list[str]:
    path = backlog / str(row["task"])
    if not path.is_file():
        return []
    return model.split_list(model.first(model.parse_keys(model.read_text(path)), "requirements") or "")


def query_csv(path: Path, where: list[str], columns: str | None) -> int:
    fields, rows = model.read_csv(path)
    filters = []
    for condition in where:
        column, separator, value = condition.partition("=")
        if not separator or column not in fields:
            raise storage.StorageError(f"--where {condition!r}: use COLUMN=VALUE with a column of {path.name}")
        filters.append((column, value))
    chosen = model.split_list(columns) if columns else fields
    unknown = [column for column in chosen if column not in fields]
    if unknown:
        raise storage.StorageError(f"--columns: unknown {', '.join(unknown)}")
    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow(chosen)
    for row in rows:
        if all(row.get(column) == value for column, value in filters):
            writer.writerow([row.get(column, "") for column in chosen])
    return 0


def cmd_query(args: argparse.Namespace) -> int:
    backlog = Path(args.backlog).resolve()
    if args.csv:
        return query_csv(backlog / args.csv, args.where or [], args.columns)
    rows = model.load_index(backlog)
    for row in rows:
        invalid = model.index_row_errors(row)
        if invalid:
            raise storage.StorageError(f"invalid index fields: {', '.join(invalid)}; run validate")
    by_id = {row["id"]: row for row in rows}
    if args.task:
        row = by_id.get(args.task)
        if row is None:
            print(f"no task {args.task} in tasks/index.json", file=sys.stderr)
            return 1
        print(row_line(row))
        for dep in row["deps"]:
            print(f"  dependency {dep}: {by_id.get(dep, {}).get('status', 'missing')}")
        print(f"  task file: {row['task']}")
        print(f"  checkpoint: {row['checkpoint'] or 'none'}")
        print(f"  successor: {row['successor'] or 'none'}")
        return 0
    if args.next:
        selected = [
            row for row in rows
            if row["status"] in ("planned", "ready")
            and all(by_id.get(dep, {}).get("status") == "done" for dep in row["deps"])
        ]
    elif args.status:
        selected = [row for row in rows if row["status"] == args.status]
    elif args.project:
        selected = [row for row in rows if row.get("project") == args.project]
    else:
        selected = [row for row in rows if args.requirement in task_requirements(backlog, row)]
    for row in selected:
        print(row_line(row))
    return 0


def cmd_cost(args: argparse.Namespace) -> int:
    backlog = Path(args.backlog).resolve()
    _, keys = read_state(backlog)
    candidates = [EXECUTING_SKILL, CONTRACT, backlog / "STATE.md", backlog / "PROTOCOL.md"]
    candidates += [backlog / item for item in model.split_list(model.first(keys, "read") or "")]
    files: list[Path] = []
    for path in candidates:
        resolved = path.resolve()
        if resolved.is_file() and resolved not in files:
            files.append(resolved)
    total = 0
    for path in files:
        size = path.stat().st_size
        total += size
        print(f"{size:>8} bytes  ~{size // 4:>6} tokens  {path}")
    print(f"{total:>8} bytes  ~{total // 4:>6} tokens  resume set")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="backlog.py", description="Backlog helper for contract version 3.")
    commands = parser.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="create a backlog from the templates")
    init.add_argument("--name", required=True, help="backlog name; the branch becomes backlog/<name>")
    init.add_argument("--code", help="code repository (orphan-worktree profile)")
    init.add_argument("--path", help="backlog directory (default: <repo parent>/backlog-<name>)")
    init.add_argument("--profile", choices=("orphan-worktree", "directory"), default="orphan-worktree")
    init.add_argument("--objective", default="", help="requested outcome, written into STATE and PLAN")
    init.add_argument("--install-hooks", action="store_true", help="install the backlog-guard git hooks")

    for name, summary in (
        ("sync", "record the code worktree's identity"),
        ("doctor", "check that the backlog and code stay separated"),
        ("validate", "check the backlog against the contract"),
        ("query", "print selected index rows or bulk-table rows"),
        ("cost", "print the size of the resume set"),
    ):
        command = commands.add_parser(name, help=summary)
        command.add_argument("--backlog", default=".", help="backlog root (default: current directory)")
        if name == "sync":
            command.add_argument("--code", help="code worktree (default: from STATE's code: line)")
            command.add_argument("--write", action="store_true", help="replace STATE's code: line")
            command.add_argument("--pin", metavar="TASK", help="create refs/backlog/<name>/<TASK> at HEAD")
        if name == "query":
            group = command.add_mutually_exclusive_group(required=True)
            group.add_argument("--task", metavar="ID")
            group.add_argument("--next", action="store_true", help="planned or ready tasks whose dependencies are done")
            group.add_argument("--status", choices=model.STATUSES)
            group.add_argument("--project")
            group.add_argument("--requirement", metavar="ID")
            group.add_argument("--csv", metavar="PATH", help="bulk table, relative to the backlog root")
            command.add_argument("--where", action="append", metavar="COLUMN=VALUE")
            command.add_argument("--columns", metavar="A,B")
    return parser


COMMANDS = {
    "init": cmd_init,
    "sync": cmd_sync,
    "doctor": cmd_doctor,
    "validate": cmd_validate,
    "query": cmd_query,
    "cost": cmd_cost,
}


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return COMMANDS[args.command](args)
    except (storage.StorageError, ValueError, OSError, csv.Error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
