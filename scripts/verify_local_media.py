#!/usr/bin/env python3
"""Read-only, stdlib-only inventory of locally supplied CD-i media.

The supported CUE profile is one BINARY file, one CDI/2352 (or MODE2/2352)
track, INDEX 01 00:00:00. This is a sampled structural check, not a dump
authenticator, full filesystem validator, EDC/ECC check or BIOS execution test.
Offsets follow Philips Green Book II.4 and III.2, available at:
https://www.icdia.co.uk/docs/GRNBK/BY_NAME/disc_format
https://www.icdia.co.uk/docs/GRNBK/BY_NAME/data_retrieval

Exit codes: 0 = checks passed (warnings possible); 2 = configuration/I/O
error; 3 = missing media, sampled structural problem or manifest mismatch.
No commercial payload is extracted or written. Reports and observed manifests
may only be written below <root>/data/private/.
"""

import argparse
import hashlib
import json
from pathlib import Path, PureWindowsPath
import shlex
import sys


SECTOR_SIZE = 2352
SYNC = b"\x00" + b"\xff" * 10 + b"\x00"
DISC_CUES = {
    "faces": "roms/Link The Faces of Evil/Link - The Faces of Evil (Europe).cue",
    "wand": "roms/Zelda The Wand of Gamelon/Zelda - The Wand of Gamelon (Europe).cue",
    "adventure": "roms/Zeldas Adventure/Zelda's Adventure (Europe).cue",
}
BIOS_SIZES = {"cdi490a.rom": 524288, "impega.rom": 262144, "vmpega.rom": 262144}


class ConfigurationError(ValueError):
    """Invalid options, manifest or output destination."""


class MediaError(ValueError):
    """A missing file or unsupported/inconsistent media structure."""


def contained(path, directory):
    try:
        path.resolve().relative_to(directory.resolve())
        return True
    except ValueError:
        return False


def safe_relative(directory, name):
    """Reject absolute, parent-traversing and symlink-escaping references."""
    normalized = name.replace("\\", "/")
    relative = Path(normalized)
    windows = PureWindowsPath(name)
    if (not normalized or relative.is_absolute() or windows.is_absolute()
            or windows.drive or ".." in relative.parts):
        raise MediaError("referência deve ser relativa, sem '..' ou unidade absoluta")
    result = directory / relative
    if not contained(result, directory):
        raise MediaError("referência/symlink sai da pasta permitida")
    return result


def parse_cue(path):
    """Parse a deliberately narrow CUE profile without silently guessing tracks."""
    if not path.is_file():
        raise MediaError("CUE ausente")
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except UnicodeError as exc:
        raise MediaError("CUE deve ser texto UTF-8/ASCII") from exc
    source = None
    track = None
    index = None
    for number, line in enumerate(lines, 1):
        try:
            words = shlex.split(line, comments=False, posix=True)
        except ValueError as exc:
            raise MediaError(f"CUE linha {number}: {exc}") from exc
        if not words or words[0].upper() == "REM":
            continue
        command = words[0].upper()
        if command == "FILE":
            if source is not None or track is not None or len(words) != 3:
                raise MediaError(f"CUE linha {number}: requer um único FILE antes de TRACK")
            if words[2].upper() != "BINARY":
                raise MediaError("somente FILE BINARY é suportado")
            source = safe_relative(path.parent, words[1])
        elif command == "TRACK":
            if source is None or track is not None or len(words) != 3:
                raise MediaError("requer um único TRACK depois de FILE")
            if words[1] != "01" or words[2].upper() not in {"CDI/2352", "MODE2/2352"}:
                raise MediaError("perfil suportado: TRACK 01 CDI/2352 ou MODE2/2352")
            track = words[2].upper()
        elif command == "INDEX":
            if track is None or index is not None or words[1:] != ["01", "00:00:00"]:
                raise MediaError("perfil suportado: somente INDEX 01 00:00:00")
            index = 0
        elif command == "CATALOG":
            if len(words) != 2 or len(words[1]) != 13 or not words[1].isdigit():
                raise MediaError("CATALOG deve ter 13 dígitos")
        elif command in {"TITLE", "PERFORMER", "SONGWRITER"}:
            if len(words) != 2:
                raise MediaError(f"metadado CUE {command} malformado")
        else:
            raise MediaError(f"comando CUE não suportado: {command} (linha {number})")
    if source is None or track is None or index is None:
        raise MediaError("CUE incompleto: FILE, TRACK e INDEX obrigatórios")
    if not source.is_file():
        raise MediaError(f"BIN referenciado ausente: {source.name}")
    return source


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def decode_bcd(value):
    if value >> 4 > 9 or value & 15 > 9:
        raise MediaError("endereço MSF não é BCD válido")
    return (value >> 4) * 10 + (value & 15)


def check_sector(data, lba):
    """Validate descrambled raw sector headers; return Form 1/2, not payload."""
    if len(data) != SECTOR_SIZE:
        raise MediaError("setor raw incompleto")
    if data[:12] != SYNC:
        raise MediaError("sync de 12 bytes incompatível com setor CD-i raw")
    if data[15] != 2:
        raise MediaError(f"modo {data[15]}, esperado Mode 2")
    minute, second, frame = (decode_bcd(value) for value in data[12:15])
    if second >= 60 or frame >= 75:
        raise MediaError("endereço MSF fora dos limites")
    if (minute * 60 + second) * 75 + frame != lba + 150:
        raise MediaError("endereço MSF não corresponde ao LBA + 150 deste perfil CUE")
    if data[16:20] != data[20:24]:
        raise MediaError("duas cópias do subheader divergem")
    return 2 if data[18] & 0x20 else 1


def read_sector(stream, lba):
    stream.seek(lba * SECTOR_SIZE)
    return stream.read(SECTOR_SIZE)


def check_disc_label(stream, sector_count):
    """Check essential Green Book label fields at LBA16 and its terminator.

    Big-endian fields are at BP85 (volume blocks) and BP131 (block size),
    with BP positions starting at one. Directories/modules are not followed.
    The finite 64-record label limit is a supported profile, not a spec limit.
    """
    if sector_count <= 16:
        raise MediaError("imagem curta demais para o Disc Label no LBA 16")
    labels = []
    for lba in range(16, min(sector_count, 16 + 64)):
        sector = read_sector(stream, lba)
        if (check_sector(sector, lba) != 1 or sector[16:18] != b"\x00\x00"
                or sector[19] != 0 or sector[18] & 0x7f != 9):
            raise MediaError(f"LBA {lba}: Disc Label exige Form 1, file/channel/coding zero e Data+EOR")
        block = sector[24:2072]
        if block[1:6] != b"CD-I " or block[6] != 1:
            raise MediaError(f"LBA {lba}: assinatura/versão do Disc Label CD-i não reconhecida")
        if block[0] == 255:
            if not labels:
                raise MediaError("Disc Label termina antes de um descritor de volume")
            return {"descriptor_count": len(labels), "terminator_lba": lba,
                    "volume_blocks": labels[0], "logical_block_size": 2048}
        if block[0] not in {1, 2}:
            raise MediaError(f"LBA {lba}: tipo de descritor de volume não suportado")
        if sector[18] & 0x80:
            raise MediaError(f"LBA {lba}: EOF antes do terminador do Disc Label")
        if block[8:40] != b"CD-RTOS".ljust(32, b" "):
            raise MediaError(f"LBA {lba}: identificador CD-RTOS ausente")
        blocks = int.from_bytes(block[84:88], "big")
        if int.from_bytes(block[130:132], "big") != 2048:
            raise MediaError(f"LBA {lba}: bloco lógico deve ter 2048 bytes")
        if blocks <= lba or blocks > sector_count:
            raise MediaError(f"LBA {lba}: volume declarado não cabe na imagem")
        if labels and blocks != labels[0]:
            raise MediaError("descritores discordam sobre tamanho do volume")
        labels.append(blocks)
    raise MediaError("terminador do Disc Label não encontrado em até 64 registros")


def sample_positions(count, samples):
    positions = {0, 1, 16, 17, count - 1}
    if count > 1:
        positions.update(i * (count - 1) // (samples - 1) for i in range(samples))
    return sorted(position for position in positions if 0 <= position < count)


def inspect_disc(path, samples=32):
    size = path.stat().st_size
    if size == 0 or size % SECTOR_SIZE:
        raise MediaError("BIN deve ser não vazio e múltiplo de 2352 bytes")
    count = size // SECTOR_SIZE
    result = {"sector_size": SECTOR_SIZE, "sector_count": count,
              "sampled_lbas": [], "form1_samples": 0, "form2_samples": 0,
              "errors": [], "warnings": [], "edc_ecc_checked": False}
    with path.open("rb") as stream:
        try:
            label = check_disc_label(stream, count)
            result["disc_label"] = label
            data_count = label["volume_blocks"]
        except MediaError as exc:
            result["errors"].append(str(exc))
            data_count = count
        for lba in sample_positions(data_count, samples):
            result["sampled_lbas"].append(lba)
            try:
                form = check_sector(read_sector(stream, lba), lba)
                result[f"form{form}_samples"] += 1
            except MediaError as exc:
                result["errors"].append(f"LBA {lba}: {exc}")
        if data_count < count:
            result["outside_volume_sectors"] = count - data_count
            # A label bounds the filesystem, not the full physical track.
            # Trailing uniform fill outside that bound is reported, not certified.
            trailing = 0
            for lba in range(count - 1, data_count - 1, -1):
                sector = read_sector(stream, lba)
                if sector not in {b"\x00" * SECTOR_SIZE, b" " * SECTOR_SIZE}:
                    break
                trailing += 1
            if trailing:
                result["trailing_uniform_sectors"] = trailing
                result["warnings"].append(
                    f"{trailing} setores finais uniformes fora do volume declarado; "
                    "possível padding, origem não autenticada")
            result["warnings"].append(
                f"{count - data_count} setores fora do volume; faixa extra não validada")
    return result


def load_manifest(path, root):
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ConfigurationError(f"manifest não pôde ser lido: {exc}") from exc
    if not isinstance(manifest, dict) or manifest.get("version") != 1:
        raise ConfigurationError("manifest requer objeto JSON com version: 1")
    files = manifest.get("files")
    if not isinstance(files, dict) or not files:
        raise ConfigurationError("manifest requer files não vazio, indexado por caminho relativo")
    for name, entry in files.items():
        try:
            safe_relative(root, name)
        except (MediaError, TypeError) as exc:
            raise ConfigurationError(f"caminho inseguro no manifest: {name!r}") from exc
        if not isinstance(entry, dict):
            raise ConfigurationError(f"manifest {name}: entrada deve ser objeto")
        digest = entry.get("sha256")
        size = entry.get("size")
        if (not isinstance(digest, str) or len(digest) != 64
                or any(char not in "0123456789abcdef" for char in digest)):
            raise ConfigurationError(f"manifest {name}: sha256 exige 64 dígitos hex minúsculos")
        if not isinstance(size, int) or isinstance(size, bool) or size <= 0:
            raise ConfigurationError(f"manifest {name}: size exige inteiro positivo")
    return files


def verify(root, scope="all", samples=32, expected=None):
    root = root.resolve()
    report = {"version": 1, "scope": scope, "files": {}, "discs": {},
              "errors": [], "warnings": [],
              "assurance": "amostragem estrutural; SHA-256 observado não autentica dump/BIOS"}
    files = set()
    for directory in (root / "roms", root / "bios"):
        if directory.is_dir():
            for path in directory.rglob("*"):
                if path.suffix.lower() in {".bin", ".cue", ".rom"}:
                    files.add(path)
    selected = DISC_CUES if scope == "all" else {"faces": DISC_CUES["faces"]}
    for game, relative in selected.items():
        cue = root / relative
        try:
            if not contained(cue, root / "roms"):
                raise MediaError("CUE/symlink sai da pasta roms")
            image = parse_cue(cue)
            files.update({cue, image})
            disc = inspect_disc(image, samples)
            report["discs"][game] = disc
            report["errors"].extend(f"{game}: {item}" for item in disc["errors"])
            report["warnings"].extend(f"{game}: {item}" for item in disc["warnings"])
        except MediaError as exc:
            report["errors"].append(f"{game}: {exc}")
    if not (root / "bios/cdi490a.rom").is_file():
        report["errors"].append("BIOS obrigatória ausente: bios/cdi490a.rom")
    for path in sorted(files):
        relative = path.relative_to(root).as_posix()
        if not contained(path, root / "roms") and not contained(path, root / "bios"):
            report["errors"].append(f"{relative}: symlink sai das pastas de mídia")
            continue
        if not path.is_file():
            report["errors"].append(f"{relative}: arquivo regular ausente")
            continue
        size = path.stat().st_size
        digest = sha256_file(path)
        entry = {"size": size, "sha256": digest, "hash_status": "observed_only"}
        report["files"][relative] = entry
        if not size:
            report["errors"].append(f"{relative}: arquivo vazio")
        if path.parent == root / "bios" and path.name in BIOS_SIZES:
            entry["format_check"] = "tamanho do perfil raw; módulos OS-9/CRC não validados"
            if size != BIOS_SIZES[path.name]:
                report["errors"].append(
                    f"{relative}: tamanho {size}, perfil esperado {BIOS_SIZES[path.name]} bytes")
        if expected is not None:
            if relative not in expected:
                entry["hash_status"] = "not_in_manifest"
                report["warnings"].append(f"{relative}: sem hash esperado no manifest")
            elif digest != expected[relative]["sha256"] or size != expected[relative]["size"]:
                entry["hash_status"] = "mismatch"
                report["errors"].append(f"{relative}: SHA-256/tamanho diverge do manifest local")
            else:
                entry["hash_status"] = "matches_local_manifest"
    if expected is not None:
        for relative in sorted(set(expected) - set(report["files"])):
            report["errors"].append(f"manifest: arquivo esperado ausente/não inventariado: {relative}")
    else:
        report["warnings"].append("sem manifest de referência local: hashes somente observados")
    report["exit_code"] = 3 if report["errors"] else 0
    return report


def private_output(root, argument):
    private_root = root / "data/private"
    if private_root.resolve() != private_root:
        raise ConfigurationError("data/private/ não pode ser redirecionada por symlink")
    path = Path(argument)
    if not path.is_absolute():
        path = root / path
    if not contained(path, private_root) or path.resolve() == private_root:
        raise ConfigurationError("saídas JSON/manifest só podem ficar em data/private/")
    if path.suffix.lower() != ".json":
        raise ConfigurationError("saída deve usar extensão .json")
    return path


def write_json(path, value, exclusive=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x" if exclusive else "w", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write("\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--scope", choices=("all", "faces"), default="all")
    parser.add_argument("--samples", type=int, default=32, help="pontos distribuídos por volume (2–4096)")
    parser.add_argument("--manifest", type=Path, help="hashes/tamanhos esperados, fornecidos localmente")
    parser.add_argument("--json", help="relatório privado em data/private/*.json")
    parser.add_argument("--write-manifest", help="salva baseline observado novo; não autentica dump")
    args = parser.parse_args(argv)
    try:
        root = args.root.resolve()
        if not root.is_dir() or not 2 <= args.samples <= 4096:
            raise ConfigurationError("root deve existir; samples deve ficar entre 2 e 4096")
        output = private_output(root, args.json) if args.json else None
        baseline = private_output(root, args.write_manifest) if args.write_manifest else None
        if baseline and baseline.exists():
            raise ConfigurationError("baseline já existe; use --manifest para comparar, ou escolha outro nome")
        if output and baseline and output.resolve() == baseline.resolve():
            raise ConfigurationError("relatório e baseline devem usar caminhos diferentes")
        manifest_path = args.manifest
        if manifest_path and not manifest_path.is_absolute():
            manifest_path = root / manifest_path
        if output and manifest_path and output.resolve() == manifest_path.resolve():
            raise ConfigurationError("relatório não pode sobrescrever o manifest de referência")
        expected = load_manifest(manifest_path, root) if manifest_path else None
        report = verify(root, args.scope, args.samples, expected)
        if output:
            write_json(output, report)
        if baseline:
            if report["errors"]:
                print("AVISO: baseline não foi gravado porque houve falhas de verificação")
            else:
                write_json(baseline, {"version": 1, "provenance": "observed_local_baseline_not_authentication",
                                     "files": {name: {"size": entry["size"], "sha256": entry["sha256"]}
                                               for name, entry in report["files"].items()}}, exclusive=True)
        print(f"Mídia local: {len(report['files'])} arquivos, {len(report['discs'])} discos inspecionados.")
        for game, disc in report["discs"].items():
            print(f"  {game}: {disc['sector_count']} setores; "
                  f"{len(disc['sampled_lbas'])} amostras; "
                  f"Form 1={disc['form1_samples']}, Form 2={disc['form2_samples']}")
        for name, entry in report["files"].items():
            print(f"  {name}: {entry['size']} bytes; SHA-256 {entry['sha256']} ({entry['hash_status']})")
        for warning in report["warnings"]:
            print(f"AVISO: {warning}")
        for error in report["errors"]:
            print(f"FALHA: {error}")
        print("Limites: sem validação EDC/ECC, módulos OS-9, execução da BIOS ou autenticação do dump.")
        print(f"Resultado: exit {report['exit_code']}.")
        return report["exit_code"]
    except (ConfigurationError, OSError) as exc:
        print(f"ERRO DE CONFIGURAÇÃO/I/O: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
