"""Synthetic OS-9 modules and sectors only; no commercial media is read."""

import hashlib
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import prepare_rea_module as mod
from verify_local_media import SYNC


def reference_crc(data):
    # Independent polynomial long division, deliberately without lookup tables.
    remainder = 0xFFFFFF
    for value in data:
        for position in range(7, -1, -1):
            feedback = ((remainder >> 23) & 1) ^ ((value >> position) & 1)
            remainder = (remainder << 1) & 0xFFFFFF
            if feedback:
                remainder ^= 0x800063
    return remainder


def checksum(data):
    data[-3:] = (reference_crc(data[:-3]) ^ 0xFFFFFF).to_bytes(3, "big")
    return bytes(data)


def fixture(size=256, entry=0x48, exception=0):
    data = bytearray(size)
    data[:2] = b"\x4a\xfc"
    struct.pack_into(">I", data, 4, size)
    data[0x12:0x14] = b"\x01\x01"
    parity = 0xFFFF
    for word in struct.unpack_from(">23H", data):
        parity ^= word
    struct.pack_into(">H", data, 0x2E, parity)
    struct.pack_into(">II", data, 0x30, entry, exception)
    data[0x48:0x4E] = b"\x70\x2a\x52\x80\x4e\x75"  # moveq 42; addq.l 1; rts
    return checksum(data)


def sector(lba, payload=b"", form=1, file=1, channel=0, eof=False):
    value = lba + 150
    minute, rest = divmod(value, 4500)
    second, frame = divmod(rest, 75)
    bcd = lambda x: (x // 10 << 4) | x % 10
    data = bytearray(2352)
    data[:12] = SYNC
    data[12:16] = bytes((bcd(minute), bcd(second), bcd(frame), 2))
    header = bytes((file, channel, 0x08 | (0x20 if form == 2 else 0) | (0x80 if eof else 0), 0))
    data[16:24] = header * 2
    data[24:24 + len(payload)] = payload
    return bytes(data)


class ReaModuleTests(unittest.TestCase):
    def test_crc_matches_independent_polynomial_division(self):
        for data in (b"", b"123456789", bytes(range(256)), fixture()):
            self.assertEqual(mod.crc24(data), reference_crc(data))
        self.assertEqual(mod.crc24(fixture()), 0x800FE3)

    def test_valid_module_and_analysis_mapping_preserve_complete_source(self):
        source = fixture()
        info = mod.inspect_module(source)
        self.assertEqual(info["entry_offset"], 0x48)
        image = mod.analysis_image(source)
        self.assertEqual(image[0x100:], source)
        self.assertEqual(image[:6], b"\x4e\xf9\x00\x00\x01\x48")
        self.assertEqual(image[6:0x100], bytes(250))
        self.assertEqual(image[0x148:0x14E], source[0x48:0x4E])

    def test_reject_truncated_extra_and_bad_id_size_parity_crc(self):
        good = fixture()
        invalid = [good[:0x4A], good[:-1], good + b"\0"]
        for offset in (0, 4, 0x2E, 0x48, len(good) - 1):
            altered = bytearray(good)
            altered[offset] ^= 1
            invalid.append(bytes(altered))
        for data in invalid:
            with self.subTest(size=len(data)), self.assertRaises(ValueError):
                mod.inspect_module(data)

    def test_reject_invalid_entry_exception_and_non_program(self):
        for entry, exception in ((0x47, 0), (0x49, 0), (254, 0), (0x48, 0x49), (0x48, 254)):
            with self.subTest(entry=entry, exception=exception), self.assertRaises(ValueError):
                mod.inspect_module(fixture(entry=entry, exception=exception))
        data = bytearray(fixture())
        data[0x12] = 2
        data[0x2E:0x30] = b"\0\0"
        parity = 0xFFFF
        for word in struct.unpack_from(">23H", data):
            parity ^= word
        struct.pack_into(">H", data, 0x2E, parity)
        with self.assertRaisesRegex(ValueError, "only OS-9 Prog"):
            mod.inspect_module(checksum(data))

    def registry(self, data=None):
        return {"total": 1, "dropped": 0, "complete": True,
                "targets": [{"sha256": hashlib.sha256(data or fixture()).hexdigest(),
                             "offset": 0x48, "hits": 5}]}

    def test_targets_bind_exact_identity_and_do_not_invent_function_boundaries(self):
        info = mod.inspect_module(fixture())
        registry = self.registry()
        registry["targets"] += [dict(registry["targets"][0]),
                                {"sha256": "f" * 64, "offset": 2, "hits": 1}]
        registry["total"] = 3
        offsets, report = mod.observed_seeds({"module_targets": registry}, info)
        self.assertEqual(offsets, [0x48])
        self.assertEqual(report["duplicate_offsets"], 1)
        self.assertEqual(report["other_identity_rows"], 1)
        self.assertEqual(report["seed_kind"], "code")
        self.assertFalse(report["runtime_observation_is_function_proof"])

    def test_incomplete_or_dropped_targets_remain_explicit(self):
        for change in ({"total": 9}, {"dropped": 2}, {"complete": False}):
            registry = self.registry()
            registry.update(change)
            _, report = mod.observed_seeds(registry, mod.inspect_module(fixture()))
            self.assertFalse(report["registry_complete"])

    def test_invalid_targets_rejected(self):
        for changes in ({"offset": 0x49}, {"offset": 0x20}, {"offset": 254},
                        {"offset": True}, {"hits": 0}, {"sha256": "x" * 64},
                        {"sha256": "f" * 64}):
            registry = self.registry()
            registry["targets"][0].update(changes)
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                mod.observed_seeds(registry, mod.inspect_module(fixture()))
        registry = self.registry()
        registry["total"] = 0
        with self.assertRaises(ValueError):
            mod.observed_seeds(registry, mod.inspect_module(fixture()))

    def test_private_output_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            out = root / "data/private/rea-pilot/synthetic"
            source = fixture()
            manifest = mod.prepare(source, {"synthetic": True}, out, self.registry(), root)
            self.assertEqual((out / "module.bin").read_bytes(), source)
            self.assertEqual((out / "analysis.bin").read_bytes()[0x100:], source)
            self.assertTrue(manifest["analysis_only"])
            self.assertIn("0x148\tcode", (out / "seeds.tsv").read_text())
            self.assertEqual(json.loads((out / "manifest.json").read_text()), manifest)
            with self.assertRaisesRegex(ValueError, "overwrite"):
                mod.prepare(source, {}, out, root=root)
            for path in (root / "scripts/out", root / "build", root / "data/private/rea-pilot"):
                with self.assertRaises(ValueError):
                    mod.output_destination(path, root)

    def test_symlink_escape_and_symlink_output_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "build").mkdir()
            (root / "outside").mkdir()
            (root / "build/link").symlink_to(root / "outside", target_is_directory=True)
            with self.assertRaises(ValueError):
                mod.output_destination(root / "build/link/new", root)
            (root / "build/real").mkdir()
            (root / "build/alias").symlink_to(root / "build/real", target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "symlink"):
                mod.output_destination(root / "build/alias/new", root)

    def disc(self, root, second=None, **first_options):
        data = fixture(2500)
        (root / "input.bin").write_bytes(sector(0, data[:2048], **first_options) +
                                       (second if second is not None else sector(1, data[2048:], eof=True)))
        cue = root / "input.cue"
        cue.write_text('FILE "input.bin" BINARY\nTRACK 01 CDI/2352\nINDEX 01 00:00:00\n')
        return cue, data

    def test_contiguous_form1_extent_preserves_media(self):
        with tempfile.TemporaryDirectory() as temp:
            cue, expected = self.disc(Path(temp))
            before = cue.with_suffix(".bin").read_bytes()
            data, source = mod.extract_extent(cue, 0, len(expected))
            self.assertEqual(data, expected)
            self.assertEqual(source["sectors_read"], 2)
            self.assertFalse(source["filesystem_membership_verified"])
            self.assertEqual(cue.with_suffix(".bin").read_bytes(), before)

    def test_extent_rejects_form2_identity_change_eof_and_range_overflow(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for second in (sector(1, form=2), sector(1, file=2), sector(1, channel=1)):
                cue, data = self.disc(root, second=second)
                with self.assertRaises(ValueError):
                    mod.extract_extent(cue, 0, len(data))
            cue, data = self.disc(root, eof=True)
            with self.assertRaisesRegex(ValueError, "EOF"):
                mod.extract_extent(cue, 0, len(data))
            for lba, size in ((-1, 2500), (0xFFFFFFFF, 2500), (0, mod.MAX_MODULE_BYTES + 1),
                              (0, 74), (1, 2500)):
                with self.subTest(lba=lba, size=size), self.assertRaises(ValueError):
                    mod.extract_extent(cue, lba, size)


if __name__ == "__main__":
    unittest.main()
