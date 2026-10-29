#!/usr/bin/env python3
"""Build host-menu candidates from immutable, accepted generated inputs."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

from build_macos_app import load_runtime_catalog
from build_windows_runtimes import accepted_inputs, digest
from prepare_sdl_macos import prepare_sdl

ROOT = Path(__file__).resolve().parents[1]
HEADERS = ["cdi_player_ui.h", "cdi_player_ui_sdl.h", "cdi_player_ui_frontend.h"]


def run(args, log):
    with log.open("w") as f:
        subprocess.run([str(a) for a in args], check=True, stdout=f, stderr=subprocess.STDOUT)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=ROOT / "data/private/rea-titles/runtime-catalog.json")
    parser.add_argument("--game", choices=["all", "faces", "gamelon", "adventure"], default="all")
    args = parser.parse_args()
    chosen = load_runtime_catalog(args.catalog)
    sdl_dir = prepare_sdl()
    sdl_library = sdl_dir.parents[1] / "libSDL2-2.0.0.dylib"
    patch = ROOT / "scripts/patches/0010-player-options-and-mouse.patch"
    logs = ROOT / "data/private/player-ui"
    logs.mkdir(parents=True, exist_ok=True)
    catalog = {"schema_version": 1, "runtimes": {}}
    for name, entry in chosen.items():
        catalog["runtimes"][name] = {"path": str(entry["path"]), "sha256": entry["sha256"], "status_text": entry["status_text"]}
        if args.game not in ("all", name):
            continue
        source, generated, provenance = accepted_inputs(entry["path"])
        token = hashlib.sha256((entry["sha256"] + digest(patch) +
                                "".join(digest(ROOT / "app/native" / h) for h in HEADERS) +
                                digest(sdl_library)).encode()).hexdigest()[:12]
        base = ROOT / "build/player-ui/variants" / token / name
        stage, runtime = base / "source", base / "runtime"
        if not stage.exists():
            for folder in ["runner", "bios", "common", "external", "recompiler", "tools"]:
                shutil.copytree(source / folder, stage / folder)
            for file in ["LICENSE", "PROVENANCE.md", "THIRD-PARTY-NOTICES.md"]:
                shutil.copy2(source / file, stage / file)
            check = subprocess.run(["patch", "--dry-run", "--batch", "-p1", "-i", str(patch)], cwd=stage, capture_output=True)
            if check.returncode == 0:
                run(["patch", "--batch", "-d", stage, "-p1", "-i", patch], logs / (name + "-patch.log"))
            else:
                reverse = subprocess.run(["patch", "--dry-run", "--batch", "-R", "-p1", "-i", str(patch)], cwd=stage, capture_output=True)
                if reverse.returncode:
                    raise ValueError("UI patch does not match accepted source: " + name)
            for h in HEADERS:
                shutil.copy2(ROOT / "app/native" / h, stage / "runner/include" / h)
        print("Building player menu: " + name, flush=True)
        run(["cmake", "-S", stage / "runner", "-B", runtime, "-DCMAKE_BUILD_TYPE=Release",
             "-DCMAKE_OSX_DEPLOYMENT_TARGET=13.0", "-DCMAKE_PREFIX_PATH=/opt/homebrew",
             "-DSDL2_DIR=" + str(sdl_dir),
             "-DCDI_COSIM_BUILD=OFF", "-DCDI_GAME_GENERATED_DIR=" + str(generated)], logs / (name + "-configure.log"))
        run(["cmake", "--build", runtime, "-j", "4"], logs / (name + "-build.log"))
        catalog["runtimes"][name].update(path=str(runtime / "CdiRuntime"), sha256=digest(runtime / "CdiRuntime"))
        (base / "origin.json").write_text(json.dumps({"accepted_runtime_sha256": entry["sha256"],
              "source": str(source), "generated": str(generated), "source_inputs": len(provenance["inputs"]),
              "patch_sha256": digest(patch), "headers": {h: digest(ROOT / "app/native" / h) for h in HEADERS}}, indent=2))
    output = logs / ("runtime-catalog-" + args.game + ".json")
    output.write_text(json.dumps(catalog, indent=2) + "\n")
    print("Candidate catalog: " + str(output), flush=True)


if __name__ == "__main__":
    main()
