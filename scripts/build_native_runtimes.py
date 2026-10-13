#!/usr/bin/env python3
"""Rebuild private native CD-i runtimes without changing the upstream checkout.

Generated BIOS/game code, build logs and binaries stay in ignored build/native/.
The staging source directory is disposable and is replaced on each invocation.
Requires the audited upstream checkout/submodule, CMake, Clang and local SDL2.
"""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_COMMIT = "f3c8d579efb11d5a33c6bc7c935dfbced773e62e"
CORE_COMMIT = "ddfa4e1b090b643a9ee596050e7eb345b8b276a2"
GAME_CUES = {
    "faces": "roms/Link The Faces of Evil/Link - The Faces of Evil (Europe).cue",
    "gamelon": "roms/Zelda The Wand of Gamelon/Zelda - The Wand of Gamelon (Europe).cue",
    "adventure": "roms/Zeldas Adventure/Zelda's Adventure (Europe).cue",
}


def command(argv, log, cwd=ROOT):
    print("Running: " + str(log.relative_to(ROOT)), flush=True)
    with log.open("w") as stream:
        result = subprocess.run([str(value) for value in argv], cwd=cwd,
                                stdout=stream, stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError("Command failed ({}); see {}".format(result.returncode, log))


def git_revision(path):
    return subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"],
                          check=True, capture_output=True, text=True).stdout.strip()


def plausible_bios_vectors(image):
    stack, entry = int.from_bytes(image[:4], "big"), int.from_bytes(image[4:8], "big")
    return 0 < stack <= 0x200000 and stack % 2 == 0 and 0x400000 <= entry < 0x480000 and entry % 2 == 0


def normalize_bios(source, destination):
    raw = source.read_bytes()
    if len(raw) != 524288:
        raise RuntimeError("Expected a 512 KiB cdi490a system BIOS")
    image, byte_order = raw, "big"
    if not plausible_bios_vectors(image):
        normalized = bytearray(raw)
        normalized[0::2], normalized[1::2] = raw[1::2], raw[0::2]
        image, byte_order = bytes(normalized), "swap16"
        if not plausible_bios_vectors(image):
            raise RuntimeError("BIOS reset vectors are unsupported in either byte order")
    destination.write_bytes(image)
    return {"size": len(raw), "byte_order": byte_order,
            "sha256": hashlib.sha256(raw).hexdigest(),
            "runtime_sha256": hashlib.sha256(image).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game", choices=("all", *GAME_CUES), default="all")
    parser.add_argument("--jobs", type=int, default=3)
    args = parser.parse_args()
    if sys.platform != "darwin" or not 1 <= args.jobs <= 32:
        parser.error("this build pipeline requires macOS and 1–32 jobs")
    upstream = ROOT / "upstream-cdirecomp"
    if git_revision(upstream) != UPSTREAM_COMMIT:
        raise RuntimeError("Upstream commit differs from the audited revision")
    if git_revision(upstream / "external/m68k-recomp-core") != CORE_COMMIT:
        raise RuntimeError("m68k core differs from the audited revision; initialize the pinned submodule")
    base = ROOT / "build/native"
    source, logs, inputs = base / "source", base / "logs", base / "input"
    for directory in (logs, inputs):
        directory.mkdir(parents=True, exist_ok=True)
    if source.exists():
        shutil.rmtree(source)
    shutil.copytree(upstream, source,
                    ignore=shutil.ignore_patterns(".git", "build", "generated", "__pycache__", ".DS_Store"))
    patch = ROOT / "scripts/patches/0001-graceful-launcher-shutdown.patch"
    command(["patch", "-p1", "-i", patch], logs / "launcher-patch.log", cwd=source)
    perf_patch = ROOT / "scripts/patches/0002-performance-pacing-audio-vsync.patch"
    command(["patch", "-p1", "-i", perf_patch], logs / "performance-patch.log", cwd=source)
    canonical = inputs / "cdi490a.be.rom"
    bios_info = normalize_bios(ROOT / "bios/cdi490a.rom", canonical)
    (inputs / "bios-info.json").write_text(json.dumps(bios_info, indent=2) + "\n")
    (source / "bios/generated").mkdir(parents=True, exist_ok=True)

    compiler = base / "recompiler"
    command(["cmake", "-S", source / "recompiler", "-B", compiler,
             "-DCMAKE_BUILD_TYPE=Release", "-DCMAKE_OSX_DEPLOYMENT_TARGET=13.0"],
            logs / "recompiler-configure.log")
    command(["cmake", "--build", compiler, "--target", "CdiRecomp", "CdiRecompBios",
             "--parallel", args.jobs], logs / "recompiler-build.log")
    # Seeds are explicit: resolving them relative to the normalized input would
    # silently omit the upstream BIOS discovery data and produce an incomplete boot.
    command([compiler / "CdiRecompBios", canonical, "--emit", "--seeds",
             source / "bios/cdrtos_discovered.txt"], logs / "bios-emit.log", cwd=source)

    selected = GAME_CUES if args.game == "all" else {args.game: GAME_CUES[args.game]}
    for game_id, cue in selected.items():
        generated = base / "generated" / game_id
        if generated.exists():
            shutil.rmtree(generated)
        generated.mkdir(parents=True)
        emit = [compiler / "CdiRecomp", ROOT / cue, "--emit", "--out", generated]
        if game_id == "adventure":
            # Its Subr export layout has not been established. Never apply the
            # Hotel Mario-only named-offset32 layout to this title by guessing.
            emit.extend(["--module", "cdi_zelda"])
        command(emit, logs / (game_id + "-emit.log"))
        runtime = base / ("runtime-" + game_id)
        command(["cmake", "-S", source / "runner", "-B", runtime,
                 "-DCMAKE_BUILD_TYPE=Release", "-DCMAKE_OSX_DEPLOYMENT_TARGET=13.0",
                 "-DCMAKE_PREFIX_PATH=/opt/homebrew", "-DCDI_COSIM_BUILD=OFF",
                 "-DCDI_GAME_GENERATED_DIR=" + str(generated)],
                logs / (game_id + "-configure.log"))
        command(["cmake", "--build", runtime, "--target", "CdiRuntime", "--parallel", args.jobs],
                logs / (game_id + "-build.log"))
        print("Native executable: " + str(runtime / "CdiRuntime"), flush=True)
    print("Build complete. Boot/gameplay acceptance must be tested separately.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        print("Native build failed: " + str(exc), file=sys.stderr)
        raise SystemExit(1)
