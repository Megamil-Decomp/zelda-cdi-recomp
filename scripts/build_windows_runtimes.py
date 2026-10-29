#!/usr/bin/env python3
"""Cross-compile accepted private generated inputs for Windows x64."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

from build_macos_app import load_runtime_catalog

ROOT = Path(__file__).resolve().parents[1]
SDL_VERSION = "2.32.10"


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest() if hasattr(hashlib, "file_digest") else _hash(stream)


def _hash(stream):
    h = hashlib.sha256()
    for block in iter(lambda: stream.read(1024 * 1024), b""):
        h.update(block)
    return h.hexdigest()


def copy_changed(source, destination):
    destination = Path(destination)
    if not destination.is_file() or digest(source) != digest(destination):
        shutil.copy2(source, destination)
    return str(destination)


def write_changed(path, text):
    if not path.is_file() or path.read_text() != text:
        path.write_text(text)


def accepted_inputs(runtime, root=ROOT):
    """Do not silently cross-compile sources changed since Mac acceptance."""
    runtime = Path(runtime)
    document = json.loads(runtime.with_name(runtime.name + ".build.json").read_text())
    if document["runtime_sha256"] != digest(runtime):
        raise ValueError("Accepted runtime provenance mismatch")
    rows = document["inputs"]
    for row in rows:
        path = Path(row["path"]).resolve()
        if not path.is_relative_to(root.resolve() / "build") or digest(path) != row["sha256"]:
            raise ValueError("Accepted source identity changed: " + path.name)
    bios = next(Path(r["path"]).resolve() for r in rows if r["path"].endswith("/bios/generated/cdrtos_full.c"))
    module = next(Path(r["path"]).resolve() for r in rows if r["path"].endswith("/module_manifest.c"))
    return bios.parents[2], module.parent, document


def run(args, log):
    with log.open("w") as stream:
        subprocess.run([str(a) for a in args], check=True, stdout=stream, stderr=subprocess.STDOUT)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=ROOT / "data/private/rea-titles/runtime-catalog.json")
    parser.add_argument("--game", choices=["all", "faces", "gamelon", "adventure"], default="all")
    parser.add_argument("--jobs", type=int, default=3)
    args = parser.parse_args()
    compiler = shutil.which("x86_64-w64-mingw32-gcc")
    if not compiler or not 1 <= args.jobs <= 16:
        parser.error("Requires MinGW x64 GCC and --jobs between 1 and 16")
    sdl = ROOT / "build/windows/tools" / ("SDL2-" + SDL_VERSION) / "x86_64-w64-mingw32"
    if not (sdl / "lib/cmake/SDL2/sdl2-config.cmake").is_file():
        parser.error("Install the verified official SDL2 MinGW SDK under build/windows/tools")
    selected = load_runtime_catalog(args.catalog)
    base = ROOT / "build/windows"
    logs = ROOT / "data/private/windows"
    logs.mkdir(parents=True, exist_ok=True)
    for game in ["faces", "gamelon", "adventure"]:
        if args.game not in ("all", game):
            continue
        source, generated, provenance = accepted_inputs(selected[game]["path"])
        stage = base / ("source-" + game)
        # Keep the copy incremental, while reconciling every file with its source.
        def ignore(directory, names):
            return ["CMakeLists.txt"] if Path(directory) == source / "runner" else []
        for folder in ["runner", "bios", "common", "external", "recompiler", "tools"]:
            shutil.copytree(source / folder, stage / folder, dirs_exist_ok=True,
                            copy_function=copy_changed, ignore=ignore)
        for name in ["LICENSE", "PROVENANCE.md", "THIRD-PARTY-NOTICES.md"]:
            copy_changed(source / name, stage / name)
        # Windows 10 1903+ UTF-8 ACP lets the existing char* guest-media API
        # accept Unicode paths supplied by the wide-character launcher.
        rc = stage / "runner/windows-app.rc"
        write_changed(rc, '1 24 "' + (ROOT / "app/windows/app.manifest").as_posix() + '"\n')
        cmake = stage / "runner/CMakeLists.txt"
        write_changed(cmake, (source / "runner/CMakeLists.txt").read_text() +
                      '\nif(WIN32)\n  enable_language(RC)\n  target_sources(CdiRuntime PRIVATE windows-app.rc)\nendif()\n')
        output = base / ("runtime-" + game)
        print("Configuring Windows x64: " + game, flush=True)
        run(["cmake", "-S", stage / "runner", "-B", output,
             "-DCMAKE_SYSTEM_NAME=Windows", "-DCMAKE_C_COMPILER=" + compiler,
             "-DCMAKE_RC_COMPILER=" + str(Path(compiler).with_name("x86_64-w64-mingw32-windres")),
             "-DCMAKE_BUILD_TYPE=Release", "-DCMAKE_C_FLAGS_RELEASE=-O2 -DNDEBUG",
             "-DCMAKE_EXE_LINKER_FLAGS=-static-libgcc", "-DCDI_COSIM_BUILD=OFF",
             "-DSDL2_DIR=" + str(sdl / "lib/cmake/SDL2"),
             "-DCDI_GAME_GENERATED_DIR=" + str(generated)], logs / (game + "-configure.log"))
        print("Building Windows x64: " + game, flush=True)
        run(["cmake", "--build", output, "-j", args.jobs], logs / (game + "-build.log"))
        report = {"game": game, "mac_accepted_runtime_sha256": selected[game]["sha256"],
                  "source_input_count": len(provenance["inputs"]),
                  "runtime_sha256": digest(output / "CdiRuntime.exe"), "source": str(source),
                  "generated": str(generated), "compiler": compiler, "sdl_version": SDL_VERSION,
                  "execution_on_windows_validated": False}
        (output / "windows-build.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
