"""Portable media selection uses only synthetic files."""
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from export_private_macos import copy_media, media_plan


class PrivateExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        bios = self.root / "bios/test.rom"
        bios.parent.mkdir()
        bios.write_bytes(b"synthetic BIOS")
        self.manifest = {"bios": {"local_relative": "bios/test.rom", "size": bios.stat().st_size,
                                  "sha256": hashlib.sha256(bios.read_bytes()).hexdigest()}, "games": []}
        for game in ("faces", "gamelon", "adventure"):
            folder = self.root / "roms" / game
            folder.mkdir(parents=True)
            image = folder / "test image.bin"
            image.write_bytes((game.encode() * 2352)[:2352])
            (folder / "test.cue").write_text('FILE "test image.bin" BINARY\n TRACK 01 CDI/2352\n INDEX 01 00:00:00\n')
            self.manifest["games"].append({"id": game, "local_cue_relative": f"roms/{game}/test.cue",
                                            "disc_sha256": hashlib.sha256(image.read_bytes()).hexdigest()})

    def test_complete_copy_preserves_originals_and_names_with_spaces(self):
        rows = media_plan(self.manifest, self.root)
        self.assertEqual(len(rows), 7)
        destination = self.root / "export/LocalMedia"
        copy_media(rows, destination)
        for row in rows:
            self.assertEqual((destination / row["relative"]).read_bytes(), row["source"].read_bytes())
        self.assertTrue((destination / "roms/adventure/test image.bin").is_file())

    def test_wrong_disc_cannot_be_exported_as_accepted_media(self):
        (self.root / "roms/faces/test image.bin").write_bytes(b"other revision")
        with self.assertRaisesRegex(ValueError, "checksum mismatch"):
            media_plan(self.manifest, self.root)

    def test_manifest_paths_and_symlinks_cannot_escape_media_directory(self):
        self.manifest["bios"]["local_relative"] = "bios/../outside.rom"
        with self.assertRaisesRegex(ValueError, "remain"):
            media_plan(self.manifest, self.root)
        outside = self.root / "outside.rom"
        outside.write_bytes(b"synthetic BIOS")
        path = self.root / "bios/link.rom"
        path.symlink_to(outside)
        self.manifest["bios"]["local_relative"] = "bios/link.rom"
        with self.assertRaisesRegex(ValueError, "escaping symlink"):
            media_plan(self.manifest, self.root)

    def test_missing_title_or_wrong_bios_is_rejected(self):
        removed = self.manifest["games"].pop()
        with self.assertRaisesRegex(ValueError, "all three"):
            media_plan(self.manifest, self.root)
        self.manifest["games"].append(removed)
        self.manifest["bios"]["size"] += 1
        with self.assertRaisesRegex(ValueError, "BIOS size"):
            media_plan(self.manifest, self.root)

    def test_changed_source_during_copy_is_detected(self):
        rows = media_plan(self.manifest, self.root)
        rows[0]["source"].write_bytes(b"changed after planning")
        with self.assertRaisesRegex(ValueError, "Copied media"):
            copy_media(rows, self.root / "export")

    def test_cue_alias_keeps_declared_filename_in_export(self):
        folder = self.root / "roms/faces"
        (folder / "actual.bin").write_bytes((folder / "test image.bin").read_bytes())
        (folder / "test image.bin").unlink()
        (folder / "test image.bin").symlink_to(folder / "actual.bin")
        rows = media_plan(self.manifest, self.root)
        copy_media(rows, self.root / "export")
        self.assertTrue((self.root / "export/roms/faces/test image.bin").is_file())


if __name__ == "__main__":
    unittest.main()
