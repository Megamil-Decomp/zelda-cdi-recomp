#!/usr/bin/env python3
"""Run the project's isolated REA CLI without changing agent registrations.

Tool paths and versions are in ignored build/rea-tools/toolchain.json.
All analysis workspaces stay below ignored build/rea-tools/tmp/.
"""
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def main():
    config = ROOT / "build/rea-tools/toolchain.json"
    try:
        tools = json.loads(config.read_text())
        paths = {key: Path(tools[key]).resolve() for key in
                 ("node", "rea", "ghidra", "java_home")}
        for key, path in paths.items():
            if not path.exists():
                raise ValueError(f"{key} is missing: {path}")
        temporary = ROOT / "build/rea-tools/tmp"
        temporary.mkdir(parents=True, exist_ok=True)
        env = os.environ.copy()
        env.update({"PATH": str(paths["node"].parent) + os.pathsep + env.get("PATH", ""),
                    "GHIDRA_INSTALL_DIR": str(paths["ghidra"]),
                    "JAVA_HOME": str(paths["java_home"]), "TMPDIR": str(temporary)})
        return subprocess.run([str(paths["node"]), str(paths["rea"]), *sys.argv[1:]],
                              env=env).returncode
    except (OSError, ValueError, KeyError) as exc:
        print(f"REA toolchain unavailable: {exc}; see docs/REA_PILOT_PLAN.md", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
