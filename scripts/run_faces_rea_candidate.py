#!/usr/bin/env python3
"""Launch the locally tested REA Faces candidate with a separate battery.

This is an experimental local build, not campaign compatibility certification.
Requires the private pilot artifacts. No downloads or changes to the main app.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import sys
import uuid

from verify_local_media import parse_cue, sha256_file


ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "data/private/rea-pilot"


def exit_observation(returncode):
    """Keep a host signal distinct from a normal player shutdown or hang."""
    if type(returncode) is not int:
        return {"kind": "unknown", "returncode": None, "signal": None, "shell_status": 2}
    if returncode < 0:
        try:
            name = signal.Signals(-returncode).name
        except ValueError:
            name = f"SIGNAL_{-returncode}"
        return {"kind": "signal", "returncode": returncode, "signal": name,
                "shell_status": 128 - returncode}
    return {"kind": "exited", "returncode": returncode, "signal": None,
            "shell_status": returncode}


def run_session(command, env, log):
    """Persist session completion even when the native process crashes."""
    metadata_path = log.with_suffix(".json")
    metadata = {"schema_version": 1, "command": command, "log": str(log),
                "started_utc": datetime.now(timezone.utc).isoformat(),
                "state": "launching", "runtime_sha256": sha256_file(Path(command[0])),
                "player_config": env.get("CDI_PLAYER_CONFIG_PATH"),
                "exit": None, "hang_established": False}
    with metadata_path.open("x") as stream:
        json.dump(metadata, stream, indent=2)
    process = None
    try:
        with log.open("xb") as stream:
            process = subprocess.Popen(command, env=env, stdout=stream, stderr=subprocess.STDOUT)
            metadata.update(state="running", pid=process.pid)
            metadata_path.write_text(json.dumps(metadata, indent=2) + "\n")
            try:
                process.wait()
            except KeyboardInterrupt:
                metadata["interrupted_by_user"] = True
                if process.poll() is None:
                    process.send_signal(signal.SIGINT)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.terminate()
                    try:
                        process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=3)
            metadata["exit"] = exit_observation(process.returncode)
            metadata["state"] = "finished"
    except OSError as exc:
        metadata.update(state="launch_failed", error=str(exc), exit=exit_observation(None))
    finally:
        metadata["ended_utc"] = datetime.now(timezone.utc).isoformat()
        metadata_path.write_text(json.dumps(metadata, indent=2) + "\n")
    observation = metadata["exit"]
    print(f"Session result: {observation['kind']}; return code: {observation['returncode']}; "
          f"signal: {observation['signal'] or 'none'}")
    print(f"Private session report: {metadata_path}")
    return observation["shell_status"]


def checked_inputs(candidate_name=None):
    experiments = json.loads((PRIVATE / "experiment-manifest.json").read_text())
    selected = candidate_name or experiments.get("interactive_candidate", "menu")
    candidate = next(item for item in experiments["experiments"] if item["name"] == selected)
    runtime = Path(candidate["runtime"]).resolve()
    if not runtime.is_relative_to(ROOT / "build") or sha256_file(runtime) != candidate["runtime_sha256"]:
        raise ValueError("experimental runtime identity changed; regenerate the private pilot manifest")
    source = json.loads((PRIVATE / "faces-module/manifest.json").read_text())["source"]
    cue = Path(source["cue"]).resolve()
    image = parse_cue(cue)
    if (sha256_file(cue) != source["cue_sha256"] or
            sha256_file(image) != source["image_sha256"]):
        raise ValueError("disc identity differs from the candidate analysis")
    bios = ROOT / "build/native/input/cdi490a.be.rom"
    bios_info = json.loads((ROOT / "build/native/input/bios-info.json").read_text())
    if sha256_file(bios) != bios_info["runtime_sha256"]:
        raise ValueError("normalized BIOS identity changed")
    return runtime, bios, cue


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify private inputs without launching or writing")
    parser.add_argument("--port", type=int, default=4503)
    parser.add_argument("--candidate", help="explicit private experiment name; default comes from the verified manifest")
    parser.add_argument("--fault-hold", action="store_true", help="keep supported fault diagnostics queryable")
    args = parser.parse_args()
    try:
        if not 1024 <= args.port <= 65535:
            raise ValueError("port must be between 1024 and 65535")
        runtime, bios, cue = checked_inputs(args.candidate)
        if args.check:
            print("Experimental Faces runtime, normalized BIOS and disc identities verified.")
            return 0
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", args.port))
        player = PRIVATE / "interactive-player"
        if player.is_symlink():
            raise ValueError("interactive player directory must not be a symlink")
        player.mkdir(exist_ok=True)
        config = player / "player.cfg"
        battery = player / "nvram.bin"
        if config.is_symlink() or battery.is_symlink():
            raise ValueError("interactive player configuration/battery must not be symlinks")
        if not config.exists():
            config.write_text("[input]\ncapture_mouse = false\n\n[rtc]\nsync_host_on_startup = false\n")
        if not battery.exists():
            original = ROOT / "data/private/probes/rea-faces-baseline/nvram.bin"
            if original.stat().st_size != 32768:
                raise ValueError("pilot battery is unavailable or invalid")
            shutil.copyfile(original, battery)
        env = os.environ.copy()
        env.update(CDI_PLAYER_CONFIG_PATH=str(config), CDI_PACE_SPEED="1.0")
        for key in ("SDL_VIDEODRIVER", "SDL_AUDIODRIVER", "CDI_MENU_MOD_PATH", "CDI_TEXT_MOD_PATH"):
            env.pop(key, None)
        log = player / ("session-" + uuid.uuid4().hex + ".log")
        print("Launching experimental Faces at 1x with a separate battery.")
        print(f"Private log: {log}")
        command = [str(runtime), str(bios), "--disc", str(cue), "--port", str(args.port)]
        if args.fault_hold:
            command.append("--fault-hold")
        return run_session(command, env, log)
    except (OSError, ValueError, KeyError, StopIteration) as exc:
        print(f"Cannot launch experimental Faces: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
