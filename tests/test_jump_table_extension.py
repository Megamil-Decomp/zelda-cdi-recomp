"""Regress the private upstream adaptation using author-written machine code.

The audited local checkout and a C compiler are optional test prerequisites.
No BIOS, disc, generated commercial code, or downloaded dependency is used.
"""
import hashlib
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / "upstream-cdirecomp"
RELATIVE = Path("external/m68k-recomp-core/profiles/scc68070/code_generator.c")


class JumpTableExtensionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("cc")
        if compiler is None or not (UPSTREAM / RELATIVE).is_file():
            raise unittest.SkipTest("requires the audited local upstream checkout and cc")
        cls.original_digest = hashlib.sha256((UPSTREAM / RELATIVE).read_bytes()).digest()
        cls.temporary = tempfile.TemporaryDirectory(prefix="cdi-table-regression-")
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.root = Path(cls.temporary.name)
        copy = cls.root / RELATIVE
        copy.parent.mkdir(parents=True)
        shutil.copy2(UPSTREAM / RELATIVE, copy)
        subprocess.run(["patch", "--batch", "-p1", "-i", str(ROOT /
                        "scripts/patches/0007-jump-table-extension-guard.patch")],
                       cwd=cls.root, check=True, capture_output=True, text=True, timeout=10)
        core = UPSTREAM / "external/m68k-recomp-core"
        common, profile = core / "common", core / "profiles/scc68070"
        sources = [ROOT / "tests/native/jump_table_extension_fixture.c",
                   common / "m68k_decoder.c", common / "m68k_validator.c",
                   common / "annotations.c", profile / "function_finder.c",
                   profile / "codegen_diag.c", UPSTREAM / "recompiler/src/rom_parser.c",
                   UPSTREAM / "recompiler/src/game_config.c", UPSTREAM / "recompiler/src/toml.c"]
        for version, generator in (("before", UPSTREAM / RELATIVE), ("after", copy)):
            command = [compiler, "-std=c11", "-O0", "-I" + str(common),
                       "-I" + str(profile), "-I" + str(UPSTREAM / "recompiler/src"),
                       *map(str, sources), str(generator), "-o", str(cls.root / version)]
            subprocess.run(command, check=True, capture_output=True, text=True, timeout=60)

    def run_fixture(self, version, case):
        output = self.root / (version + "-" + case)
        output.mkdir(exist_ok=True)
        result = subprocess.run([str(self.root / version), str(output), case],
                                capture_output=True, text=True, timeout=10)
        return result, (output / "full.c").read_text()

    def test_original_failure_is_reproduced_by_synthetic_extension(self):
        result, _ = self.run_fixture("before", "interior")
        self.assertEqual(result.returncode, 1)
        self.assertIn("INVALID_STORE_EA", result.stderr)
        self.assertIn("fixture_emitted=0", result.stdout)

    def test_guard_keeps_computed_fallback_without_speculative_data_code(self):
        result, generated = self.run_fixture("after", "interior")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("diagnostics=0", result.stdout)
        self.assertIn("hybrid_jmp_interpret", generated)
        self.assertNotIn("cannot store to EA", generated)

    def test_real_table_outside_instruction_remains_supported(self):
        for version in ("before", "after"):
            with self.subTest(version=version):
                result, generated = self.run_fixture(version, "external")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("$000060", generated)
                self.assertIn("$000064", generated)

    def test_upstream_source_is_unchanged(self):
        self.assertEqual(hashlib.sha256((UPSTREAM / RELATIVE).read_bytes()).digest(),
                         self.original_digest)


if __name__ == "__main__":
    unittest.main()
