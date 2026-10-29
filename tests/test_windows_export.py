"""Windows package/provenance checks use synthetic media and PE fixtures."""
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_windows_runtimes import accepted_inputs, digest, copy_changed, write_changed
from export_private_windows import pe_x64, check_imports, package_header


class WindowsExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def provenance(self):
        runtime = self.root / "build/runtime/CdiRuntime"
        paths = [self.root / "build/source/bios/generated/cdrtos_full.c",
                 self.root / "build/game/module_manifest.c"]
        for p in [runtime, *paths]:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(b"synthetic " + p.name.encode())
        report = {"runtime_sha256": digest(runtime),
                  "inputs": [{"path": str(p), "sha256": digest(p)} for p in paths]}
        runtime.with_name("CdiRuntime.build.json").write_text(json.dumps(report))
        return runtime, paths

    def test_accepts_only_identical_sources_for_the_accepted_runtime(self):
        runtime, paths = self.provenance()
        source, generated, _ = accepted_inputs(runtime, self.root)
        self.assertEqual(source, self.root / "build/source")
        self.assertEqual(generated, self.root / "build/game")
        paths[0].write_bytes(b"changed source")
        with self.assertRaisesRegex(ValueError, "source identity"):
            accepted_inputs(runtime, self.root)

    def test_stale_runtime_cannot_reuse_a_provenance_record(self):
        runtime, _ = self.provenance()
        runtime.write_bytes(b"changed runtime")
        with self.assertRaisesRegex(ValueError, "provenance mismatch"):
            accepted_inputs(runtime, self.root)

    def test_incremental_staging_preserves_timestamps_but_detects_changed_content(self):
        source, target = self.root / "source.c", self.root / "target.c"
        source.write_text("synthetic old"); target.write_text("synthetic old")
        os.utime(target, (100, 100))
        copy_changed(source, target)
        self.assertEqual(target.stat().st_mtime, 100)
        source.write_text("synthetic new")
        copy_changed(source, target)
        self.assertEqual(target.read_text(), "synthetic new")
        os.utime(target, (100, 100))
        write_changed(target, "synthetic new")
        self.assertEqual(target.stat().st_mtime, 100)

    def test_source_outside_private_build_is_rejected(self):
        runtime, paths = self.provenance()
        outside = self.root / "outside.c"
        paths[0].rename(outside)
        paths[0].symlink_to(outside)
        with self.assertRaisesRegex(ValueError, "source identity"):
            accepted_inputs(runtime, self.root)

    def test_pe_requires_x64_instead_of_a_renamed_mac_binary(self):
        binary = self.root / "synthetic.exe"
        data = bytearray(128); data[:2] = b"MZ"; data[0x3c:0x40] = struct.pack("<I", 0x40)
        data[0x40:0x46] = b"PE\0\0\x64\x86"
        binary.write_bytes(data); pe_x64(binary)
        data[0x44:0x46] = b"\x64\xaa"; binary.write_bytes(data)
        with self.assertRaisesRegex(ValueError, "x64"):
            pe_x64(binary)
        binary.write_bytes(b"synthetic non-Windows binary")
        with self.assertRaisesRegex(ValueError, "Windows executable"):
            pe_x64(binary)

    def test_dependencies_allow_system_dlls_and_require_bundled_sdl(self):
        answer = SimpleNamespace(stdout="DLL Name: KERNEL32.dll\nDLL Name: SDL2.dll\nDLL Name: api-ms-win-crt-runtime-l1-1-0.dll")
        with patch("export_private_windows.subprocess.run", return_value=answer):
            with self.assertRaisesRegex(ValueError, "Unbundled DLLs"):
                check_imports(self.root / "test.exe", self.root)
            (self.root / "SDL2.dll").write_bytes(b"synthetic dll")
            self.assertEqual(len(check_imports(self.root / "test.exe", self.root)), 3)

    def header_fixture(self):
        manifest = {"bios": {"local_relative": "bios/test.rom", "sha256": "a" * 64,
                             "runtime_sha256": "b" * 64, "size": 4, "byte_order": "swap16"}, "games": []}
        rows = []
        for game in ["faces", "gamelon", "adventure"]:
            cue = "roms/" + game + "/Zelda's test.cue"
            image = "roms/" + game + "/Zelda's test.bin"
            manifest["games"].append({"id": game, "title": "Synthetic " + game,
                                      "local_cue_relative": cue, "disc_sha256": "c" * 64})
            rows.extend([{"relative": cue, "sha256": "d" * 64}, {"relative": image, "sha256": "c" * 64}])
        return manifest, rows, {g: "e" * 64 for g in ["faces", "gamelon", "adventure"]}

    def test_private_header_keeps_wide_paths_quotes_and_normalization(self):
        manifest, rows, runtimes = self.header_fixture()
        header = package_header(manifest, rows, runtimes)
        self.assertIn("#define BIOS_SWAP16 1", header)
        self.assertIn('L"roms\\\\adventure\\\\Zelda\'s test.cue"', header)
        self.assertIn('"' + "e" * 64 + '"', header)
        self.assertNotIn(str(self.root), header)

    def test_unsupported_bios_order_and_ambiguous_disc_are_rejected(self):
        manifest, rows, runtimes = self.header_fixture()
        manifest["bios"]["byte_order"] = "unknown"
        with self.assertRaisesRegex(ValueError, "normalization"):
            package_header(manifest, rows, runtimes)
        manifest["bios"]["byte_order"] = "swap16"
        rows.append({"relative": "roms/faces/other.bin", "sha256": "f" * 64})
        with self.assertRaisesRegex(ValueError, "one exported image"):
            package_header(manifest, rows, runtimes)


if __name__ == "__main__":
    unittest.main()
