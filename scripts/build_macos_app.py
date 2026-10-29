#!/usr/bin/env python3
"""Build a private Apple Silicon app from locally recompiled CD-i runtimes.

No original BIOS or disc image is copied into the bundle. Runtime binaries
contain locally generated guest code and must remain private. Builds require
Xcode command-line tools; running the resulting app does not.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import plistlib
import re
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
GAMES = (
    ("faces", "Link: The Faces of Evil", "Link The Faces of Evil", "Link - The Faces of Evil (Europe)"),
    ("gamelon", "Zelda: The Wand of Gamelon", "Zelda The Wand of Gamelon", "Zelda - The Wand of Gamelon (Europe)"),
    ("adventure", "Zelda's Adventure", "Zeldas Adventure", "Zelda's Adventure (Europe)"),
)


def load_runtime_catalog(path, root=ROOT):
    """Select all three private candidates by content, never by a stale path."""
    root = root.resolve()
    path = Path(path)
    if path.stat().st_size > 1024 * 1024:
        raise ValueError("Runtime catalog exceeds the finite size limit")
    document = json.loads(path.read_text())
    if not isinstance(document, dict) or document.get("schema_version") != 1:
        raise ValueError("Unsupported runtime catalog schema")
    entries = document.get("runtimes")
    if not isinstance(entries, dict) or set(entries) != {game[0] for game in GAMES}:
        raise ValueError("Runtime catalog must select exactly faces, gamelon and adventure")
    result = {}
    for game_id, entry in entries.items():
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            raise ValueError("Invalid runtime catalog entry")
        source = Path(entry["path"])
        source = (root / source).resolve() if not source.is_absolute() else source.resolve()
        if not any(source.is_relative_to(root / folder)
                   for folder in ("build", "dist", "data/private")):
            raise ValueError("Runtime candidate must stay in this project's private directories")
        digest = entry.get("sha256")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("Runtime catalog requires a complete SHA-256")
        if not source.is_file() or sha256(source) != digest:
            raise ValueError("Runtime candidate identity changed: " + game_id)
        label = entry.get("status_text", "Em teste")
        if not isinstance(label, str) or not label.strip() or len(label) > 100 or any(ord(c) < 32 for c in label):
            raise ValueError("Invalid runtime status text")
        result[game_id] = {"path": source, "sha256": digest, "status_text": label}
    return result


def run(argv, **kwargs):
    return subprocess.run([str(item) for item in argv], check=True, **kwargs)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dependencies(path):
    output = run(["otool", "-L", path], capture_output=True, text=True).stdout
    return [line.strip().split(" (compatibility version", 1)[0]
            for line in output.splitlines()[1:] if line.strip()]


def system_library(path):
    return path.startswith(("/usr/lib/", "/System/Library/"))


def add_rpath(binary, path):
    output = run(["otool", "-l", binary], capture_output=True, text=True).stdout
    if not re.search(r"path " + re.escape(path) + r" \(offset", output):
        run(["install_name_tool", "-add_rpath", path, binary], capture_output=True)


def bundle_libraries(executables, frameworks):
    """Copy non-system dylibs recursively and rewrite load commands.

    sdl2-compat opens SDL3 dynamically, so SDL3 must also be bundled even when
    it does not appear in otool -L. Its macOS loader searches @loader_path.
    """
    queue = list(executables)
    copied = {}
    while queue:
        binary = queue.pop(0)
        for dependency in dependencies(binary):
            if system_library(dependency) or dependency.startswith("@"):
                continue
            source = Path(dependency)
            if not source.is_file():
                raise RuntimeError("Missing dynamic library: " + dependency)
            if not dependency.endswith(".dylib"):
                raise RuntimeError("Unsupported non-system dependency: " + dependency)
            name = source.name
            destination = frameworks / name
            identity = source.resolve()
            if name in copied and copied[name] != identity:
                raise RuntimeError("Different libraries have the same name: " + name)
            if not destination.exists():
                shutil.copy2(source, destination)
                destination.chmod(0o755)
                copied[name] = identity
                run(["install_name_tool", "-id", "@rpath/" + name, destination], capture_output=True)
                add_rpath(destination, "@loader_path")
                queue.append(destination)
            run(["install_name_tool", "-change", dependency, "@rpath/" + name, binary], capture_output=True)
        if binary in executables:
            add_rpath(binary, "@executable_path/../Frameworks")

    if any(name.startswith("libSDL2") for name in copied):
        source = Path("/opt/homebrew/opt/sdl3/lib/libSDL3.0.dylib")
        if not source.is_file():
            raise RuntimeError("sdl2-compat requires the local SDL3 library")
        destination = frameworks / "libSDL3.dylib"
        shutil.copy2(source, destination)
        destination.chmod(0o755)
        run(["install_name_tool", "-id", "@rpath/libSDL3.dylib", destination], capture_output=True)
        for dependency in dependencies(destination):
            if not system_library(dependency) and dependency != "@rpath/libSDL3.dylib":
                raise RuntimeError("Unexpected SDL3 dependency: " + dependency)

    for binary in [*executables, *frameworks.glob("*.dylib")]:
        remaining = [item for item in dependencies(binary)
                     if not system_library(item) and not item.startswith("@")]
        if remaining:
            raise RuntimeError("Unbundled dependencies: " + repr(remaining))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    parser.add_argument("--no-dmg", action="store_true")
    parser.add_argument("--runtime-catalog", type=Path,
                        help="private JSON selecting all three runtime paths and SHA-256 identities")
    parser.add_argument("--menu-mod", type=Path, help="optional Adventure host menu compositor profile")
    parser.add_argument("--text-mod", type=Path, help="optional Adventure menu pilot configuration")
    parser.add_argument("--no-local-paths", action="store_true", help="do not prefill paths to this workspace")
    args = parser.parse_args()
    if sys.platform != "darwin":
        parser.error("packaging requires macOS")
    candidates = load_runtime_catalog(args.runtime_catalog) if args.runtime_catalog else {}
    output = args.output.resolve()
    private_locations = [ROOT / "dist", ROOT / "build", ROOT / "data/private"]
    if not any(output == path or path in output.parents for path in private_locations):
        parser.error("output must stay below ignored dist/, build/ or data/private/")
    output.mkdir(parents=True, exist_ok=True)
    work = ROOT / "build/macos-package"
    work.mkdir(parents=True, exist_ok=True)
    app = output / "Zelda CD-i.app"
    staging_app = work / "Zelda CD-i.app"
    if staging_app.exists():
        shutil.rmtree(staging_app)
    contents = staging_app / "Contents"
    macos, resources, frameworks = (contents / name for name in ("MacOS", "Resources", "Frameworks"))
    for directory in (macos, resources, frameworks):
        directory.mkdir(parents=True, exist_ok=True)
    if args.text_mod:
        shutil.copy2(args.text_mod, resources / "adventure-ptbr.txt")
    if args.menu_mod:
        if not args.text_mod:
            parser.error("--menu-mod requires --text-mod")
        shutil.copy2(args.menu_mod, resources / "adventure-menu-ptbr.txt")

    run(["swiftc", "-O", "-swift-version", "5", "-target", "arm64-apple-macosx13.0",
         "-module-cache-path", work / "module-cache", "-framework", "AppKit",
         "-framework", "CryptoKit", ROOT / "app/macos/Launcher.swift",
         "-o", macos / "ZeldaCDi"])

    canonical = ROOT / "build/native/input/cdi490a.be.rom"
    original = ROOT / "bios/cdi490a.rom"
    if not canonical.is_file():
        raise RuntimeError("Canonical BIOS has not been prepared locally")
    manifest = {"schema_version": 1, "private_build": True,
                "bios": {"size": original.stat().st_size, "sha256": sha256(original),
                         "runtime_sha256": sha256(canonical), "byte_order": "swap16",
                         "local_relative": "bios/cdi490a.rom"}, "games": []}
    if not args.no_local_paths:
        manifest["local_media_root"] = str(ROOT)

    executables = []
    for game_id, title, folder, stem in GAMES:
        candidate = candidates.get(game_id)
        runtime = candidate["path"] if candidate else ROOT / "build/native" / ("runtime-" + game_id) / "CdiRuntime"
        cue = Path("roms") / folder / (stem + ".cue")
        image = ROOT / "roms" / folder / (stem + ".bin")
        entry = {"id": game_id, "title": title, "runtime": "CdiRuntime-" + game_id,
                 "disc_sha256": sha256(image), "status": "experimental",
                 "status_text": "Em teste", "local_cue_relative": cue.as_posix()}
        if candidate:
            entry.update(status_text=candidate["status_text"], source_runtime_sha256=candidate["sha256"])
        if runtime.is_file():
            destination = macos / entry["runtime"]
            shutil.copy2(runtime, destination)
            if candidate and sha256(destination) != candidate["sha256"]:
                raise RuntimeError("Runtime candidate changed while packaging: " + game_id)
            destination.chmod(0o755)
            executables.append(destination)
        else:
            entry.update(status="unavailable", status_text="Ainda indisponível")
        manifest["games"].append(entry)
    if not executables:
        raise RuntimeError("No native runtime is available; refusing a launcher-only delivery")
    bundle_libraries(executables, frameworks)

    licenses = resources / "Licenses"
    licenses.mkdir()
    for source, name in (
        (ROOT / "upstream-cdirecomp/LICENSE", "cdirecomp-LICENSE.txt"),
        (ROOT / "upstream-cdirecomp/external/m68k-recomp-core/LICENSE", "m68k-recomp-core-LICENSE.txt"),
        (ROOT / "upstream-cdirecomp/THIRD-PARTY-NOTICES.md", "upstream-THIRD-PARTY-NOTICES.md"),
        (Path("/opt/homebrew/opt/sdl2-compat/LICENSE.txt"), "sdl2-compat-LICENSE.txt"),
        (Path("/opt/homebrew/opt/sdl3/LICENSE.txt"), "SDL3-LICENSE.txt"),
    ):
        shutil.copy2(source, licenses / name)
    (resources / "LEIA-ME.txt").write_text(
        "Zelda CD-i — build privada experimental para Mac Apple Silicon.\n\n"
        "Abra o app, selecione o jogo, a BIOS e seu arquivo CUE (ou BIN com CUE parceiro).\n"
        "O app não contém BIOS ou imagens de disco. As revisões compatíveis são verificadas.\n"
        "A BIOS local pode ser normalizada em cache privado sem alterar seu arquivo.\n"
        "A execução dos três jogos ainda exige validação; consulte o estado de cada título.\n"
        "Feche a janela do jogo para salvar a NVRAM.\n\n"
        "Não redistribua esta build: ela contém código recompilado localmente da sua mídia.\n"
        "Licenças dos componentes acompanham o pacote em Resources/Licenses.\n", encoding="utf-8")
    icon_source = ROOT / "assets/icon.png"
    app_icon = ROOT / "app/macos/AppIcon.icns"
    if icon_source.is_file() and not app_icon.is_file():
        iconset = work / "AppIcon.iconset"
        if iconset.exists():
            shutil.rmtree(iconset)
        iconset.mkdir(parents=True, exist_ok=True)
        for px, name in ((16, "icon_16x16.png"), (32, "icon_16x16@2x.png"), (32, "icon_32x32.png"),
                         (64, "icon_32x32@2x.png"), (128, "icon_128x128.png"), (256, "icon_128x128@2x.png"),
                         (256, "icon_256x256.png"), (512, "icon_256x256@2x.png"), (512, "icon_512x512.png")):
            run(["sips", "-z", str(px), str(px), str(icon_source), "--out", str(iconset / name)], capture_output=True)
        run(["iconutil", "-c", "icns", str(iconset), "-o", str(app_icon)], capture_output=True)
        shutil.rmtree(iconset, ignore_errors=True)
    if app_icon.is_file():
        shutil.copy2(app_icon, resources / "AppIcon.icns")

    info = {"CFBundleDevelopmentRegion": "pt_BR", "CFBundleDisplayName": "Zelda CD-i",
            "CFBundleExecutable": "ZeldaCDi", "CFBundleIdentifier": "local.zeldacdi.player",
            "CFBundleInfoDictionaryVersion": "6.0", "CFBundleName": "Zelda CD-i",
            "CFBundlePackageType": "APPL", "CFBundleShortVersionString": "0.1.6" if candidates else "0.1.4" if args.menu_mod else "0.1.3" if args.text_mod else "0.1.1",
            "CFBundleVersion": "7" if candidates else "5" if args.menu_mod else "4" if args.text_mod else "2", "LSMinimumSystemVersion": "13.0",
            "CFBundleIconFile": "AppIcon",
            "NSHighResolutionCapable": True, "NSHumanReadableCopyright": "Private local research build"}
    with (contents / "Info.plist").open("wb") as stream:
        plistlib.dump(info, stream)

    for binary in [*frameworks.glob("*.dylib"), *executables]:
        run(["codesign", "--force", "--sign", "-", "--timestamp=none", binary], capture_output=True)
    for entry in manifest["games"]:
        binary = macos / entry["runtime"]
        if binary.is_file():
            entry["runtime_sha256"] = sha256(binary)
    (resources / "runtime-manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    run(["codesign", "--force", "--sign", "-", "--timestamp=none", staging_app], capture_output=True)
    run(["codesign", "--verify", "--deep", "--strict", staging_app], capture_output=True)
    if app.exists():
        shutil.rmtree(app)
    shutil.copytree(staging_app, app)
    print("App: " + str(app))

    if not args.no_dmg:
        image_root = work / "disk-image"
        if image_root.exists():
            shutil.rmtree(image_root)
        image_root.mkdir()
        shutil.copytree(app, image_root / app.name)
        (image_root / "Applications").symlink_to("/Applications")
        dmg = output / "Zelda-CDi-AppleSilicon.dmg"
        if dmg.exists():
            dmg.unlink()
        run(["hdiutil", "create", "-quiet", "-volname", "Zelda CD-i", "-srcfolder", image_root,
             "-format", "UDZO", "-ov", dmg])
        run(["hdiutil", "verify", "-quiet", dmg])
        print("DMG: " + str(dmg))
    print("Private experimental build; gameplay compatibility is not certified by packaging.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        print("Packaging failed: " + str(exc), file=sys.stderr)
        raise SystemExit(1)
