"""Session diagnostics use synthetic child processes and fake signal results."""
import contextlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_faces_rea_candidate as launcher


class CandidateSessionTests(unittest.TestCase):
    def test_abort_and_shutdown_are_not_conflated(self):
        crash = launcher.exit_observation(-6)
        self.assertEqual(crash["kind"], "signal")
        self.assertEqual(crash["signal"], "SIGABRT")
        self.assertEqual(crash["shell_status"], 134)
        clean = launcher.exit_observation(0)
        self.assertEqual(clean["kind"], "exited")
        self.assertIsNone(clean["signal"])
        self.assertEqual(clean["shell_status"], 0)

    def test_nonzero_exit_and_unknown_are_distinct(self):
        self.assertEqual(launcher.exit_observation(3)["returncode"], 3)
        for value in (None, True, "0"):
            self.assertEqual(launcher.exit_observation(value)["kind"], "unknown")

    def test_real_synthetic_child_persists_command_and_exit_status(self):
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()):
            log = Path(temp) / "session.log"
            command = [sys.executable, "-c", "print('synthetic child'); raise SystemExit(3)"]
            result = launcher.run_session(command, os.environ.copy(), log)
            report = json.loads(log.with_suffix(".json").read_text())
            self.assertEqual(result, 3)
            self.assertEqual(report["state"], "finished")
            self.assertEqual(report["exit"]["returncode"], 3)
            self.assertEqual(report["command"], command)
            self.assertIn("synthetic child", log.read_text())
            self.assertFalse(report["hang_established"])
            with self.assertRaises(FileExistsError):
                launcher.run_session(command, os.environ.copy(), log)

    def test_crashed_child_leaves_report_instead_of_only_empty_log_tail(self):
        class Child:
            pid = 123
            returncode = -6
            def wait(self): return self.returncode
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()), \
                patch.object(launcher.subprocess, "Popen", return_value=Child()):
            log = Path(temp) / "crashed.log"
            result = launcher.run_session([sys.executable], os.environ.copy(), log)
            report = json.loads(log.with_suffix(".json").read_text())
            self.assertEqual(result, 134)
            self.assertEqual(report["exit"]["signal"], "SIGABRT")

    def test_process_launch_failure_is_recorded(self):
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()), \
                patch.object(launcher.subprocess, "Popen", side_effect=OSError("synthetic launch failure")):
            log = Path(temp) / "failed.log"
            result = launcher.run_session([sys.executable], os.environ.copy(), log)
            report = json.loads(log.with_suffix(".json").read_text())
            self.assertEqual(result, 2)
            self.assertEqual(report["state"], "launch_failed")
            self.assertIn("synthetic launch failure", report["error"])


if __name__ == "__main__":
    unittest.main()
