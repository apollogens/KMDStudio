import json
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from evals.judge import CT, MAIN_TYPE, OFFICE_REL, REL, W, assess, read_trace
from evals.run import make_smoke, run_bounded

TURN = {"type": "turn.completed", "usage": {"input_tokens": 120}}


def event(kind, **values):
    return {"type": "item.completed", "item": {"type": kind, **values}}


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.work = Path(temp.name)

    def test_smoke_requires_successful_fixture_access_and_exact_final_text(self):
        case = make_smoke()
        self.assertNotEqual(case["fixture"], make_smoke()["fixture"])
        self.assertNotIn(case["smoke"], case["prompt"])
        read = event("command_execution", command=f"Get-Content {case['fixture_name']}",
                     aggregated_output=case["fixture"], status="completed", exit_code=0)
        correct = event("agent_message", text=case["smoke"])
        result = assess(self.work, case, [read, correct, TURN])
        self.assertTrue(result["fixture_access"])
        self.assertEqual(result["acceptance"], "PASS")
        for events in (
            [correct, TURN],
            [read, correct, event("agent_message", text="different"), TURN],
            [read, event("agent_message", text="different"), TURN],
            [{"type": "item.completed", "item": read["item"] | {"exit_code": 1}},
             correct, TURN],
        ):
            with self.subTest(events=events):
                self.assertEqual(assess(self.work, case, events)["task"], "FAIL")

    def test_failed_command_is_not_task_success(self):
        failure = event("command_execution", status="failed", exit_code=1)
        report = assess(self.work, {}, [failure, TURN])
        self.assertEqual((report["transport"], report["status"], report["failed_commands"]),
                         ("PASS", "FAIL", 1))

    def test_missing_or_incorrect_artifact_after_completed_turn(self):
        case = {"artifacts": ["status.docx"], "required_text": ["Source title"]}
        report = assess(self.work, case, [TURN])
        self.assertEqual((report["artifact"], report["reason"]), ("FAIL", "missing artifact"))
        artifact = self.work / "status.docx"
        with ZipFile(artifact, "w") as package:
            package.writestr("[Content_Types].xml",
                             f'<Types xmlns="{CT[1:-1]}"><Override PartName="/word/document.xml" '
                             f'ContentType="{MAIN_TYPE}"/></Types>')
            package.writestr("_rels/.rels",
                             f'<Relationships xmlns="{REL[1:-1]}"><Relationship '
                             f'Id="rId1" Target="word/document.xml" Type="{OFFICE_REL}"/></Relationships>')
            package.writestr("word/document.xml", (
                f'<w:document xmlns:w="{W[1:-1]}"><w:body>'
                '<w:p><w:r><w:t>Different title</w:t></w:r></w:p></w:body></w:document>'
            ))
        self.assertEqual(assess(self.work, case, [TURN])["artifact"], "FAIL")
        case["required_text"] = ["Different title"]
        match = assess(self.work, case, [TURN])
        self.assertEqual((match["artifact"], match["task"], match["acceptance"]),
                         ("PASS", "PASS", "NOT RUN"))

    def test_incomplete_jsonl_never_passes_even_after_completed_turn(self):
        path = self.work / "trace"
        path.write_bytes(json.dumps(TURN).encode() + b'\n{"type":')
        records, error = read_trace(path)
        report = assess(self.work, {}, records, trace_error=error)
        self.assertTrue(report["turn_completed"])
        self.assertEqual((report["transport"], report["trace"], report["status"]),
                         ("PASS", "BLOCKED", "BLOCKED"))

    def test_process_timeout_has_bounded_cleanup(self):
        paths = self.work / "stdout", self.work / "stderr"
        reason = run_bounded([sys.executable, "-I", "-B", "-c", "import time; time.sleep(10)"],
                             self.work, paths, timeout=.3)
        self.assertTrue(reason.startswith("timeout"), reason)
        report = assess(self.work, {}, [], stop_reason=reason)
        self.assertEqual((report["transport"], report["status"]), ("BLOCKED", "BLOCKED"))
