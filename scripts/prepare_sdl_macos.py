#!/usr/bin/env python3
"""Prepare an isolated native SDL2 SDK with the app's macOS deployment target."""
import hashlib
from pathlib import Path
import subprocess
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
VERSION = "2.32.10"
SOURCE_SHA256 = "5f5993c530f084535c65a6879e9b26ad441169b3e25d789d83287040a9ca5165"


def prepare_sdl():
    base = ROOT / "build/player-ui/sdl2"
    sdk = ROOT / "build/player-ui/sdl2-sdk"
    config = sdk / "lib/cmake/SDL2"
    if (config / "sdl2-config.cmake").is_file():
        return config
    logs = ROOT / "data/private/player-ui"
    logs.mkdir(parents=True, exist_ok=True)
    base.mkdir(parents=True, exist_ok=True)
    archive = base / ("SDL2-" + VERSION + ".tar.gz")
    if not archive.is_file():
        urllib.request.urlretrieve("https://github.com/libsdl-org/SDL/releases/download/release-" + VERSION + "/" + archive.name, archive)
    if hashlib.sha256(archive.read_bytes()).hexdigest() != SOURCE_SHA256:
        raise ValueError("Official SDL source identity mismatch")
    source = base / ("SDL2-" + VERSION)
    if not source.exists():
        with tarfile.open(archive) as tar:
            # Android-only symlinks are unnecessary for this Mac build.
            members = [m for m in tar.getmembers() if m.isfile() or m.isdir()]
            if any(not (base / m.name).resolve().is_relative_to(base.resolve()) for m in members):
                raise ValueError("Unsafe SDL source archive entry")
            tar.extractall(base, members=members)
    commands = [
        ["cmake", "-S", source, "-B", base / "build", "-DCMAKE_BUILD_TYPE=Release",
         "-DCMAKE_OSX_ARCHITECTURES=arm64", "-DCMAKE_OSX_DEPLOYMENT_TARGET=13.0",
         "-DCMAKE_INSTALL_PREFIX=" + str(sdk), "-DSDL_SHARED=ON", "-DSDL_STATIC=OFF", "-DSDL_TEST=OFF"],
        ["cmake", "--build", base / "build", "-j", "4"],
        ["cmake", "--install", base / "build"],
    ]
    for name, args in zip(("configure", "build", "install"), commands):
        with (logs / ("sdl-" + name + ".log")).open("w") as stream:
            subprocess.run([str(a) for a in args], check=True, stdout=stream, stderr=subprocess.STDOUT)
    return config


if __name__ == "__main__":
    print(prepare_sdl())
