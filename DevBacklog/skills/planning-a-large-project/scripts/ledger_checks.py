"""Validation rules for a contract-3 ledger.

validate() returns a Report of findings: ERROR means the ledger is not usable as it stands, WARN means it
works but wastes context or invites drift.
"""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

import ledger_model as model

BUDGETS = {"STATE.md": 2048, "PROTOCOL.md": 4096, "PLAN.md": 8192}
TASK_BUDGET = 4096
CHECKPOINT_BUDGET = 4096
OTHER_MARKDOWN_WARN = 16384
LINE_LIMIT = 400
BOOT_FILES = ("STATE.md", "PROTOCOL.md", "PLAN.md")
LINK_LIMIT = 16384
LARGE_WARN = 256 * 1024
LARGE_ERROR = 1024 * 1024
PROVENANCE_ROWS = 20
BASIS_VALUES = {"script", "read", "executed", "inferred"}
REPEAT_MIN_LENGTH = 40
REPEAT_MIN_FILES = 5


@dataclass(frozen=True)
class Finding:
    level: str
    rule: str
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.level} {self.rule} {self.path}: {self.message}"


class Report:
    def __init__(self, ledger: Path) -> None:
        self.ledger = ledger
        self.findings: list[Finding] = []

    def error(self, rule: str, path: str, message: str) -> None:
        self.findings.append(Finding("ERROR", rule, path, message))

    def warn(self, rule: str, path: str, message: str) -> None:
        self.findings.append(Finding("WARN", rule, path, message))

    @property
    def errors(self) -> list[Finding]:
        return [finding for finding in self.findings if finding.level == "ERROR"]

    def rel(self, path: Path) -> str:
        return path.relative_to(self.ledger).as_posix()


def ledger_files(root: Path, pattern: str = "*") -> list[Path]:
    return sorted(path for path in root.rglob(pattern) if ".git" not in path.relative_to(root).parts)


def validate(ledger: Path, templates: Path) -> Report:
    report = Report(ledger)
    state_path = ledger / "STATE.md"
    if not state_path.is_file():
        report.error("state.missing", "STATE.md", "no STATE.md here; pass the ledger root with --ledger")
        return report
    state = model.parse_keys(model.read_text(state_path), stop_at_heading=False)
    version = model.contract_version(model.first(state, "contract") or "")
    if version != model.CONTRACT_VERSION:
        report.error(
            "state.contract", "STATE.md",
            f"legacy ledger (contract {version or 'unknown'}); follow the contract's 'Legacy ledgers' section",
        )
        return report
    index = check_index(report)
    check_state(report, state, index)
    classes = check_protocol(report)
    check_plan(report, state, index)
    check_tasks(report, index)
    check_checkpoints(report, classes)
    check_markdown(report, templates)
    check_tables(report)
    check_files(report)
    return report


def check_index(report: Report) -> list[dict] | None:
    where = "tasks/index.json"
    if not (report.ledger / where).is_file():
        report.error("index.missing", where, "the task index is missing")
        return None
    try:
        rows = model.load_index(report.ledger)
    except (ValueError, json.JSONDecodeError) as exc:
        report.error("index.json", where, str(exc))
        return None
    well_formed = []
    for row in rows:
        invalid = model.index_row_errors(row)
        if invalid:
            rule = "index.deps" if invalid == ["deps"] else "index.fields"
            report.error(rule, where, f"invalid or missing fields: {', '.join(invalid)}")
        else:
            well_formed.append(row)
    ids = {row["id"] for row in well_formed}
    seen: set[str] = set()
    valid: list[dict] = []
    for row in well_formed:
        task_id = row.get("id", "?")
        missing = [field for field in model.INDEX_FIELDS if field not in row]
        if missing:
            report.error("index.fields", where, f"{task_id}: missing {', '.join(missing)}")
            continue
        if task_id in seen:
            report.error("index.unique", where, f"duplicate id {task_id}")
        seen.add(task_id)
        valid.append(row)
        if row["status"] not in model.STATUSES:
            report.error("index.status", where, f"{task_id}: unknown status {row['status']!r}")
        if not isinstance(row["deps"], list):
            report.error("index.deps", where, f"{task_id}: deps must be a list")
        else:
            for dep in row["deps"]:
                if dep not in ids:
                    report.error("index.deps", where, f"{task_id}: dependency {dep} does not exist")
        if row["successor"] is not None and row["successor"] not in ids:
            report.error("index.successor", where, f"{task_id}: successor {row['successor']} does not exist")
        if not (report.ledger / str(row["task"])).is_file():
            report.error("index.task", where, f"{task_id}: task file {row['task']} not found")
        check_index_checkpoint(report, row)
    cycle = find_cycle(valid)
    if cycle:
        report.error("index.cycle", where, "dependency cycle " + " -> ".join(cycle))
    return valid


def check_index_checkpoint(report: Report, row: dict) -> None:
    where, task_id, checkpoint = "tasks/index.json", row["id"], row["checkpoint"]
    if checkpoint is None:
        if row["status"] in ("done", "awaiting_acceptance"):
            report.error("index.checkpoint", where, f"{task_id}: status {row['status']} needs a checkpoint")
        return
    path = report.ledger / checkpoint
    checkpoint_root = report.ledger / "checkpoints"
    if not path.resolve().is_relative_to(checkpoint_root):
        report.error("index.checkpoint", where, f"{task_id}: checkpoint must be inside checkpoints/")
        return
    if not path.is_file():
        report.error("index.checkpoint", where, f"{task_id}: checkpoint {checkpoint} not found")
        return
    if row["status"] == "done":
        keys = model.parse_keys(model.read_text(path), stop_at_heading=False)
        acceptance = model.first(keys, "acceptance") or "pending"
        if acceptance == "pending" or not model.ACCEPTANCE.fullmatch(acceptance):
            report.error("index.acceptance", where, f"{task_id}: done, but {checkpoint} has no acceptance")
        checkpoint_task = (model.first(keys, "task") or "").split(" / ", 1)[0]
        if checkpoint_task != task_id:
            report.error("index.acceptance", where, f"{task_id}: checkpoint belongs to {checkpoint_task or 'no task'}")
        if model.first(keys, "kind") not in ("accepted", "planning", "replan", "closeout"):
            report.error("index.acceptance", where, f"{task_id}: checkpoint kind cannot accept a task")


def find_cycle(rows: list[dict]) -> list[str] | None:
    graph = {row["id"]: [dep for dep in row["deps"] if isinstance(dep, str)]
             for row in rows if isinstance(row["deps"], list)}
    visiting: list[str] = []
    finished: set[str] = set()

    def visit(node: str) -> list[str] | None:
        visiting.append(node)
        for dep in graph.get(node, []):
            if dep in visiting:
                return visiting[visiting.index(dep):] + [dep]
            if dep in graph and dep not in finished:
                found = visit(dep)
                if found:
                    return found
        visiting.pop()
        finished.add(node)
        return None

    for node in graph:
        if node not in finished:
            found = visit(node)
            if found:
                return found
    return None


def check_state(report: Report, state: dict[str, list[str]], index: list[dict] | None) -> None:
    where = "STATE.md"
    for key in model.STATE_KEYS:
        count = len(state.get(key, []))
        if count == 0:
            report.error("state.keys", where, f"missing '{key}:'")
        elif count > 1:
            report.error("state.keys", where, f"'{key}:' appears {count} times; STATE keeps one of each")
    lifecycle = model.first(state, "lifecycle")
    if lifecycle and lifecycle not in model.LIFECYCLES:
        report.error("state.lifecycle", where, f"unknown lifecycle {lifecycle!r}")
    cursor = model.first(state, "cursor")
    if cursor:
        check_cursor(report, cursor, index)
    for key in ("accepted", "recovery"):
        target = model.pointer(model.first(state, key))
        if target and not (report.ledger / target).is_file():
            report.error(f"state.{key}", where, f"{target} not found")
    for target in model.split_list(model.first(state, "read") or ""):
        path = report.ledger / target
        if not path.is_file():
            report.error("state.read", where, f"{target} not found")
        elif path.stat().st_size > LINK_LIMIT:
            report.error("links.boot", where, f"read: loads {target} ({path.stat().st_size} bytes); use query")


def check_cursor(report: Report, cursor: str, index: list[dict] | None) -> None:
    where = "STATE.md"
    match = model.CURSOR.match(cursor)
    if not match:
        report.error("state.cursor", where, "cursor must read '<phase> / <task> / <step> — <status>'")
        return
    if not match["step"].startswith(match["task"] + "."):
        report.error("state.cursor", where, f"step {match['step']} does not belong to {match['task']}")
    if index is None:
        return
    row = next((row for row in index if row["id"] == match["task"]), None)
    if row is None:
        report.error("state.cursor", where, f"task {match['task']} is not in tasks/index.json")
    elif row["status"] != match["status"]:
        report.error(
            "state.cursor", where,
            f"cursor says {match['status']} but the index says {row['status']} for {match['task']}",
        )
    if row is not None:
        if row["phase"] != match["phase"]:
            report.error("state.cursor", where, f"cursor phase {match['phase']} differs from {row['phase']}")
        path = report.ledger / row["task"]
        if path.is_file() and match["step"] not in model.step_ids(model.read_text(path)):
            report.error("state.cursor", where, f"step {match['step']} is absent from {row['task']}")


def check_protocol(report: Report) -> dict[str, bool]:
    where = "PROTOCOL.md"
    path = report.ledger / where
    if not path.is_file():
        report.error("protocol.missing", where, "PROTOCOL.md is missing")
        return {}
    text = model.read_text(path)
    keys = model.parse_keys(text, stop_at_heading=False)
    for key in model.PROTOCOL_KEYS:
        if key not in keys:
            report.error("protocol.keys", where, f"missing '{key}:'")
    classes = {}
    for item in model.list_items(text, "stop classes"):
        if ":" in item:
            name, rule = item.split(":", 1)
            classes[name.strip()] = "stop for human" in rule.lower()
    if not classes:
        report.error("protocol.stop_classes", where, "declare at least one stop class")
    return classes


def check_plan(report: Report, state: dict[str, list[str]], index: list[dict] | None) -> None:
    where = "PLAN.md"
    path = report.ledger / where
    if not path.is_file():
        report.error("plan.missing", where, "PLAN.md is missing")
        return
    text = model.read_text(path)
    phases_path = report.ledger / "phases.md"
    phase_text = text + ("\n" + model.read_text(phases_path) if phases_path.is_file() else "")
    requirements = model.table_first_column(text, "Requirements")
    phases = model.table_first_column(phase_text, "Phases")
    flag = report.warn if model.first(state, "lifecycle") == "planning" else report.error
    covered: set[str] = set()
    for row in index or []:
        task_path = report.ledger / str(row["task"])
        if task_path.is_file():
            keys = model.parse_keys(model.read_text(task_path))
            covered.update(model.split_list(model.first(keys, "requirements") or ""))
        if row["phase"] not in phases:
            flag("plan.phases", where, f"{row['id']}: phase {row['phase']} is not in the Phases table")
    for requirement in requirements:
        if requirement not in covered:
            flag("plan.coverage", where, f"requirement {requirement} has no task")


def check_tasks(report: Report, index: list[dict] | None) -> None:
    directory = report.ledger / "tasks"
    if not directory.is_dir():
        return
    rows = {str(row["task"]): row for row in index or []}
    for path in ledger_files(directory, "*.md"):
        where = report.rel(path)
        text = model.read_text(path)
        keys = model.parse_keys(text)
        for key in model.TASK_KEYS:
            if key not in keys:
                report.error("task.keys", where, f"missing '{key}:'")
        row = rows.get(where)
        if row is None:
            report.warn("task.index", where, "no row in tasks/index.json points to this file")
            continue
        for step in model.step_ids(text):
            if not step.startswith(row["id"] + "."):
                report.error("task.steps", where, f"step {step} does not belong to {row['id']}")
        root = row.get("root")
        if root:
            for owned in model.split_list(model.first(keys, "owns") or ""):
                if not model.is_under(owned, root):
                    report.error("task.owns", where, f"owned path {owned} is outside {root}")


def check_checkpoints(report: Report, classes: dict[str, bool]) -> None:
    directory = report.ledger / "checkpoints"
    if not directory.is_dir():
        return
    for path in ledger_files(directory, "*.md"):
        where = report.rel(path)
        keys = model.parse_keys(model.read_text(path), stop_at_heading=False)
        for key in model.CHECKPOINT_KEYS:
            if key not in keys:
                report.error("checkpoint.keys", where, f"missing '{key}:'")
        acceptance = model.first(keys, "acceptance")
        if acceptance is None:
            continue
        match = model.ACCEPTANCE.match(acceptance)
        if not match:
            report.error(
                "checkpoint.acceptance", where,
                'acceptance must be pending, human "<verbatim words>" (<source>, <date>) or policy <stop class>',
            )
        elif match["cls"] and match["cls"] not in classes:
            report.error("checkpoint.acceptance", where, f"stop class {match['cls']} is not declared in PROTOCOL")
        elif match["cls"] and classes[match["cls"]]:
            report.error("checkpoint.acceptance", where, f"stop class {match['cls']} requires human acceptance")


def check_markdown(report: Report, templates: Path) -> None:
    allowed_repeats = template_lines(templates)
    holders: dict[str, set[str]] = {}
    for path in ledger_files(report.ledger, "*.md"):
        where = report.rel(path)
        data = path.read_bytes()
        text = data.decode("utf-8", errors="replace")
        strict = where in BOOT_FILES or where.startswith(("tasks/", "checkpoints/"))
        check_size(report, where, len(data))
        for number, line in enumerate(text.splitlines(), 1):
            if len(line) > LINE_LIMIT:
                (report.error if strict else report.warn)(
                    "size.line", where, f"line {number} has {len(line)} characters (limit {LINE_LIMIT})"
                )
        check_links(report, path, where, text, strict)
        for line in model.strip_fences(text).splitlines():
            normalized = " ".join(line.split())
            if len(normalized) >= REPEAT_MIN_LENGTH and normalized not in allowed_repeats:
                holders.setdefault(normalized, set()).add(where)
    for line, files in sorted(holders.items()):
        if len(files) >= REPEAT_MIN_FILES:
            report.warn(
                "repeat.lines", min(files),
                f"{len(files)} files repeat '{line[:80]}'; write it once in PROTOCOL or a linked record",
            )


def check_size(report: Report, where: str, size: int) -> None:
    if where in BUDGETS:
        budget = BUDGETS[where]
    elif where.startswith("tasks/"):
        budget = TASK_BUDGET
    elif where.startswith("checkpoints/"):
        budget = CHECKPOINT_BUDGET
    else:
        if size > OTHER_MARKDOWN_WARN:
            report.warn("size.budget", where, f"{size} bytes; split it or route readers through query")
        return
    if size > budget:
        report.error("size.budget", where, f"{size} bytes; budget {budget}")


def check_links(report: Report, path: Path, where: str, text: str, strict: bool) -> None:
    for target in model.links(text):
        resolved = Path(target) if target.startswith("/") else path.parent / target
        inside = is_inside(resolved, report.ledger)
        if not resolved.exists():
            (report.error if inside else report.warn)("links.target", where, f"{target} not found")
            continue
        if not inside or not resolved.is_file():
            continue
        size = resolved.stat().st_size
        if size <= LINK_LIMIT:
            continue
        if where in BOOT_FILES:
            report.error("links.boot", where, f"links {target} ({size} bytes); route it through ledger.py query")
        elif strict:
            report.warn("links.large", where, f"links {target} ({size} bytes); say how to read a slice of it")


def is_inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def template_lines(templates: Path) -> set[str]:
    lines: set[str] = set()
    if templates.is_dir():
        for path in templates.glob("*.md"):
            lines.update(" ".join(line.split()) for line in model.read_text(path).splitlines())
    return lines


def check_tables(report: Report) -> None:
    for path in ledger_files(report.ledger, "*.csv"):
        where = report.rel(path)
        try:
            fields, rows = model.read_csv(path)
        except (csv.Error, UnicodeDecodeError) as exc:
            report.error("csv.parse", where, str(exc))
            continue
        if len(rows) <= PROVENANCE_ROWS:
            continue
        missing = [column for column in ("basis", "verified_by") if column not in fields]
        if missing:
            report.error("csv.provenance", where, f"{len(rows)} rows without {' and '.join(missing)} columns")
        else:
            unknown = sorted({row.get("basis") or "" for row in rows} - BASIS_VALUES)
            if unknown:
                report.error(
                    "csv.provenance", where,
                    f"basis must be script, read, executed or inferred; found {', '.join(map(repr, unknown[:5]))}",
                )
        for column in fields:
            if column in ("basis", "verified_by"):
                continue
            values = {row.get(column) or "" for row in rows}
            if len(values) == 1 and values != {""}:
                report.warn("csv.constant", where, f"column {column} holds one value in all {len(rows)} rows; state it once")


def check_files(report: Report) -> None:
    allowed = large_file_allowlist(report.ledger)
    for path in ledger_files(report.ledger):
        where = report.rel(path)
        if path.is_dir():
            if path.name == "__pycache__":
                report.error("files.bytecode", where, "remove it; run ledger scripts with python3 -B")
            continue
        if path.suffix == ".pyc":
            if "__pycache__" not in path.parts:
                report.error("files.bytecode", where, "remove it; run ledger scripts with python3 -B")
            continue
        if where in allowed:
            continue
        size = path.stat().st_size
        if size > LARGE_ERROR:
            report.error(
                "files.large", where,
                f"{size} bytes; store generator, seed and hash, or give a reason in evidence/large-files.txt",
            )
        elif size > LARGE_WARN:
            report.warn("files.large", where, f"{size} bytes")


def large_file_allowlist(ledger: Path) -> set[str]:
    path = ledger / "evidence" / "large-files.txt"
    if not path.is_file():
        return set()
    entries: set[str] = set()
    for line in model.read_text(path).splitlines():
        name, separator, reason = line.partition(" — ")
        if not separator:
            name, separator, reason = line.partition(" - ")
        if name.strip() and separator and reason.strip():
            entries.add(name.strip())
    return entries
