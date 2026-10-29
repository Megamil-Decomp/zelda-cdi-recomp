#!/usr/bin/env python3
"""Copy an accepted local app and matching media into a private portable ZIP."""
import argparse
from datetime import datetime
import json
from pathlib import Path, PurePosixPath
import plistlib
import shlex
import shutil
import subprocess
import sys

from verify_local_media import parse_cue, sha256_file

ROOT = Path(__file__).resolve().parents[1]


def media_path(root, relative, folder):
    if not isinstance(relative, str) or "\\" in relative:
        raise ValueError("Invalid relative media path")
    parts = PurePosixPath(relative)
    if parts.is_absolute() or ".." in parts.parts or not parts.parts or parts.parts[0] != folder:
        raise ValueError("Media path must remain in " + folder)
    path = (root / relative).resolve()
    if not path.is_relative_to((root / folder).resolve()) or not path.is_file():
        raise ValueError("Missing media or escaping symlink")
    return path


def media_plan(manifest, root):
    root = Path(root).resolve()
    games = manifest.get("games", [])
    if len(games) != 3 or {g.get("id") for g in games} != {"faces", "gamelon", "adventure"}:
        raise ValueError("Export requires all three games")
    rows = []

    def add(source, relative, expected=None):
        digest = sha256_file(source)
        if expected is not None and digest != expected:
            raise ValueError("Media checksum mismatch: " + relative)
        if any(r["relative"] == relative for r in rows):
            raise ValueError("Duplicate media destination")
        rows.append({"source": source, "relative": relative, "sha256": digest,
                     "size": source.stat().st_size})

    bios = manifest["bios"]
    path = media_path(root, bios["local_relative"], "bios")
    if path.stat().st_size != bios["size"]:
        raise ValueError("BIOS size mismatch")
    add(path, bios["local_relative"], bios["sha256"])
    for game in games:
        relative = game["local_cue_relative"]
        cue = media_path(root, relative, "roms")
        image = parse_cue(cue)
        # Keep the original CUE byte-for-byte; its FILE names a sibling BIN.
        tokens = [shlex.split(line) for line in cue.read_text(encoding="utf-8-sig").splitlines()]
        filename = next(words[1] for words in tokens if words and words[0].upper() == "FILE")
        image_relative = (PurePosixPath(relative).parent / filename).as_posix()
        add(cue, relative)
        add(image, image_relative, game["disc_sha256"])
    return rows


def copy_media(rows, destination):
    for row in rows:
        target = destination / row["relative"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(row["source"], target)
        if sha256_file(target) != row["sha256"]:
            raise ValueError("Copied media checksum mismatch: " + row["relative"])


def run(*args):
    subprocess.run([str(a) for a in args], check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-app", type=Path, default=ROOT / "dist/Zelda CD-i.app")
    parser.add_argument("--output", type=Path,
                        help="new private destination; default creates a dated export")
    args = parser.parse_args()
    if sys.platform != "darwin":
        parser.error("Export requires macOS signing and Swift tools")
    output = (args.output or ROOT / "dist/exports" /
              datetime.now().astimezone().strftime("export-%Y%m%d-%H%M%S")).resolve()
    if not any(output.is_relative_to(ROOT / folder) for folder in ("dist", "build", "data/private")):
        parser.error("Export must remain inside an ignored private directory")
    if output.exists():
        parser.error("Output already exists; choose a new --output directory")
    source = args.source_app.resolve()
    run("codesign", "--verify", "--deep", "--strict", source)
    resources = source / "Contents/Resources"
    manifest = json.loads((resources / "runtime-manifest.json").read_text())
    for game in manifest["games"]:
        binary = source / "Contents/MacOS" / game["runtime"]
        if binary.parent != source / "Contents/MacOS" or sha256_file(binary) != game["runtime_sha256"]:
            raise ValueError("Accepted runtime identity mismatch")
    print("Verifying matching local media…", flush=True)
    rows = media_plan(manifest, ROOT)
    output.mkdir(parents=True)
    app = output / "Zelda CD-i.app"
    shutil.copytree(source, app)
    portable_resources = app / "Contents/Resources"
    print("Copying BIOS and three CUE/BIN pairs…", flush=True)
    copy_media(rows, portable_resources / "LocalMedia")
    manifest.pop("local_media_root", None)
    (portable_resources / "runtime-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    info_path = app / "Contents/Info.plist"
    info = plistlib.loads(info_path.read_bytes())
    info["CFBundleIdentifier"] = "local.zeldacdi.player.portable"
    info_path.write_bytes(plistlib.dumps(info))
    launcher = app / "Contents/MacOS" / info["CFBundleExecutable"]
    run("swiftc", "-O", "-swift-version", "5", "-target", "arm64-apple-macosx13.0",
        "-framework", "AppKit", "-framework", "CryptoKit", ROOT / "app/macos/Launcher.swift", "-o", launcher)
    instructions = (
        "Zelda CD-i — pacote privado portátil, Apple Silicon, macOS 13 ou posterior.\n\n"
        "Descompacte e abra Zelda CD-i.app. Selecione o jogo e clique em Iniciar jogo.\n"
        "A BIOS e os três discos estão dentro do aplicativo; não é necessário compilar.\n"
        "Pode mover o aplicativo inteiro para outra pasta. Não separar seus arquivos internos.\n"
        "Se o macOS solicitar autorização na primeira abertura, a build tem assinatura local, sem notarização Apple.\n"
        "Saves pessoais não foram incluídos; novos saves ficam no suporte de aplicação deste usuário.\n"
        "Compatibilidade experimental: não certifica campanha completa.\n"
    )
    (portable_resources / "LEIA-ME.txt").write_text(instructions)
    run("codesign", "--force", "--sign", "-", "--timestamp=none", launcher)
    run("codesign", "--force", "--sign", "-", "--timestamp=none", app)
    run("codesign", "--verify", "--deep", "--strict", app)
    print("Creating portable ZIP…", flush=True)
    archive = output / "Zelda-CDi-Completo.zip"
    run("ditto", "-c", "-k", "--sequesterRsrc", "--keepParent", app, archive)
    run("unzip", "-tq", archive)
    report = {"schema_version": 1, "version": info["CFBundleShortVersionString"],
              "archive_sha256": sha256_file(archive), "archive_bytes": archive.stat().st_size,
              "includes_personal_saves": False,
              "files": [{k: v for k, v in r.items() if k != "source"} for r in rows]}
    (output / "export-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print("Ready: " + str(archive), flush=True)


if __name__ == "__main__":
    main()
