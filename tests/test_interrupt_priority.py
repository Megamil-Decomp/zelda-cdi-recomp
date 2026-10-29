"""SCC68070 interrupt masking/frame regression with synthetic guest memory."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / "upstream-cdirecomp"


class InterruptPriorityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("cc")
        original = UPSTREAM / "runner/src/runtime.c"
        if compiler is None or not original.is_file():
            raise unittest.SkipTest("requires the audited local checkout and cc")
        cls.temp = tempfile.TemporaryDirectory(prefix="cdi-irq-regression-")
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name)
        patched = cls.root / "runner/src/runtime.c"
        patched.parent.mkdir(parents=True)
        shutil.copy2(original, patched)
        subprocess.run(["patch", "--batch", "-p1", "-i", str(ROOT /
                        "scripts/patches/0009-interrupt-priority-on-ack.patch")],
                       cwd=cls.root, check=True, capture_output=True, text=True, timeout=10)
        dead_strip = "-Wl,-dead_strip" if sys.platform == "darwin" else "-Wl,--gc-sections"
        for version, source in (("before", original), ("after", patched)):
            subprocess.run([compiler, "-std=c11", "-D_POSIX_C_SOURCE=200809L", "-O0",
                            "-ffunction-sections", "-fdata-sections",
                            "-I" + str(UPSTREAM / "runner/include"),
                            "-I" + str(UPSTREAM / "external/m68k-recomp-core/common"),
                            "-I" + str(UPSTREAM / "recompiler/src"),
                            str(ROOT / "tests/native/interrupt_priority_fixture.c"),
                            str(source), dead_strip, "-o", str(cls.root / version)],
                           check=True, capture_output=True, text=True, timeout=60)

    def run_case(self, case, version="after"):
        return subprocess.run([str(self.root / version), case], capture_output=True,
                              text=True, timeout=10)

    def test_original_entry_leaves_priority_and_trace_incorrect(self):
        result = self.run_case("entry", "before")
        self.assertEqual(result.returncode, 1)
        self.assertIn("SR=a215", result.stderr)

    def test_ack_sets_priority_preserving_original_status_in_frame(self):
        result = self.run_case("entry")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_same_priority_cannot_reenter_and_remains_pending(self):
        self.assertEqual(self.run_case("same-level", "before").returncode, 1)
        result = self.run_case("same-level")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_higher_priority_can_preempt_with_a_separate_frame(self):
        result = self.run_case("higher-level")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_onchip_irq_uses_its_level_and_vector(self):
        result = self.run_case("onchip")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_restoring_saved_frame_allows_next_interrupt(self):
        result = self.run_case("restore")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_masked_interrupt_keeps_state_and_request(self):
        for version in ("before", "after"):
            result = self.run_case("masked", version)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_no_landing_pad_keeps_pending_request(self):
        for version in ("before", "after"):
            result = self.run_case("unarmed", version)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
