"""Synthetic discovery fixtures; no user disc/BIOS required."""

import csv
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import text_catalog as text
from verify_local_media import SYNC


def sector(payload, form=1, eof=False):
    raw = bytearray(2352)
    raw[:12] = SYNC
    raw[15] = 2
    raw[18] = (32 if form == 2 else 0) | (128 if eof else 0)
    raw[20:24] = raw[16:20]
    raw[24:24 + len(payload)] = payload
    return bytes(raw)


class TextCatalogTest(unittest.TestCase):
    def test_ascii_runs_have_no_quote_requirement_and_retain_nul(self):
        scanner = text.Scanner()
        scanner.feed(b"\0HELLO WORLD\0AB\0", 100)
        self.assertEqual(len(scanner.candidates), 1)
        row = scanner.candidates[0]
        self.assertEqual(row["original"], "HELLO WORLD")
        self.assertEqual(row["spans"], [{"raw_offset": 101, "length": 11}])
        self.assertTrue(row["nul_terminated"])

    def test_cross_sector_run_records_non_contiguous_physical_spans(self):
        scanner = text.Scanner()
        scanner.feed(b"\0HELLO ", 24)
        scanner.feed(b"WORLD\0", 2376)
        row = scanner.candidates[0]
        self.assertEqual(row["original"], "HELLO WORLD")
        self.assertEqual(row["spans"], [{"raw_offset": 25, "length": 6}, {"raw_offset": 2376, "length": 5}])

    def test_discontinuity_prevents_fabricated_string(self):
        scanner = text.Scanner(minimum=5)
        scanner.feed(b"ABC", 24)
        scanner.feed(b"DEF\0", 4700, contiguous=False)
        self.assertEqual(scanner.candidates, [])

    def test_overlong_runs_are_skipped_without_exporting_a_truncated_tail(self):
        scanner = text.Scanner(minimum=4, maximum=8)
        scanner.feed(b"ABCDEFGHI", 0)
        scanner.feed(b"JKLM\0VALID\0", 20)
        self.assertEqual([r["original"] for r in scanner.candidates], ["VALID"])

    def test_form2_eof_invalid_sectors_and_stable_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.bin"
            path.write_bytes(sector(b"HELLO\0") + sector(b"VOICE ONLY\0", 2) +
                             sector(b"\0" * 2045 + b"ABC", eof=True) + sector(b"DEF\0") + b"\0" * 2352)
            before = path.read_bytes()
            one = text.scan_image(path, "test", minimum=5)
            two = text.scan_image(path, "test", minimum=5)
            self.assertEqual([r["original"] for r in one["candidates"]], ["HELLO"])
            self.assertEqual(one, two)
            self.assertEqual(one["sector_counts"], {"form1": 3, "form2": 1, "invalid": 1})
            self.assertEqual(path.read_bytes(), before)
            self.assertTrue(one["candidates"][0]["id"].startswith("t_"))

    def fixture(self):
        return {"schema_version": 1, "game": "fixture", "source_sha256": "synthetic",
                "candidates": [{"id": "t_test", "original": "HELLO %s", "byte_length": 8,
                                "confidence": "high", "lba": 0, "payload_offset": 0,
                                "reviewed": False, "translation": ""}]}

    def validate_row(self, **changes):
        catalog = self.fixture()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "edit.csv"
            text.export_csv(path, catalog)
            with path.open(encoding="utf-8-sig", newline="") as stream:
                rows = list(csv.DictReader(stream))
            rows[0].update(changes)
            with path.open("w", encoding="utf-8-sig", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
            return text.validate(catalog, path)

    def test_untranslated_template_roundtrip(self):
        result = self.validate_row()
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["translations"], {})
        self.assertFalse(result["runtime_supported"])

    def test_utf8_longer_translation_is_warning_not_a_rom_write(self):
        result = self.validate_row(translation="Olá, você: %s", reviewed="true")
        self.assertEqual(result["errors"], [])
        self.assertEqual(len(result["warnings"]), 1)

    def test_changed_original_unreviewed_and_missing_placeholder_are_errors(self):
        for changes in ({"original": "changed"}, {"translation": "Olá %s"},
                        {"translation": "Olá", "reviewed": "true"}, {"id": "unknown"}):
            with self.subTest(changes=changes):
                self.assertTrue(self.validate_row(**changes)["errors"])

    def test_formula_like_candidates_are_escaped_for_csv(self):
        self.assertEqual(text.csv_text("=EXAMPLE"), "'=EXAMPLE")
        catalog = self.fixture()
        catalog["candidates"][0]["original"] = "=EXAMPLE"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "out.csv"
            text.export_csv(path, catalog)
            self.assertIn("'=EXAMPLE", path.read_text(encoding="utf-8-sig"))
            self.assertEqual(text.validate(catalog, path)["errors"], [])


if __name__ == "__main__":
    unittest.main()
