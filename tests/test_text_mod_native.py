"""Compile and exercise the original text-view helper with synthetic RAM."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class NativeTextModTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("clang") or shutil.which("cc")
        if not compiler:
            raise unittest.SkipTest("C compiler required for native adapter fixture")
        cls.temp = tempfile.TemporaryDirectory()
        cls.directory = Path(cls.temp.name)
        source = cls.directory / "fixture.c"
        source.write_text(r'''
#include "cdi_text_mod.h"
int main(int argc, char **argv) {
    CdiTextMod mod;
    if (argc != 2) return 10;
    if (!cdi_text_mod_load(&mod, argv[1])) return 2;
    uint8_t ram[] = "XEMPTY\0EMPTYX\0";
    uint8_t before[sizeof ram]; memcpy(before,ram,sizeof ram);
    char output[6]={0};
    for(unsigned i=0;i<5;i++) output[i]=cdi_text_mod_byte(&mod,ram,sizeof ram,i+1,ram[i+1]);
    if(memcmp(before,ram,sizeof ram)) return 3;
    if(cdi_text_mod_byte(&mod,ram,sizeof ram,7,ram[7]) != ram[7]) return 4;
    if(cdi_text_mod_byte(&mod,ram,4,3,ram[3]) != ram[3]) return 5;
    puts(output);return 0;
}
''')
        cls.binary = cls.directory / "fixture"
        include = Path(__file__).resolve().parents[1] / "app/native"
        subprocess.run([compiler, "-std=c11", "-Wall", "-Wextra", "-I", str(include),
                        str(source), "-o", str(cls.binary)], check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "temp"):
            cls.temp.cleanup()

    def run_config(self, content):
        path = self.directory / "mod.txt"
        path.write_text(content, encoding="utf-8")
        return subprocess.run([str(self.binary), str(path)], capture_output=True, text=True)

    def test_enabled_translation_preserves_original_bytes(self):
        result = self.run_config("enabled=true\nadventure.menu.empty=VAZIO\n")
        self.assertEqual((result.returncode, result.stdout.strip()), (0, "VAZIO"))

    def test_disabled_returns_original(self):
        result = self.run_config("enabled=false\nadventure.menu.empty=VAZIO\n")
        self.assertEqual((result.returncode, result.stdout.strip()), (0, "EMPTY"))

    def test_invalid_lengths_accents_and_unknown_keys_are_rejected(self):
        for value in ("VAZIOS", "VÁZIO", "", "vazio"):
            with self.subTest(value=value):
                result = self.run_config("enabled=true\nadventure.menu.empty=" + value + "\n")
                self.assertEqual(result.returncode, 2)
        self.assertEqual(self.run_config("enabled=true\nother=value\n").returncode, 2)

    def test_duplicate_and_missing_configuration_are_rejected(self):
        for content in ("enabled=true\n", "adventure.menu.empty=VAZIO\n",
                        "enabled=true\nenabled=false\nadventure.menu.empty=VAZIO\n"):
            with self.subTest(content=content):
                self.assertEqual(self.run_config(content).returncode, 2)
