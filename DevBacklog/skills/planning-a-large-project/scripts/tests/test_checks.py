"""Validation, query and cost behavior of ledger.py on directory-profile ledgers."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

LEDGER_PY = Path(__file__).resolve().parents[1] / "ledger.py"


def run_ledger(*args: str) -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run([sys.executable, "-B", str(LEDGER_PY), *args], capture_output=True, text=True, env=env)


def task_text(task_id: str, requirements: str, owns: str) -> str:
    return (
        f"# {task_id} — Task {task_id}\n\n"
        f"Loaded when: executing or reviewing {task_id}. Up: [STATE](../STATE.md)\n\n"
        f"outcome: output of {task_id}\n"
        f"requirements: {requirements}\n"
        "entry: predecessor accepted\n"
        f"owns: {owns}\n"
        "checks: unit profile\n"
        f"exit: checkpoint checkpoints/{task_id}.md; successor none\n\n"
        "## Steps\n\n"
        f"- [ ] {task_id}.1 Do the work — done when it exists\n\n"
        "## Record\n\nnot started\n"
    )


def checkpoint_text(task_id: str, acceptance: str) -> str:
    return (
        f"# {task_id} checkpoint — accepted\n\n"
        f"Loaded when: reviewing or resuming {task_id}. Up: [STATE](../STATE.md)\n\n"
        "kind: accepted\n"
        f"task: {task_id} / {task_id}.1; plan revision 1; predecessor none; time 2026-10-09T00:00:00Z\n"
        "artifact: code none; ledger uncommitted\n"
        "findings: none\n"
        "limits: none\n"
        f"acceptance: {acceptance}\n"
        "next: none\n"
    )


class LedgerCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.ledger = Path(self.tmp.name) / "ledger"
        result = run_ledger(
            "init", "--profile", "directory", "--name", "demo", "--path", str(self.ledger),
            "--objective", "demo objective",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def read(self, rel: str) -> str:
        return (self.ledger / rel).read_text(encoding="utf-8")

    def write(self, rel: str, text: str) -> None:
        path = self.ledger / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def replace(self, rel: str, old: str, new: str) -> None:
        text = self.read(rel)
        self.assertIn(old, text)
        self.write(rel, text.replace(old, new, 1))

    def index(self) -> list[dict]:
        return json.loads(self.read("tasks/index.json"))

    def save_index(self, rows: list[dict]) -> None:
        self.write("tasks/index.json", json.dumps(rows, indent=2) + "\n")

    def add_task(self, task_id: str, status: str = "planned", deps: list[str] | None = None,
                 checkpoint: str | None = None, requirements: str = "none", owns: str = "src/",
                 **extra: str) -> None:
        rows = self.index()
        rows.append({
            "id": task_id, "phase": "P0", "title": f"Task {task_id}", "task": f"tasks/{task_id}.md",
            "deps": deps or [], "status": status, "successor": None, "checkpoint": checkpoint, **extra,
        })
        self.save_index(rows)
        self.write(f"tasks/{task_id}.md", task_text(task_id, requirements, owns))

    def add_checkpoint(self, task_id: str, acceptance: str) -> str:
        rel = f"checkpoints/{task_id}.md"
        self.write(rel, checkpoint_text(task_id, acceptance))
        return rel

    def validate(self) -> subprocess.CompletedProcess:
        return run_ledger("validate", "--ledger", str(self.ledger))

    def assertFinding(self, result: subprocess.CompletedProcess, level: str, rule: str) -> None:
        self.assertIn(f"{level} {rule} ", result.stdout, result.stdout)

    def assertNoFinding(self, result: subprocess.CompletedProcess, rule: str) -> None:
        self.assertNotIn(f" {rule} ", result.stdout, result.stdout)


class SkeletonTests(LedgerCase):
    def test_required_ledger_files_are_diagnosed(self) -> None:
        for rel, rule in (("STATE.md", "state.missing"), ("tasks/index.json", "index.missing"),
                          ("PROTOCOL.md", "protocol.missing"), ("PLAN.md", "plan.missing")):
            with self.subTest(file=rel):
                text = self.read(rel)
                (self.ledger / rel).unlink()
                self.assertFinding(self.validate(), "ERROR", rule)
                self.write(rel, text)

    def test_new_ledger_has_no_findings(self) -> None:
        result = self.validate()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("validate: 0 errors, 0 warnings", result.stdout)

    def test_legacy_contract_reports_one_error_and_stops(self) -> None:
        self.replace("STATE.md", "contract: 3 ", "contract: 2 ")
        result = self.validate()
        self.assertEqual(result.returncode, 1)
        self.assertFinding(result, "ERROR", "state.contract")
        self.assertEqual(result.stdout.count("ERROR"), 1, result.stdout)


class StateTests(LedgerCase):
    def test_invalid_lifecycle(self) -> None:
        self.replace("STATE.md", "lifecycle: planning", "lifecycle: finished")
        self.assertFinding(self.validate(), "ERROR", "state.lifecycle")

    def test_checkpoint_pointers_must_resolve(self) -> None:
        self.replace("STATE.md", "accepted: none", "accepted: checkpoints/missing.md (2026-10-09)")
        self.replace("STATE.md", "recovery: none", "recovery: checkpoints/missing.md")
        result = self.validate()
        self.assertFinding(result, "ERROR", "state.accepted")
        self.assertFinding(result, "ERROR", "state.recovery")

    def test_cursor_phase_must_match_index(self) -> None:
        self.replace("STATE.md", "cursor: P0 /", "cursor: P99 /")
        self.assertFinding(self.validate(), "ERROR", "state.cursor")

    def test_cursor_step_must_exist(self) -> None:
        self.replace("STATE.md", "PREP-01.1 —", "PREP-01.99 —")
        self.assertFinding(self.validate(), "ERROR", "state.cursor")

    def test_read_cannot_load_an_oversized_file(self) -> None:
        self.write("evidence/big.txt", "x" * 17000)
        self.replace("STATE.md", "read: PROTOCOL.md", "read: evidence/big.txt, PROTOCOL.md")
        self.assertFinding(self.validate(), "ERROR", "links.boot")

    def test_budget(self) -> None:
        self.write("STATE.md", self.read("STATE.md") + "filler line for budget\n" * 100)
        self.assertFinding(self.validate(), "ERROR", "size.budget")

    def test_long_line(self) -> None:
        self.write("STATE.md", self.read("STATE.md") + "x" * 450 + "\n")
        self.assertFinding(self.validate(), "ERROR", "size.line")

    def test_duplicate_key(self) -> None:
        self.write("STATE.md", self.read("STATE.md") + "next: a second action\n")
        self.assertFinding(self.validate(), "ERROR", "state.keys")

    def test_missing_key(self) -> None:
        self.replace("STATE.md", "pending: none\n", "")
        self.assertFinding(self.validate(), "ERROR", "state.keys")

    def test_cursor_status_must_match_index(self) -> None:
        self.replace("STATE.md", "— in_progress", "— review")
        self.assertFinding(self.validate(), "ERROR", "state.cursor")

    def test_cursor_task_must_exist(self) -> None:
        self.replace("STATE.md", "P0 / PREP-01 / PREP-01.1", "P0 / T99 / T99.1")
        self.assertFinding(self.validate(), "ERROR", "state.cursor")

    def test_read_paths_must_exist(self) -> None:
        self.replace("STATE.md", "read: PROTOCOL.md", "read: tasks/T99.md, PROTOCOL.md")
        self.assertFinding(self.validate(), "ERROR", "state.read")


class IndexTests(LedgerCase):
    def test_invalid_json_shape(self) -> None:
        for value in ("not json", "{}", "[1]"):
            with self.subTest(value=value):
                self.write("tasks/index.json", value)
                self.assertFinding(self.validate(), "ERROR", "index.json")

    def test_duplicate_ids(self) -> None:
        self.save_index(self.index() * 2)
        self.assertFinding(self.validate(), "ERROR", "index.unique")

    def test_unknown_status_successor_and_task_file(self) -> None:
        self.save_index([{**self.index()[0], "status": "finished", "successor": "MISSING", "task": "tasks/missing.md"}])
        result = self.validate()
        for rule in ("index.status", "index.successor", "index.task"):
            with self.subTest(rule=rule):
                self.assertFinding(result, "ERROR", rule)

    def test_done_needs_an_acceptance_bearing_checkpoint_kind(self) -> None:
        checkpoint = self.add_checkpoint("T01", "policy boundary")
        self.replace(checkpoint, "kind: accepted", "kind: unknown")
        self.add_task("T01", status="done", checkpoint=checkpoint)
        self.assertFinding(self.validate(), "ERROR", "index.acceptance")

    def test_checkpoint_must_be_in_checkpoints_directory(self) -> None:
        self.write("evidence/T01.md", checkpoint_text("T01", "policy boundary"))
        self.add_task("T01", status="done", checkpoint="evidence/T01.md")
        self.assertFinding(self.validate(), "ERROR", "index.checkpoint")

    def test_malformed_index_values_report_findings_without_tracebacks(self) -> None:
        original = self.index()[0]
        for field, value in (("id", []), ("id", 1), ("task", []), ("phase", {}),
                             ("deps", [[]]), ("status", None), ("successor", {}),
                             ("checkpoint", []), ("root", [])):
            with self.subTest(field=field, value=value):
                self.save_index([{**original, field: value}])
                result = self.validate()
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("ERROR index.", result.stdout)
                self.assertNotIn("Traceback", result.stderr)

    def test_done_checkpoint_must_belong_to_the_task(self) -> None:
        self.add_task("T01", status="done", checkpoint=self.add_checkpoint("OTHER", "policy boundary"))
        self.assertFinding(self.validate(), "ERROR", "index.acceptance")

    def test_recovery_checkpoint_cannot_accept_a_task(self) -> None:
        checkpoint = self.add_checkpoint("T01", "policy boundary")
        self.replace(checkpoint, "kind: accepted", "kind: recovery")
        self.add_task("T01", status="done", checkpoint=checkpoint)
        self.assertFinding(self.validate(), "ERROR", "index.acceptance")

    def test_nested_checkpoint_acceptance_is_validated(self) -> None:
        self.write("checkpoints/batch/T01.md", checkpoint_text("T01", "nonsense"))
        self.add_task("T01", status="done", checkpoint="checkpoints/batch/T01.md")
        self.assertFinding(self.validate(), "ERROR", "checkpoint.acceptance")

    def test_missing_dependency(self) -> None:
        self.add_task("T01", deps=["T00"])
        self.assertFinding(self.validate(), "ERROR", "index.deps")

    def test_cycle(self) -> None:
        self.add_task("T01", deps=["T02"])
        self.add_task("T02", deps=["T01"])
        self.assertFinding(self.validate(), "ERROR", "index.cycle")

    def test_done_needs_checkpoint(self) -> None:
        self.add_task("T01", status="done")
        self.assertFinding(self.validate(), "ERROR", "index.checkpoint")

    def test_done_needs_acceptance(self) -> None:
        checkpoint = self.add_checkpoint("T01", "pending")
        self.add_task("T01", status="done", checkpoint=checkpoint)
        self.assertFinding(self.validate(), "ERROR", "index.acceptance")

    def test_done_with_policy_acceptance_is_clean(self) -> None:
        checkpoint = self.add_checkpoint("T01", "policy boundary")
        self.add_task("T01", status="done", checkpoint=checkpoint)
        result = self.validate()
        self.assertEqual(result.returncode, 0, result.stdout)


class CheckpointTests(LedgerCase):
    def test_missing_checkpoint_keys(self) -> None:
        self.write("checkpoints/T01.md", "acceptance: pending\n")
        self.assertFinding(self.validate(), "ERROR", "checkpoint.keys")

    def test_human_stop_class_cannot_accept_by_policy(self) -> None:
        self.replace("PROTOCOL.md", "stop classes:\n", "stop classes:\n- review: every remediation task → stop for human acceptance\n")
        self.add_checkpoint("T01", "policy review")
        self.assertFinding(self.validate(), "ERROR", "checkpoint.acceptance")

    def test_policy_class_must_be_declared(self) -> None:
        self.add_checkpoint("T01", "policy nightly")
        self.assertFinding(self.validate(), "ERROR", "checkpoint.acceptance")

    def test_human_acceptance_needs_a_quote(self) -> None:
        self.add_checkpoint("T01", "human approved")
        self.assertFinding(self.validate(), "ERROR", "checkpoint.acceptance")

    def test_quoted_human_acceptance_is_clean(self) -> None:
        self.add_checkpoint("T01", 'human "accept T01" (chat, 2026-10-09)')
        self.assertNoFinding(self.validate(), "checkpoint.acceptance")


class TaskTests(LedgerCase):
    def test_owned_path_cannot_escape_dot_root(self) -> None:
        self.add_task("T01", owns="../outside/file", root=".")
        self.assertFinding(self.validate(), "ERROR", "task.owns")

    def test_owned_path_cannot_escape_root_with_dotdot(self) -> None:
        self.add_task("T01", owns="src/../outside/file", root="src")
        self.assertFinding(self.validate(), "ERROR", "task.owns")

    def test_step_from_another_task(self) -> None:
        self.add_task("T01")
        self.replace("tasks/T01.md", "- [ ] T01.1", "- [ ] T02.1")
        self.assertFinding(self.validate(), "ERROR", "task.steps")

    def test_owned_path_outside_root(self) -> None:
        self.add_task("T01", owns="wks/other/src.rs", root="wks/mine")
        self.assertFinding(self.validate(), "ERROR", "task.owns")

    def test_missing_key(self) -> None:
        self.add_task("T01")
        self.replace("tasks/T01.md", "owns: src/\n", "")
        self.assertFinding(self.validate(), "ERROR", "task.keys")

    def test_unindexed_task_file_warns(self) -> None:
        self.write("tasks/T09.md", task_text("T09", "none", "src/"))
        self.assertFinding(self.validate(), "WARN", "task.index")


class PlanTests(LedgerCase):
    def test_missing_phase_table_errors_after_planning(self) -> None:
        self.replace("PLAN.md", "## Phases", "## NotPhases")
        self.replace("STATE.md", "lifecycle: planning", "lifecycle: ready")
        self.assertFinding(self.validate(), "ERROR", "plan.phases")

    def add_requirement(self) -> None:
        separator = "| --- | --- | --- | --- |\n"
        self.replace("PLAN.md", separator, separator + "| R1 | Keep records | user | count matches |\n")

    def test_uncovered_requirement_warns_while_planning(self) -> None:
        self.add_requirement()
        self.assertFinding(self.validate(), "WARN", "plan.coverage")

    def test_uncovered_requirement_errors_after_planning(self) -> None:
        self.add_requirement()
        self.replace("STATE.md", "lifecycle: planning", "lifecycle: executing")
        self.assertFinding(self.validate(), "ERROR", "plan.coverage")

    def test_covered_requirement_is_clean(self) -> None:
        self.add_requirement()
        self.add_task("T01", requirements="R1")
        self.assertNoFinding(self.validate(), "plan.coverage")


class ContentTests(LedgerCase):
    def test_protocol_needs_required_keys_and_a_stop_class(self) -> None:
        self.replace("PROTOCOL.md", "session:", "removed:")
        self.replace("PROTOCOL.md", "- boundary: every task boundary → continue after the reviewed checkpoint\n", "")
        result = self.validate()
        self.assertFinding(result, "ERROR", "protocol.keys")
        self.assertFinding(result, "ERROR", "protocol.stop_classes")

    def test_task_link_to_large_file_warns(self) -> None:
        self.write("evidence/big.txt", "x" * 17000)
        self.add_task("T01")
        self.write("tasks/T01.md", self.read("tasks/T01.md") + "\nSee [data](../evidence/big.txt)\n")
        self.assertFinding(self.validate(), "WARN", "links.large")

    def test_invalid_csv_is_a_parse_finding(self) -> None:
        for text in ('name,basis\n"unclosed,read\n', 'name,basis\nx,read,extra\n', 'name,basis\nx\n'):
            with self.subTest(text=text):
                self.write("evidence/tests.csv", text)
                self.assertFinding(self.validate(), "ERROR", "csv.parse")

    def test_large_file_allowlist_requires_a_reason(self) -> None:
        self.write("evidence/blob.txt", "x" * (1024 * 1024 + 1))
        self.write("evidence/large-files.txt", "evidence/blob.txt\n")
        self.assertFinding(self.validate(), "ERROR", "files.large")

    def test_boot_link_to_large_file(self) -> None:
        self.write("evidence/big.md", "word " * 4000)
        self.write("PLAN.md", self.read("PLAN.md") + "\nDetails: [big](evidence/big.md)\n")
        self.assertFinding(self.validate(), "ERROR", "links.boot")

    def test_broken_link(self) -> None:
        self.write("PLAN.md", self.read("PLAN.md") + "\nSee [missing](research/missing.md)\n")
        self.assertFinding(self.validate(), "ERROR", "links.target")

    def test_csv_needs_provenance(self) -> None:
        self.write("evidence/tests.csv", "project,test\n" + "".join(f"p,t{i}\n" for i in range(21)))
        self.assertFinding(self.validate(), "ERROR", "csv.provenance")

    def test_csv_with_provenance_is_clean(self) -> None:
        rows = "".join(f"p{i},t{i},script,\n" for i in range(21))
        self.write("evidence/tests.csv", "project,test,basis,verified_by\n" + rows)
        result = self.validate()
        self.assertNoFinding(result, "csv.provenance")
        self.assertNoFinding(result, "csv.constant")

    def test_csv_unknown_basis(self) -> None:
        rows = "".join(f"p{i},t{i},guess,\n" for i in range(21))
        self.write("evidence/tests.csv", "project,test,basis,verified_by\n" + rows)
        self.assertFinding(self.validate(), "ERROR", "csv.provenance")

    def test_csv_constant_column_warns(self) -> None:
        rows = "".join(f"p{i},unit,script,\n" for i in range(21))
        self.write("evidence/tests.csv", "project,scope,basis,verified_by\n" + rows)
        self.assertFinding(self.validate(), "WARN", "csv.constant")

    def test_repeated_lines_warn(self) -> None:
        for number in range(5):
            self.write(f"research/note{number}.md", "This sentence is copied into every research note verbatim.\n")
        self.assertFinding(self.validate(), "WARN", "repeat.lines")

    def test_large_file_needs_allowlist(self) -> None:
        self.write("evidence/blob.txt", "x" * (1024 * 1024 + 1))
        self.assertFinding(self.validate(), "ERROR", "files.large")
        self.write("evidence/large-files.txt", "evidence/blob.txt — reference corpus that cannot be regenerated\n")
        self.assertNoFinding(self.validate(), "files.large")

    def test_bytecode_is_rejected(self) -> None:
        self.write("evidence/__pycache__/oracle.cpython-314.pyc", "")
        self.assertFinding(self.validate(), "ERROR", "files.bytecode")


class QueryAndCostTests(LedgerCase):
    def test_query_malformed_index_returns_usage_error(self) -> None:
        self.save_index([{**self.index()[0], "id": []}])
        result = run_ledger("query", "--ledger", str(self.ledger), "--next")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_next_lists_tasks_whose_dependencies_are_done(self) -> None:
        rows = self.index()
        rows[0]["status"] = "done"
        rows[0]["checkpoint"] = self.add_checkpoint("PREP-01", "policy boundary")
        self.save_index(rows)
        self.add_task("T01", deps=["PREP-01"])
        self.add_task("T02", deps=["T01"])
        result = run_ledger("query", "--ledger", str(self.ledger), "--next")
        self.assertIn("T01", result.stdout)
        self.assertNotIn("T02", result.stdout)

    def test_task_shows_dependency_status(self) -> None:
        self.add_task("T01")
        self.add_task("T02", deps=["T01"])
        result = run_ledger("query", "--ledger", str(self.ledger), "--task", "T02")
        self.assertIn("dependency T01: planned", result.stdout)

    def test_csv_filter(self) -> None:
        self.write("evidence/tests.csv", "project,test,basis,verified_by\na,t1,script,\nb,t2,script,\na,t3,script,\n")
        result = run_ledger(
            "query", "--ledger", str(self.ledger), "--csv", "evidence/tests.csv",
            "--where", "project=a", "--columns", "test",
        )
        self.assertEqual(result.stdout.split(), ["test", "t1", "t3"])

    def test_cost_reports_resume_set(self) -> None:
        result = run_ledger("cost", "--ledger", str(self.ledger))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("resume set", result.stdout)
        self.assertIn("STATE.md", result.stdout)


if __name__ == "__main__":
    unittest.main()
