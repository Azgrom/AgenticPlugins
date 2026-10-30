"""Read ledger files into plain Python values.

This module only parses. Decisions about what is valid live in ledger_checks.py.
"""
from __future__ import annotations

import csv
import json
import posixpath
import re
from pathlib import Path

CONTRACT_VERSION = "3"
STATUSES = ("planned", "ready", "in_progress", "review", "awaiting_acceptance", "done", "blocked", "needs_replan")
LIFECYCLES = ("planning", "ready", "executing", "blocked", "complete", "archived")
STATE_KEYS = (
    "contract", "ledger", "lifecycle", "storage", "code", "plan", "cursor",
    "accepted", "recovery", "pending", "operations", "next", "read",
)
TASK_KEYS = ("outcome", "entry", "owns", "checks", "exit")
CHECKPOINT_KEYS = ("kind", "task", "artifact", "acceptance", "next")
PROTOCOL_KEYS = ("authority", "storage", "authorization", "delivery", "stop classes", "check profiles", "session")
INDEX_FIELDS = ("id", "phase", "title", "task", "deps", "status", "successor", "checkpoint")

KEY_LINE = re.compile(r"^([a-z][a-z ]*[a-z]):(?:[ \t]+(.*))?$")
CURSOR = re.compile(r"^(?P<phase>\S+) / (?P<task>\S+) / (?P<step>\S+) (?:—|-) (?P<status>\S+)$")
ACCEPTANCE = re.compile(r'^(?:pending|human ".+" \(.+\)|policy (?P<cls>\S+))$')
STEP = re.compile(r"^- \[[ xX]\] (\S+)")
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
SEPARATOR_CELL = re.compile(r":?-{3,}:?")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def strip_fences(text: str) -> str:
    """Blank out fenced code blocks so their contents are not read as ledger content."""
    lines: list[str] = []
    inside = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            inside = not inside
            lines.append("")
            continue
        lines.append("" if inside else line)
    return "\n".join(lines)


def parse_keys(text: str, stop_at_heading: bool = True) -> dict[str, list[str]]:
    """Collect 'key: value' lines; with stop_at_heading, stop at the first '## ' heading."""
    keys: dict[str, list[str]] = {}
    for line in strip_fences(text).splitlines():
        if stop_at_heading and line.startswith("## "):
            break
        match = KEY_LINE.match(line)
        if match:
            keys.setdefault(match.group(1), []).append((match.group(2) or "").strip())
    return keys


def first(keys: dict[str, list[str]], name: str) -> str | None:
    values = keys.get(name)
    return values[0] if values else None


def list_items(text: str, key: str) -> list[str]:
    """The '- item' lines that follow 'key:' up to the next key line or heading."""
    items: list[str] = []
    inside = False
    for line in text.splitlines():
        match = KEY_LINE.match(line)
        if match:
            inside = match.group(1) == key
            continue
        if line.startswith("#"):
            inside = False
            continue
        if inside and line.startswith("- "):
            items.append(line[2:].strip())
    return items


def split_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def contract_version(value: str) -> str:
    parts = value.split()
    return parts[0] if parts else ""


def ledger_name(keys: dict[str, list[str]]) -> str:
    return (first(keys, "ledger") or "").split(" — ", 1)[0].strip()


def code_path(keys: dict[str, list[str]]) -> str | None:
    value = first(keys, "code") or "none"
    return None if value == "none" else value.split(" @ ", 1)[0].strip()


def pointer(value: str | None) -> str | None:
    """'checkpoints/T01.md (2026-10-09)' -> 'checkpoints/T01.md'; 'none' -> None."""
    if not value or value == "none":
        return None
    return value.split(" (", 1)[0].strip()


def load_index(ledger: Path) -> list[dict]:
    data = json.loads(read_text(ledger / "tasks" / "index.json"))
    if not isinstance(data, list) or not all(isinstance(row, dict) for row in data):
        raise ValueError("tasks/index.json must be a JSON list of objects")
    return data


def index_row_errors(row: dict) -> list[str]:
    """Fields unsafe for index consumers; leave status/dependency semantics to checks."""
    errors = [field for field in INDEX_FIELDS if field not in row]
    for field in ("id", "phase", "title", "task", "status", "project", "root"):
        if field in row and (not isinstance(row[field], str) or not row[field].strip()):
            errors.append(field)
    for field in ("successor", "checkpoint"):
        if field in row and row[field] is not None and (not isinstance(row[field], str) or not row[field].strip()):
            errors.append(field)
    if "deps" in row and (not isinstance(row["deps"], list)
                          or not all(isinstance(dep, str) and dep.strip() for dep in row["deps"])):
        errors.append("deps")
    return errors


def links(text: str) -> list[str]:
    """Relative or absolute file targets of markdown links, without anchors."""
    targets: list[str] = []
    for target in LINK.findall(strip_fences(text)):
        if target.startswith("#") or SCHEME.match(target):
            continue
        targets.append(target.split("#", 1)[0])
    return targets


def table_first_column(text: str, heading: str) -> list[str]:
    """First-column values of the markdown table under '## <heading>'."""
    values: list[str] = []
    inside = separator_seen = False
    for line in text.splitlines():
        if line.startswith("## "):
            inside = line[3:].strip().lower() == heading.lower()
            separator_seen = False
            continue
        if not inside or not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not separator_seen:
            separator_seen = all(SEPARATOR_CELL.fullmatch(cell) for cell in cells if cell)
            continue
        if cells and cells[0]:
            values.append(cells[0])
    return values


def step_ids(text: str) -> list[str]:
    return [match.group(1) for line in text.splitlines() if (match := STEP.match(line))]


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, strict=True)
        rows = list(reader)
    fields = list(reader.fieldnames or [])
    if not fields or len(fields) != len(set(fields)) or any(not field for field in fields):
        raise csv.Error("CSV needs nonempty, unique column names")
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        raise csv.Error("CSV row width differs from its header")
    return fields, rows


def is_under(path: str, root: str) -> bool:
    path = Path(posixpath.normpath(path.strip()))
    root = Path(posixpath.normpath(root.strip()))
    return path.is_relative_to(root) and ".." not in path.relative_to(root).parts
