import importlib.util
from pathlib import Path
import struct
import unittest

spec = importlib.util.spec_from_file_location('resource_index', Path(__file__).resolve().parents[1] / 'scripts/adventure_resource_index.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def variable(entries):
    payload = 20 + 4 * len(entries)
    offsets = []; pos = 0
    for entry in entries:
        offsets.append(pos); pos += len(entry)
    return struct.pack('>5I', 2, payload + pos, len(entries), 20, payload) + struct.pack('>' + 'I' * len(entries), *offsets) + b''.join(entries)


def fixture():
    names = variable([b'r\0', b'l\0', b'v\0', b'a\0', b'd\0'])
    records = struct.pack('>5I6H', 1, 32, 1, 12, 20, 1, 2, 3, 4, 5, 6)
    labels = variable([b'menu\0'])
    empty = struct.pack('>5I', 1, 20, 0, 1, 20)
    parts = [records, labels, empty, empty, empty]
    offsets = []; pos = 0
    for part in parts:
        offsets.append(pos); pos += len(part)
    value_table = struct.pack('>10I', 2, 40, 5, 20, 40, *offsets)
    body = names + value_table + b''.join(parts)
    return struct.pack('>5I', 0, 20 + len(body), 5, 20, 20 + len(names)) + body


class ResourceIndexTests(unittest.TestCase):
    def test_synthetic_resource_names_and_raw_fields(self):
        report = mod.inspect(fixture())
        self.assertEqual(report['resources'], [{'index': 0, 'name': 'menu', 'raw_fields': [1, 2, 3, 4, 5, 6]}])

    def test_truncated_input(self):
        for length in (0, 19, 50, len(fixture()) - 1):
            with self.assertRaises(ValueError): mod.inspect(fixture()[:length])

    def test_unsupported_container(self):
        data = bytearray(fixture()); struct.pack_into('>I', data, 0, 99)
        with self.assertRaises(ValueError): mod.inspect(data)

    def test_invalid_name_offset(self):
        data = bytearray(fixture()); struct.pack_into('>I', data, 40, 99999)
        with self.assertRaises(ValueError): mod.inspect(data)

    def test_record_name_mismatch(self):
        data = bytearray(fixture()); labelbase = 20 + 50 + 40 + 32
        struct.pack_into('>I', data, labelbase + 8, 0)
        with self.assertRaises(ValueError): mod.inspect(data)
