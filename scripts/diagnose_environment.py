#!/usr/bin/env python3
"""Inspect the host toolchain without installing packages or reading game media."""

import argparse
import json
import platform
import shutil
import subprocess
from pathlib import Path


def run(argv):
    try:
        result = subprocess.run(argv, text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=20)
        return {"command": argv, "exit_code": result.returncode,
                "output": result.stdout.strip()}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"command": argv, "exit_code": None, "output": str(exc)}


def diagnose():
    commands = {
        "clang": ["clang", "--version"],
        "cmake": ["cmake", "--version"],
        "python3": ["python3", "--version"],
        "git": ["git", "--version"],
        "make": ["make", "--version"],
        "ninja": ["ninja", "--version"],
        "pkg-config": ["pkg-config", "--version"],
        "sdl2-config": ["sdl2-config", "--version"],
    }
    tools = {}
    for name, argv in commands.items():
        path = shutil.which(name)
        tools[name] = {"path": path, "present": path is not None}
        if path:
            tools[name].update(run(argv))
    report = {"system": platform.system(), "machine": platform.machine(),
              "python": platform.python_version(), "tools": tools}
    if platform.system() == "Darwin":
        report["macos"] = run(["sw_vers"])
        report["xcode"] = run(["xcode-select", "-p"])
        report["sdk"] = run(["xcrun", "--show-sdk-path"])
        report["hardware"] = run(["sysctl", "-n", "hw.ncpu", "hw.memsize"])
    required = ("clang", "cmake", "python3", "git", "make")
    report["missing_required"] = [name for name in required
                                  if not tools[name]["present"]]
    report["failed_required"] = [name for name in required
                                 if tools[name]["present"]
                                 and tools[name].get("exit_code") != 0]
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, help="write a private JSON report")
    args = parser.parse_args()
    report = diagnose()
    print("Host: {} {}".format(report["system"], report["machine"]))
    if "macos" in report:
        print(report["macos"]["output"])
    for name, entry in report["tools"].items():
        if not entry["present"]:
            print("{}: absent".format(name))
        else:
            first_line = entry.get("output", "").splitlines()
            print("{}: {} (exit {})".format(
                name, first_line[0] if first_line else "no output",
                entry.get("exit_code")))
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
        print("Private report: {}".format(args.json))
    return 1 if report["missing_required"] or report["failed_required"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
