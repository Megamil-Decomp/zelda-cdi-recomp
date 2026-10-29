"""Synthetic CPU/MMIO-boundary regression, without BIOS or commercial media."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / "upstream-cdirecomp"


class InterpreterFetchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("cc")
        if compiler is None or not (UPSTREAM / "runner/src/m68k_interp.c").is_file():
            raise unittest.SkipTest("requires the audited local checkout and cc")
        cls.temp = tempfile.TemporaryDirectory(prefix="cdi-fetch-regression-")
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name)
        for relative in ("runner/src/m68k_interp.c", "runner/include/m68k_interp.h"):
            destination = cls.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(UPSTREAM / relative, destination)
        subprocess.run(["patch", "--batch", "-p1", "-i", str(ROOT /
                        "scripts/patches/0008-interpreter-decode-window.patch")],
                       cwd=cls.root, check=True, capture_output=True, text=True, timeout=10)
        common = UPSTREAM / "external/m68k-recomp-core/common"
        for version, source in (("before", UPSTREAM / "runner/src/m68k_interp.c"),
                                ("after", cls.root / "runner/src/m68k_interp.c")):
            command = [compiler, "-std=c11", "-O0", "-I" + str(cls.root / "runner/include"),
                       "-I" + str(UPSTREAM / "runner/include"), "-I" + str(common),
                       "-I" + str(UPSTREAM / "recompiler/src"),
                       str(ROOT / "tests/native/interpreter_fetch_fixture.c"), str(source),
                       str(UPSTREAM / "runner/src/m68k_arith.c"), str(common / "m68k_decoder.c"),
                       str(UPSTREAM / "recompiler/src/rom_parser.c"), "-o", str(cls.root / version)]
            subprocess.run(command, check=True, capture_output=True, text=True, timeout=60)

    def run_case(self, case, version="after"):
        return subprocess.run([str(self.root / version), case], capture_output=True,
                              text=True, timeout=10)

    def test_original_speculative_fetch_touches_forbidden_mmio(self):
        result = self.run_case("short", "before")
        self.assertEqual(result.returncode, 90)
        self.assertIn("forbidden synthetic bus read", result.stderr)

    def test_short_instruction_before_mmio_preserves_interrupt_status(self):
        result = self.run_case("short")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_unfetchable_pc_is_rejected_without_mmio_read(self):
        result = self.run_case("invalid")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_required_extension_bytes_are_not_synthesized(self):
        result = self.run_case("truncated")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_ram_end_does_not_fetch_next_unmapped_region(self):
        result = self.run_case("ram-end")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_real_operand_bus_error_still_takes_existing_exception(self):
        for version in ("before", "after"):
            with self.subTest(version=version):
                result = self.run_case("operand-fault", version)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_ordinary_instruction_retains_result_and_program_counter(self):
        for version in ("before", "after"):
            with self.subTest(version=version):
                result = self.run_case("ordinary", version)
                self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
