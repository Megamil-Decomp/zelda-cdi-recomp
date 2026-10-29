#!/usr/bin/env python3
"""Inspect Adventure's observed resource index format; never modify media.

Input is a private extracted metadata prefix, not a standard Rich Text document.
Only the locally observed container and its r/l tables are supported.
"""
import argparse
import json
from pathlib import Path
import struct


def words(data, start, count):
    if start < 0 or count < 0 or start + count * 4 > len(data):
        raise ValueError('truncated header or offsets')
    return struct.unpack_from('>' + 'I' * count, data, start)


def variable(data, base):
    kind, size, count, index, payload = words(data, base, 5)
    if kind != 2 or size < 20 or base + size > len(data) or count > 100000:
        raise ValueError('invalid variable table')
    if index < 20 or index + count * 4 > payload or payload > size:
        raise ValueError('invalid table bounds')
    offsets = words(data, base + index, count)
    if list(offsets) != sorted(offsets) or any(x > size - payload for x in offsets):
        raise ValueError('invalid entry offsets')
    ends = (*offsets[1:], size - payload)
    return [data[base + payload + a:base + payload + b] for a, b in zip(offsets, ends)]


def inspect(data):
    kind, size, count, labels, values = words(data, 0, 5)
    if kind != 0 or size < 20 or size > len(data) or count != 5:
        raise ValueError('unsupported resource container')
    data = data[:size]
    names = variable(data, labels)
    table_kind, table_size, n, index, payload = words(data, values, 5)
    if (table_kind != 2 or n != count or len(names) != count or
            table_size < 20 or values + table_size > size or
            index < 20 or index + count * 4 > table_size or payload != table_size):
        raise ValueError('inconsistent container tables')
    # The values table contains offsets into the following sibling block area.
    offsets = words(data, values + index, count)
    if list(offsets) != sorted(offsets):
        raise ValueError('unordered child offsets')
    children = values + payload
    tables = {}
    for name, off in zip(names, offsets):
        key = name.rstrip(b'\0').decode('ascii')
        base = children + off
        child_kind, child_size, child_count, stride, child_payload = words(data, base, 5)
        if child_size < 20 or base + child_size > size:
            raise ValueError('child outside container')
        tables[key] = {'offset': base, 'size': child_size, 'count': child_count, 'kind': child_kind}
        if key == 'l':
            tables[key]['names'] = [x.rstrip(b'\0').decode('ascii') for x in variable(data, base)]
        if key == 'r':
            if child_kind != 1 or stride != 12 or child_payload != 20 or 20 + child_count * stride != child_size:
                raise ValueError('unsupported resource record layout')
            tables[key]['records_u16be'] = [list(struct.unpack_from('>6H', data, base + 20 + i * 12)) for i in range(child_count)]
    records = tables.get('r', {}).get('records_u16be', [])
    labels = tables.get('l', {}).get('names', [])
    if len(records) != len(labels):
        raise ValueError('resource/name count mismatch')
    return {'metadata_bytes': size, 'tables': tables,
            'resources': [{'index': i, 'name': name, 'raw_fields': record} for i, (name, record) in enumerate(zip(labels, records))],
            'limitations': 'Field meanings and image codecs are not yet confirmed; names are internal IDs, not translations.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    private = Path(__file__).resolve().parents[1] / 'data/private'
    output = args.output.resolve()
    if not output.is_relative_to(private) or output.exists():
        parser.error('output must be a new file under data/private/')
    report = inspect(args.input.read_bytes())
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(f"Indexed {len(report['resources'])} resources; field semantics remain unconfirmed.")


if __name__ == '__main__':
    main()
