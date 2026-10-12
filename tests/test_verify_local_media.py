"""Synthetic media only. Never reads the user's ROMs/BIOS."""

import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import verify_local_media as media


def bcd(value):
    return (value // 10) * 16 + value % 10


def sector(lba, form=2, block=None, submode=None):
    address = lba + 150
    minute, remainder = divmod(address, 60 * 75)
    second, frame = divmod(remainder, 75)
    result = bytearray(media.SECTOR_SIZE)
    result[:12] = media.SYNC
    result[12:16] = bytes((bcd(minute), bcd(second), bcd(frame), 2))
    subheader = bytes((0, 0, submode if submode is not None else (0x20 if form == 2 else 9), 0))
    result[16:24] = subheader * 2
    if block is not None:
        result[24:24 + len(block)] = block
    return bytes(result)


def volume_block(count=64, record_type=1):
    result = bytearray(2048)
    result[:8] = bytes((record_type,)) + b"CD-I " + b"\x01\x00"
    if record_type != 255:
        result[8:40] = b"CD-RTOS".ljust(32, b" ")
        result[84:88] = count.to_bytes(4, "big")
        result[130:132] = (2048).to_bytes(2, "big")
    return bytes(result)


def make_disc(path, count=64, trailing=0):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as stream:
        for lba in range(count):
            if lba == 16:
                stream.write(sector(lba, 1, volume_block(count)))
            elif lba == 17:
                stream.write(sector(lba, 1, volume_block(record_type=255), 0x89))
            else:
                stream.write(sector(lba, form=1 if lba % 4 == 0 else 2))
        stream.write(b" " * media.SECTOR_SIZE * trailing)


class MediaTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.cue = self.root / media.DISC_CUES["faces"]
        self.image = self.cue.with_suffix(".bin")
        make_disc(self.image)
        self.cue.write_text(f'CATALOG 0000000000000\nFILE "{self.image.name}" BINARY\n'
                            ' TRACK 01 CDI/2352\n INDEX 01 00:00:00\n', encoding="utf-8")
        bios = self.root / "bios/cdi490a.rom"
        bios.parent.mkdir()
        bios.write_bytes(b"\x00" * 524288)

    def tearDown(self):
        self.temporary.cleanup()

    def corrupt(self, lba, offset, replacement):
        with self.image.open("r+b") as stream:
            stream.seek(lba * media.SECTOR_SIZE + offset)
            stream.write(replacement)

    def main(self, *args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = media.main(["--root", str(self.root), "--scope", "faces", *args])
        return code, stdout.getvalue(), stderr.getvalue()

    def test_valid_single_track_cue_with_space_and_apostrophe(self):
        image = self.cue.parent / "Zelda's synthetic image.bin"
        self.image.rename(image)
        self.cue.write_text(f'FILE "{image.name}" BINARY\nTRACK 01 CDI/2352\nINDEX 01 00:00:00')
        self.assertEqual(media.parse_cue(self.cue), image)

    def test_missing_cue_and_missing_bin(self):
        self.image.unlink()
        with self.assertRaisesRegex(media.MediaError, "BIN.*ausente"):
            media.parse_cue(self.cue)
        self.cue.unlink()
        with self.assertRaisesRegex(media.MediaError, "CUE ausente"):
            media.parse_cue(self.cue)

    def test_cue_path_escape_is_rejected_before_opening(self):
        for name in ("../outside.bin", "/tmp/outside.bin", "C:\\outside.bin", "..\\outside.bin"):
            with self.subTest(name=name):
                self.cue.write_text(f'FILE "{name}" BINARY\nTRACK 01 CDI/2352\nINDEX 01 00:00:00')
                with self.assertRaises(media.MediaError):
                    media.parse_cue(self.cue)

    def test_cue_symlink_escape_is_rejected(self):
        outside = self.root / "outside.bin"
        outside.write_bytes(b"synthetic")
        self.image.unlink()
        self.image.symlink_to(outside)
        with self.assertRaisesRegex(media.MediaError, "sai da pasta"):
            media.parse_cue(self.cue)

    def test_unsupported_cue_profiles_are_not_silently_interpreted(self):
        original = self.cue.read_text()
        for text in (original.replace("CDI/2352", "AUDIO"),
                     original.replace("00:00:00", "00:02:00"),
                     original + "TRACK 02 CDI/2352\nINDEX 01 00:01:00\n",
                     original + "PREGAP 00:02:00\n",
                     original.replace(" BINARY", " WAVE"),
                     original.replace('FILE "', 'FILE "broken "')):
            with self.subTest(text=text):
                self.cue.write_text(text)
                with self.assertRaises(media.MediaError):
                    media.parse_cue(self.cue)

    def test_valid_forms_and_label_terminator_eof(self):
        report = media.inspect_disc(self.image)
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["disc_label"]["volume_blocks"], 64)
        self.assertGreater(report["form1_samples"], 0)
        self.assertGreater(report["form2_samples"], 0)
        self.assertFalse(report["edc_ecc_checked"])

    def test_truncated_raw_image_is_rejected(self):
        with self.image.open("ab") as stream:
            stream.write(b"x")
        with self.assertRaisesRegex(media.MediaError, "múltiplo de 2352"):
            media.inspect_disc(self.image)

    def test_sync_mode_bcd_address_and_subheader_corruption(self):
        valid = sector(0)
        corruptions = ((0, b"x", "sync"), (15, b"\x01", "modo"),
                       (13, b"\xfa", "BCD"), (13, b"\x60", "limites"),
                       (14, b"\x01", "LBA"), (20, b"\x01", "subheader"))
        for offset, value, message in corruptions:
            with self.subTest(offset=offset):
                data = bytearray(valid)
                data[offset:offset + len(value)] = value
                with self.assertRaisesRegex(media.MediaError, message):
                    media.check_sector(bytes(data), 0)

    def test_sampled_interior_corruption_is_failure(self):
        lba = media.sample_positions(64, 32)[10]
        self.corrupt(lba, 20, b"\x02")
        report = media.verify(self.root, scope="faces")
        self.assertEqual(report["exit_code"], 3)
        self.assertTrue(any("subheader" in error for error in report["errors"]))

    def test_volume_signature_wrong_block_size_and_extent_are_rejected(self):
        for offset, value, message in ((25, b"NOPE!", "assinatura"),
                                       (24 + 130, b"\x04\x00", "2048"),
                                       (24 + 84, (65).to_bytes(4, "big"), "não cabe")):
            with self.subTest(offset=offset):
                make_disc(self.image)
                self.corrupt(16, offset, value)
                self.assertTrue(any(message in error for error in media.inspect_disc(self.image)["errors"]))

    def test_missing_label_terminator_is_failure(self):
        self.corrupt(17, 24, b"\x00")
        self.assertTrue(media.inspect_disc(self.image)["errors"])

    def test_uniform_tail_outside_valid_volume_is_warning(self):
        make_disc(self.image, trailing=4)
        report = media.inspect_disc(self.image)
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["trailing_uniform_sectors"], 4)
        self.assertTrue(report["warnings"])

    def test_uniform_sector_inside_volume_is_failure(self):
        self.corrupt(63, 0, b" " * media.SECTOR_SIZE)
        self.assertTrue(media.inspect_disc(self.image)["errors"])

    def test_missing_required_bios_and_default_games_fail(self):
        (self.root / "bios/cdi490a.rom").unlink()
        report = media.verify(self.root)
        self.assertEqual(report["exit_code"], 3)
        self.assertTrue(any("BIOS obrigatória" in item for item in report["errors"]))
        self.assertTrue(any("wand" in item for item in report["errors"]))
        self.assertTrue(any("adventure" in item for item in report["errors"]))

    def test_observed_manifest_roundtrip_and_checksum_mismatch(self):
        code, _, stderr = self.main("--write-manifest", "data/private/lock.json")
        self.assertEqual((code, stderr), (0, ""))
        code, stdout, _ = self.main("--manifest", "data/private/lock.json", "--json", "data/private/report.json")
        self.assertEqual(code, 0)
        self.assertIn("matches_local_manifest", stdout)
        self.corrupt(2, 24, b"changed without header damage")
        code, stdout, _ = self.main("--manifest", "data/private/lock.json")
        self.assertEqual(code, 3)
        self.assertIn("diverge do manifest", stdout)

    def test_manifest_missing_file_and_unlisted_file_are_diagnosed(self):
        report = media.verify(self.root, scope="faces")
        expected = {name: entry for name, entry in report["files"].items()}
        expected.pop(next(name for name in expected if name.endswith(".cue")))
        expected["bios/missing.rom"] = {"size": 1, "sha256": "0" * 64}
        report = media.verify(self.root, scope="faces", expected=expected)
        self.assertEqual(report["exit_code"], 3)
        self.assertTrue(any("sem hash esperado" in item for item in report["warnings"]))
        self.assertTrue(any("missing.rom" in item for item in report["errors"]))

    def test_manifest_invalid_missing_and_path_escape_are_configuration_errors(self):
        self.assertEqual(self.main("--manifest", "does-not-exist.json")[0], 2)
        manifest = self.root / "bad.json"
        for value in ([], {"version": 1, "files": {}},
                      {"version": 1, "files": {"../secret": {"size": 1, "sha256": "0" * 64}}},
                      {"version": 1, "files": {"bios/a.rom": {"size": 1, "sha256": "bad"}}},
                      {"version": 1, "files": {"bios/a.rom": {"size": True, "sha256": "0" * 64}}}):
            with self.subTest(value=value):
                manifest.write_text(json.dumps(value))
                self.assertEqual(self.main("--manifest", "bad.json")[0], 2)

    def test_output_cannot_escape_private_or_overwrite_reference_baseline(self):
        for output in ("README.json", "data/private/../../roms/out.json", str(self.root.parent / "out.json")):
            with self.subTest(output=output):
                self.assertEqual(self.main("--json", output)[0], 2)
        self.assertEqual(self.main("--write-manifest", "data/private/lock.json")[0], 0)
        self.assertEqual(self.main("--write-manifest", "data/private/lock.json")[0], 2)
        self.assertEqual(self.main("--manifest", "data/private/lock.json", "--json", "data/private/lock.json")[0], 2)

    def test_failure_does_not_create_a_baseline_or_mutate_media(self):
        self.corrupt(0, 0, b"x")
        before = hashlib.sha256(self.image.read_bytes()).digest()
        code, _, _ = self.main("--write-manifest", "data/private/lock.json")
        self.assertEqual(code, 3)
        self.assertFalse((self.root / "data/private/lock.json").exists())
        self.assertEqual(hashlib.sha256(self.image.read_bytes()).digest(), before)

    def test_private_directory_symlink_escape_is_rejected(self):
        outside = self.root / "elsewhere"
        outside.mkdir()
        private = self.root / "data/private"
        private.parent.mkdir()
        private.symlink_to(outside, target_is_directory=True)
        self.assertEqual(self.main("--json", "data/private/report.json")[0], 2)


if __name__ == "__main__":
    unittest.main()
