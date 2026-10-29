#!/usr/bin/env python3
"""Export ASCII text candidates from CD-i Form 1 sectors; validate external translations.

This is a read-only discovery tool, not a text decoder or ROM patcher.
Only uncompressed printable ASCII is detected. Commercial text exports stay
under data/private/. No external dependencies, API calls or automatic translation.
"""

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import re
import sys

from verify_local_media import DISC_CUES, SYNC, parse_cue, private_output


ROOT = Path(__file__).resolve().parents[1]
PRINTABLE = re.compile(rb"[\x20-\x7e]+")
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[-+#0 ']*(?:\d+|\*)?(?:\.(?:\d+|\*))?(?:hh|ll|[hlztjL])?[diuoxXfFeEgGaAcspn%]|\{[\w]+\}")


def rating(text):
    letters = sum(c.isalpha() for c in text)
    if letters < 3:
        return "noise"
    ratio = sum(c.isalpha() or c.isspace() for c in text) / len(text)
    if ratio >= .90 and (" " in text or text.isupper()) and letters >= 4:
        return "high"
    return "medium" if ratio >= .70 else "noise"


class Scanner:
    """Keep runs across contiguous payloads, retaining every physical span."""
    def __init__(self, minimum=4, maximum=1024):
        self.minimum, self.maximum = minimum, maximum
        self.run = bytearray()
        self.spans = []
        self.oversized = False
        self.candidates = []

    def flush(self, terminator=None):
        if not self.oversized and self.minimum <= len(self.run) <= self.maximum:
            text = self.run.decode("ascii")
            self.candidates.append({"original": text, "byte_length": len(self.run),
                                    "confidence": rating(text), "nul_terminated": terminator == 0,
                                    "spans": self.spans})
        self.run, self.spans, self.oversized = bytearray(), [], False

    def feed(self, data, raw_offset, contiguous=True):
        if not contiguous:
            self.flush()
        cursor = 0
        for match in PRINTABLE.finditer(data):
            if match.start() > cursor:
                self.flush(data[cursor])
            length = match.end() - match.start()
            if len(self.run) + length > self.maximum:
                self.oversized = True
            if not self.oversized:
                self.run.extend(match.group())
                self.spans.append({"raw_offset": raw_offset + match.start(), "length": length})
            cursor = match.end()
            if cursor < len(data):
                self.flush(data[cursor])
        if cursor < len(data):
            self.flush(data[cursor])


def scan_image(image, game, minimum=4, maximum=1024, include_noise=False):
    if image.stat().st_size == 0 or image.stat().st_size % 2352:
        raise ValueError("BIN precisa ser raw, não vazio e múltiplo de 2352")
    scanner, digest = Scanner(minimum, maximum), hashlib.sha256()
    previous = None
    previous_eof = False
    counts = {"form1": 0, "form2": 0, "invalid": 0}
    with image.open("rb") as stream:
        for lba in range(image.stat().st_size // 2352):
            sector = stream.read(2352)
            digest.update(sector)
            valid = (len(sector) == 2352 and sector[:12] == SYNC and sector[15] == 2
                     and sector[16:20] == sector[20:24])
            if not valid or sector[18] & 32:
                scanner.flush()
                counts["form2" if valid else "invalid"] += 1
                previous = None
                continue
            counts["form1"] += 1
            scanner.feed(sector[24:2072], lba * 2352 + 24,
                         contiguous=previous == lba - 1 and not previous_eof)
            previous, previous_eof = lba, bool(sector[18] & 128)
    scanner.flush()
    identity = digest.hexdigest()
    candidates = []
    for row in scanner.candidates:
        if row["confidence"] == "noise" and not include_noise:
            continue
        first = row["spans"][0]["raw_offset"]
        row.update(id="t_" + hashlib.sha256((game + ":" + identity + ":" + str(first) + ":" + row["original"]).encode()).hexdigest()[:24],
                   lba=first // 2352, payload_offset=first % 2352 - 24,
                   reviewed=False, translation="")
        candidates.append(row)
    candidates.sort(key=lambda r: ({"high": 0, "medium": 1, "noise": 2}[r["confidence"]], r["lba"], r["payload_offset"]))
    return {"schema_version": 1, "game": game, "source_sha256": identity,
            "method": "printable ASCII runs in valid raw Mode-2 Form 1 payloads",
            "limits": ["Candidates include machine code and binary noise; confidence is heuristic.",
                       "No compressed/custom-encoded text, images, voice or Form 2 payloads decoded.",
                       "Physical continuity is not proof of a string or file boundary.",
                       "nul_terminated and byte_length do not establish safe writable capacity."],
            "sector_counts": counts, "candidates": candidates}


def csv_text(value):
    return "'" + value if value.startswith(("=", "+", "-", "@", "\t", "\r")) else value


def export_csv(path, catalog):
    fields = ["id", "confidence", "lba", "payload_offset", "byte_length", "nul_terminated", "original", "translation", "reviewed"]
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in catalog["candidates"]:
            writer.writerow({**row, "original": csv_text(row["original"])})


def validate(catalog, csv_path):
    if catalog.get("schema_version") != 1 or not isinstance(catalog.get("candidates"), list):
        raise ValueError("Catálogo não reconhecido")
    expected = {r["id"]: r for r in catalog["candidates"]}
    if len(expected) != len(catalog["candidates"]):
        raise ValueError("Catálogo contém IDs duplicados")
    seen, errors, warnings, translations = set(), [], [], {}
    with csv_path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not {"id", "original", "translation", "reviewed"}.issubset(reader.fieldnames or []):
            raise ValueError("CSV requer id, original, translation e reviewed")
        for row in reader:
            key = row["id"]
            if key not in expected or key in seen:
                errors.append("ID desconhecido/duplicado: " + key)
                continue
            seen.add(key)
            original, translated = expected[key]["original"], row["translation"]
            if row["original"] != csv_text(original):
                errors.append("original alterado: " + key)
                continue
            if not translated:
                continue
            if row["reviewed"].strip().lower() not in {"true", "1", "yes", "sim"}:
                errors.append("tradução sem revisão (reviewed=true): " + key)
            if "\0" in translated:
                errors.append("tradução contém NUL: " + key)
            if Counter(PLACEHOLDER.findall(original)) != Counter(PLACEHOLDER.findall(translated)):
                errors.append("placeholders divergentes: " + key)
            if len(translated.encode("utf-8")) > expected[key]["byte_length"]:
                warnings.append("tradução excede bytes originais; requer layout/adaptador: " + key)
            translations[key] = translated
    return {"schema_version": 1, "game": catalog.get("game"), "source_sha256": catalog.get("source_sha256"),
            "locale": "pt-BR", "runtime_supported": False, "translations": translations,
            "errors": errors, "warnings": warnings,
            "note": "Pacote intermediário validado; não é patch de ROM nem mod executável."}


def destination(root, value):
    return private_output(root, value)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    extract = sub.add_parser("extract")
    extract.add_argument("--game", choices=tuple(DISC_CUES), default="adventure")
    extract.add_argument("--cue", type=Path)
    extract.add_argument("--output", default="data/private/localization/catalog-adventure.json")
    extract.add_argument("--min-length", type=int, default=4)
    extract.add_argument("--max-length", type=int, default=1024)
    extract.add_argument("--include-noise", action="store_true")
    check = sub.add_parser("validate")
    check.add_argument("catalog", type=Path)
    check.add_argument("csv", type=Path)
    check.add_argument("--output", default="data/private/localization/pt-BR.validated.json")
    args = parser.parse_args(argv)
    output = destination(ROOT, args.output)
    csv_output = output.with_suffix(".csv") if args.command == "extract" else None
    review_output = output.with_name(output.stem + ".review.csv") if csv_output else None
    if output.exists() or (csv_output and csv_output.exists()) or (review_output and review_output.exists()):
        raise ValueError("Saída já existe; escolha outro nome para preservar traduções anteriores")
    if args.command == "extract":
        if not 1 <= args.min_length <= args.max_length <= 16384:
            raise ValueError("Limites: 1 <= min-length <= max-length <= 16384")
        image = parse_cue((args.cue or ROOT / DISC_CUES[args.game]).resolve())
        catalog = scan_image(image, args.game, args.min_length, args.max_length, args.include_noise)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        export_csv(csv_output, catalog)
        review = {**catalog, "candidates": [r for r in catalog["candidates"]
                                           if r["confidence"] == "high" and r["nul_terminated"]]}
        export_csv(review_output, review)
        print("Candidatos: {} (não são textos confirmados)".format(len(catalog["candidates"])))
        print("Confiança: " + str(dict(Counter(r["confidence"] for r in catalog["candidates"]))))
        print("JSON: {}\nCSV: {}".format(output, csv_output))
        print("Fila prioritária ({} candidatos, ainda não confirmados): {}".format(
            len(review["candidates"]), review_output))
        return 0
    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    report = validate(catalog, args.csv)
    if report["errors"]:
        for error in report["errors"]:
            print("ERRO: " + error, file=sys.stderr)
        return 3
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Traduções validadas: {}; avisos de tamanho: {}. Ainda sem integração no runtime.".format(
        len(report["translations"]), len(report["warnings"])))
    print(output)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print("Erro: " + str(exc), file=sys.stderr)
        raise SystemExit(2)
