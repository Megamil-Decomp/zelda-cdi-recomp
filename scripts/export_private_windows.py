#!/usr/bin/env python3
"""Build and export a private Windows x64 test package from accepted inputs."""
import argparse
from datetime import datetime
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import tarfile
import urllib.request
import zipfile

from build_windows_runtimes import digest, SDL_VERSION
from export_private_macos import media_plan, copy_media

ROOT = Path(__file__).resolve().parents[1]
SDL_ARCHIVE_HASH = "83a5d74012311edc3c0d40ea6faecbe57ad692aa033fa5dc273cc937e3938ff2"
SDL_DLL_HASH = "53e8fa7e9ed43c30bd650c39396f0d9d2067d2fff0b926c9433b75202592e4aa"
SYSTEM_DLLS = {"kernel32.dll", "user32.dll", "gdi32.dll", "shell32.dll", "advapi32.dll",
               "bcrypt.dll", "ws2_32.dll", "msvcrt.dll", "ntdll.dll", "ole32.dll", "oleaut32.dll",
               "imm32.dll", "winmm.dll", "version.dll", "setupapi.dll", "comdlg32.dll",
               "comctl32.dll", "dinput8.dll", "hid.dll", "uxtheme.dll"}


def pe_x64(path):
    with Path(path).open("rb") as f:
        if f.read(2) != b"MZ":
            raise ValueError("Not a Windows executable")
        f.seek(0x3c)
        offset = struct.unpack("<I", f.read(4))[0]
        f.seek(offset)
        if f.read(4) != b"PE\0\0" or f.read(2) != b"\x64\x86":
            raise ValueError("Windows x64 PE required")


def check_imports(binary, directory, objdump="x86_64-w64-mingw32-objdump"):
    result = subprocess.run([objdump, "-p", str(binary)], check=True, capture_output=True, text=True)
    imports = re.findall(r"DLL Name:\s*(\S+)", result.stdout)
    packaged = {p.name.lower() for p in directory.glob("*.dll")}
    missing = [n for n in imports if n.lower() not in SYSTEM_DLLS and
               not n.lower().startswith(("api-ms-win-", "ext-ms-win-")) and n.lower() not in packaged]
    if missing:
        raise ValueError("Unbundled DLLs: " + ", ".join(missing))
    return imports


def wide(text):
    return "L" + json.dumps(text, ensure_ascii=True)


def package_header(manifest, rows, runtimes):
    files = {row["relative"]: row for row in rows}
    bios = manifest["bios"]
    runtime_hash = bios.get("runtime_sha256", bios["sha256"])
    swap = bios["sha256"] != runtime_hash
    if swap and bios.get("byte_order") != "swap16":
        raise ValueError("Unsupported BIOS normalization")
    lines = ["/* Generated private metadata; never commit this file. */",
             "#define BIOS_RELATIVE " + wide(bios["local_relative"].replace("/", "\\")),
             '#define BIOS_HASH "' + bios["sha256"] + '"',
             '#define BIOS_RUNTIME_HASH "' + runtime_hash + '"',
             "#define BIOS_SIZE " + str(bios["size"]), "#define BIOS_SWAP16 " + str(int(swap)),
             "static const Game games[3] = {"]
    for g in manifest["games"]:
        cue = g["local_cue_relative"]
        folder = str(Path(cue).parent).replace("\\", "/") + "/"
        images = [key for key in files if key.startswith(folder) and key != cue]
        if len(images) != 1:
            raise ValueError("CUE must have one exported image")
        strings = [g["id"], g["title"], "CdiRuntime-" + g["id"] + ".exe", cue, images[0]]
        values = [wide(v.replace("/", "\\")) for v in strings]
        values += [json.dumps(runtimes[g["id"]]), json.dumps(g["disc_sha256"]), json.dumps(files[cue]["sha256"])]
        lines.append("    {" + ", ".join(values) + "},")
    return "\n".join(lines + ["};", ""])


def ensure_sdl():
    tools = ROOT / "build/windows/tools"
    sdk = tools / ("SDL2-" + SDL_VERSION)
    if (sdk / "x86_64-w64-mingw32/bin/SDL2.dll").is_file():
        if digest(sdk / "x86_64-w64-mingw32/bin/SDL2.dll") != SDL_DLL_HASH:
            raise ValueError("Cached official SDL DLL identity mismatch")
        return sdk
    tools.mkdir(parents=True, exist_ok=True)
    filename = "SDL2-devel-" + SDL_VERSION + "-mingw.tar.gz"
    archive = tools / filename
    urllib.request.urlretrieve("https://github.com/libsdl-org/SDL/releases/download/release-" + SDL_VERSION + "/" + filename, archive)
    if digest(archive) != SDL_ARCHIVE_HASH:
        raise ValueError("Official SDL SDK identity mismatch")
    with tarfile.open(archive) as tar:
        for member in tar.getmembers():
            if not (tools / member.name).resolve().is_relative_to(tools.resolve()) or not (member.isfile() or member.isdir()):
                raise ValueError("Unsafe SDK archive entry")
        tar.extractall(tools)
    if digest(sdk / "x86_64-w64-mingw32/bin/SDL2.dll") != SDL_DLL_HASH:
        raise ValueError("Extracted official SDL DLL identity mismatch")
    return sdk


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--skip-build", action="store_true", help="reuse Windows binaries only if accepted provenance still matches")
    args = parser.parse_args()
    compiler = shutil.which("x86_64-w64-mingw32-gcc")
    if not compiler:
        parser.error("Install MinGW x64 (on this Mac: brew install mingw-w64)")
    output = (args.output or ROOT / "dist/exports-windows" / datetime.now().astimezone().strftime("export-%Y%m%d-%H%M%S")).resolve()
    if not any(output.is_relative_to(ROOT / p) for p in ["dist", "build", "data/private"]) or output.exists():
        parser.error("Choose a new destination inside ignored dist/, build/ or data/private/")
    sdk = ensure_sdl()
    if not args.skip_build:
        subprocess.run([sys.executable, str(ROOT / "scripts/build_windows_runtimes.py")], check=True)
    from build_macos_app import load_runtime_catalog
    from build_windows_runtimes import accepted_inputs
    catalog = load_runtime_catalog(ROOT / "data/private/rea-titles/runtime-catalog.json")
    source = ROOT / "dist/Zelda CD-i.app/Contents/Resources"
    manifest = json.loads((source / "runtime-manifest.json").read_text())
    rows = media_plan(manifest, ROOT)
    runtimes = {}
    for game in manifest["games"]:
        name = game["id"]
        accepted_inputs(catalog[name]["path"])
        binary = ROOT / "build/windows" / ("runtime-" + name) / "CdiRuntime.exe"
        report = json.loads(binary.with_name("windows-build.json").read_text())
        if (report["mac_accepted_runtime_sha256"] != catalog[name]["sha256"] or
                game["source_runtime_sha256"] != catalog[name]["sha256"] or digest(binary) != report["runtime_sha256"]):
            raise ValueError("Stale Windows runtime: " + name)
        pe_x64(binary)
        runtimes[name] = digest(binary)
    output.mkdir(parents=True)
    package = output / "Zelda CD-i Windows"
    package.mkdir()
    print("Copying accepted Windows runtimes and local media…", flush=True)
    copy_media(rows, package)
    for name in runtimes:
        shutil.copy2(ROOT / "build/windows" / ("runtime-" + name) / "CdiRuntime.exe", package / ("CdiRuntime-" + name + ".exe"))
    shutil.copy2(sdk / "x86_64-w64-mingw32/bin/SDL2.dll", package / "SDL2.dll")
    (package / "mods").mkdir()
    for n in ["adventure-ptbr.txt", "adventure-menu-ptbr.txt"]:
        shutil.copy2(source / n, package / "mods" / n)
    shutil.copytree(source / "Licenses", package / "Licenses")
    shutil.copy2(sdk / "LICENSE.txt", package / "Licenses/SDL2-Windows-LICENSE.txt")
    work = ROOT / "build/windows/launcher"
    work.mkdir(exist_ok=True)
    (work / "package_config.h").write_text(package_header(manifest, rows, runtimes))
    (work / "app.rc").write_text('1 24 "' + (ROOT / "app/windows/app.manifest").as_posix() + '"\n')
    subprocess.run([str(Path(compiler).with_name("x86_64-w64-mingw32-windres")), str(work / "app.rc"), "-o", str(work / "manifest.o")], check=True)
    subprocess.run([compiler, "-std=c11", "-O2", "-Wall", "-Wextra", "-municode", "-mwindows", "-static-libgcc",
                    "-I", str(work), str(ROOT / "app/windows/Launcher.c"), str(work / "manifest.o"),
                    "-o", str(package / "ZeldaCDi.exe"), "-lbcrypt", "-lshell32", "-lole32", "-lgdi32", "-luuid"], check=True)
    imports = {}
    for binary in [*package.glob("*.exe"), *package.glob("*.dll")]:
        pe_x64(binary)
        imports[binary.name] = check_imports(binary, package)
    (package / "LEIA-ME.txt").write_text(
        "Zelda CD-i — Windows x64 experimental\n\n"
        "Windows 10 1903+ ou Windows 11, x64.\n"
        "Extraia a pasta inteira e abra ZeldaCDi.exe. Escolha o jogo e clique em Iniciar jogo.\n"
        "Não precisa instalar Python, REA, compilador ou SDL. Mantenha todos os arquivos juntos.\n"
        "A primeira verificação de mídia pode levar alguns segundos.\n"
        "Saves e logs: %LOCALAPPDATA%\\ZeldaCDiNative, separados por título. Saves pessoais não incluídos.\n"
        "Feche a janela do jogo ou use Parar para salvar. Não force encerramento.\n"
        "Controles: setas/WASD; ação: Espaço/Enter/Z; secundário: X/Backspace.\n"
        "Build cross-compilada no Mac; gameplay no Windows ainda precisa do teste real.\n", encoding="utf-8-sig")
    metadata = {"platform": "windows-x64", "experimental": True, "execution_validated": False,
                "runtimes": runtimes, "dll_imports": imports,
                "files": {str(p.relative_to(package)): digest(p) for p in package.rglob("*") if p.is_file()}}
    (package / "package-report.json").write_text(json.dumps(metadata, indent=2) + "\n")
    archive = output / "Zelda-CDi-Windows-Completo.zip"
    print("Creating Windows ZIP…", flush=True)
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for path in package.rglob("*"):
            if path.is_file(): z.write(path, path.relative_to(output))
    with zipfile.ZipFile(archive) as z:
        if z.testzip(): raise ValueError("ZIP integrity failed")
    (output / "export-report.json").write_text(json.dumps({"zip_sha256": digest(archive), "bytes": archive.stat().st_size,
                                                          "execution_on_windows_validated": False}, indent=2) + "\n")
    print("Ready: " + str(archive), flush=True)


if __name__ == "__main__":
    main()
