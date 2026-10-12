#!/usr/bin/env python3
"""Observe a local CD-i runtime through its public development TCP protocol.

No guest RAM, CPU registers, execution entrypoints or disc bytes are changed.
Evidence is private; procedure completion does not imply gameplay acceptance.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import socket
import struct
import subprocess
import sys
import time
import zlib


class Probe:
    def __init__(self, port: int, output: Path, timeout: float):
        self.port = port
        self.output = output
        self.timeout = timeout
        self.process: subprocess.Popen | None = None

    def request(self, cmd: str, **params) -> dict:
        with socket.create_connection(("127.0.0.1", self.port), timeout=1.0) as sock:
            sock.settimeout(2.0)
            sock.sendall((json.dumps({"cmd": cmd, **params}) + "\n").encode())
            data = bytearray()
            while b"\n" not in data:
                chunk = sock.recv(65536)
                if not chunk:
                    raise RuntimeError("debug server closed without a reply")
                data.extend(chunk)
                if len(data) > 2 * 1024 * 1024:
                    raise RuntimeError("debug reply exceeded the finite size limit")
        result = json.loads(data.partition(b"\n")[0])
        if not isinstance(result, dict):
            raise RuntimeError("debug reply was not an object")
        return result

    def snapshot(self) -> dict:
        result = {}
        for cmd in ("status", "video_frame", "video_state", "disc_state",
                    "ciap_state", "audio_state", "native_state", "interp_report"):
            try:
                result[cmd] = self.request(cmd, **({"count": 0} if cmd == "interp_report" else {}))
            except (OSError, ValueError, RuntimeError) as exc:
                result[cmd] = {"error": str(exc)}
        return result

    def wait_shell(self, minimum_frame: int) -> dict:
        deadline = time.monotonic() + self.timeout
        previous_frame = None
        last = {}
        while time.monotonic() < deadline:
            if self.process is not None and self.process.poll() is not None:
                raise RuntimeError(f"runtime exited during boot: {self.process.returncode}")
            try:
                last = self.request("status")
                driver = self.request("emu_ikat_state")
                video = self.request("video_state")
                frame = int(last.get("frame", 0))
                regs = driver.get("regs", [])
                if (last.get("halted") == 1 and not last.get("held") and
                        frame >= minimum_frame and previous_frame is not None and
                        frame > previous_frame and len(regs) >= 14 and
                        (regs[13] & 2) and video.get("cursor_enabled")):
                    return {"status": last, "driver": driver, "video": video}
                if last.get("held"):
                    raise RuntimeError("runtime held before reaching a live shell")
                previous_frame = frame
            except (OSError, ValueError) as exc:
                last = {"error": str(exc)}
            time.sleep(0.05)
        raise RuntimeError(f"boot deadline expired; last status={last}")

    def click(self, x: int, y: int) -> dict:
        deadline = time.monotonic() + min(self.timeout, 15.0)
        moves = []
        while time.monotonic() < deadline:
            position = self.request("video_state")
            dx, dy = x - position["cursor_x"], y - position["cursor_y"]
            if abs(dx) <= 2 and abs(dy) <= 2:
                break
            moves.append({"dx": dx, "dy": dy, "frame": self.request("status").get("frame")})
            self.request("set_input", mask=0, dx=dx, dy=dy)
            time.sleep(0.1)
        else:
            raise RuntimeError(f"cursor failed to reach ({x}, {y})")
        start = self.request("ikat_events").get("total", 0)
        press = None
        release = None
        events = []
        self.request("set_input", mask=16)
        try:
            deadline = time.monotonic() + 5.0
            while time.monotonic() < deadline:
                events = [event for event in self.request("ikat_events").get("events", [])
                          if event["seq"] >= start]
                press = next((event for event in events if
                              event.get("type") == 2 and event.get("channel") == 0 and
                              len(event.get("data", "")) >= 2 and
                              int(event["data"][:2], 16) & 0x20), None)
                if press is not None:
                    break
                time.sleep(0.005)
        finally:
            self.request("set_input", mask=0)
        if press is None:
            raise RuntimeError("button press was not published by timed IKAT")
        deadline = time.monotonic() + 5.0
        while time.monotonic() < deadline:
            events = [event for event in self.request("ikat_events").get("events", [])
                      if event["seq"] >= start]
            release = next((event for event in events if
                            event.get("type") == 2 and event.get("channel") == 0 and
                            event["seq"] > press["seq"] and
                            len(event.get("data", "")) >= 2 and
                            not int(event["data"][:2], 16) & 0x20), None)
            if release is not None:
                break
            time.sleep(0.005)
        if release is None:
            raise RuntimeError("button release was not published by timed IKAT")
        return {"target": [x, y], "position": position, "moves": moves,
                "press_seq": press["seq"], "release_seq": release["seq"],
                "guest_read_observed": any(event.get("type") == 5 and
                                           event.get("channel") == 0 for event in events)}

    def screenshot(self) -> dict:
        acknowledgement = self.request("pause")
        if not acknowledgement.get("ok"):
            raise RuntimeError("pause request rejected")
        deadline = time.monotonic() + 5.0
        last = None
        stable_since = None
        while time.monotonic() < deadline:
            state = self.request("status")
            blocks = state.get("blocks")
            now = time.monotonic()
            if blocks != last:
                last, stable_since = blocks, now
            elif stable_since is not None and now - stable_since > 0.15 and state.get("held"):
                break
            time.sleep(0.02)
        else:
            raise RuntimeError("runtime did not park for a consistent screenshot")
        info = self.request("video_frame")
        width, height = int(info["width"]), int(info["height"])
        if not (0 < width <= 4096 and 0 < height <= 4096):
            raise RuntimeError("invalid framebuffer dimensions")
        pixels = bytearray()
        generation = None
        capture_deadline = time.monotonic() + 20.0
        for y in range(height):
            if time.monotonic() > capture_deadline:
                raise RuntimeError("screenshot capture deadline expired")
            row = self.request("video_scanline", y=y)
            if generation is None:
                generation = row["generation"]
            if (row["generation"] != generation or int(row["width"]) != width or
                    int(row["height"]) != height):
                raise RuntimeError("frame changed while paused")
            argb = bytes.fromhex(row["argb"])
            if len(argb) != width * 4:
                raise RuntimeError("incomplete framebuffer scanline")
            pixels.append(0)  # PNG scanline filter: none.
            for x in range(width):
                pixels.extend(argb[x * 4 + 1:x * 4 + 4])
        def chunk(kind: bytes, data: bytes) -> bytes:
            return (struct.pack(">I", len(data)) + kind + data +
                    struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))
        png = (b"\x89PNG\r\n\x1a\n" +
               chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)) +
               chunk(b"IDAT", zlib.compress(bytes(pixels))) + chunk(b"IEND", b""))
        path = self.output / "final.png"
        path.write_bytes(png)
        return {**info, "generation": generation, "path": str(path)}


def coverage(snapshot: dict) -> dict:
    report = snapshot.get("interp_report", {})
    native, interpreted = report.get("native", 0), report.get("total", 0)
    count = native + interpreted
    return {"native_instructions": native, "interpreted_instructions": interpreted,
            "native_percent": 100.0 * native / count if count else None,
            "includes_bios": True, "dropped": report.get("dropped")}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runtime", type=Path)
    parser.add_argument("bios", type=Path)
    parser.add_argument("disc", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--port", type=int, default=4490)
    parser.add_argument("--mode", choices=("shell", "launch"), default="shell")
    parser.add_argument("--play-x", type=int)
    parser.add_argument("--play-y", type=int)
    parser.add_argument("--timeout", type=float, default=90.0)
    parser.add_argument("--observe", type=float, default=20.0)
    parser.add_argument("--minimum-frame", type=int, default=1000)
    parser.add_argument("--pace", type=float, default=1.0)
    parser.add_argument("--initialize-battery", action="store_true")
    parser.add_argument("--headless", action="store_true",
                        help="disable frontend entirely (also disables player battery persistence)")
    args = parser.parse_args()
    if args.mode == "launch" and (args.play_x is None or args.play_y is None):
        parser.error("launch requires a visually verified --play-x and --play-y")
    if not (0 < args.timeout <= 300 and 0 <= args.observe <= 600 and 0 < args.pace <= 100):
        parser.error("timeout/observe/pace are outside the finite allowed range")
    for name in ("runtime", "bios", "disc"):
        path = getattr(args, name).resolve()
        if not path.is_file():
            parser.error(f"{name} does not exist: {path}")
        setattr(args, name, path)
    output = args.output.resolve()
    private_root = Path(__file__).resolve().parents[1] / "data" / "private" / "probes"
    if not output.is_relative_to(private_root):
        parser.error(f"output must remain under {private_root}")
    output.mkdir(parents=True, exist_ok=True)
    with socket.socket() as test:
        try:
            test.bind(("127.0.0.1", args.port))
        except OSError:
            parser.error("requested port is occupied; refusing to query another process")
    env = os.environ.copy()
    env.update({"SDL_VIDEODRIVER": "dummy", "SDL_AUDIODRIVER": "dummy",
                "CDI_PLAYER_CONFIG_PATH": str(output / "player.cfg"),
                "CDI_PACE_SPEED": str(args.pace)})
    command = [str(args.runtime), str(args.bios), "--disc", str(args.disc),
               "--port", str(args.port), "--fault-hold"]
    if args.headless:
        command.append("--headless")
    report = {"mode": args.mode, "command": command, "pace": args.pace,
              "gameplay_accepted": False, "procedure_completed": False,
              "limitations": ["No gameplay identity/response acceptance is automated.",
                              "Global instruction ratios include BIOS execution."]}
    probe = Probe(args.port, output, args.timeout)
    with (output / "stdout.log").open("wb") as stdout, (output / "stderr.log").open("wb") as stderr:
        try:
            if args.initialize_battery:
                initialized = subprocess.run(command + ["--exit-on-stop"], stdout=stdout,
                                             stderr=stderr, env=env, timeout=args.timeout)
                report["battery_initialize_returncode"] = initialized.returncode
                if initialized.returncode:
                    raise RuntimeError("battery initialization did not exit successfully")
            probe.process = subprocess.Popen(command, stdout=stdout, stderr=stderr, env=env)
            report["pid"] = probe.process.pid
            report["shell"] = probe.wait_shell(args.minimum_frame)
            report["before"] = probe.snapshot()
            report["coverage_before"] = coverage(report["before"])
            if args.mode == "launch":
                report["click"] = probe.click(args.play_x, args.play_y)
            deadline = time.monotonic() + args.observe
            observations = []
            while time.monotonic() < deadline:
                if probe.process.poll() is not None:
                    raise RuntimeError(f"runtime exited during observation: {probe.process.returncode}")
                sample = probe.snapshot()
                observations.append(sample)
                if sample.get("status", {}).get("held"):
                    report["runtime_held"] = True
                    break
                time.sleep(0.5)
            report["observations"] = observations
            report["procedure_completed"] = True
        except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
            report["error"] = str(exc)
        finally:
            if probe.process is not None:
                if probe.process.poll() is None:
                    report["after"] = probe.snapshot()
                    report["coverage_after"] = coverage(report["after"])
                    try:
                        report["screenshot"] = probe.screenshot()
                    except (OSError, ValueError, RuntimeError, KeyError) as exc:
                        report["screenshot_error"] = str(exc)
                    for cmd in ("ikat_events", "native_events", "module_targets", "dispatch_miss_info"):
                        try:
                            report[cmd] = probe.request(cmd)
                        except (OSError, ValueError, RuntimeError) as exc:
                            report[cmd] = {"error": str(exc)}
                    probe.process.terminate()
                    try:
                        probe.process.wait(3.0)
                    except subprocess.TimeoutExpired:
                        probe.process.kill()
                        probe.process.wait(3.0)
                report["process_returncode"] = probe.process.returncode
            if "coverage_before" in report and "coverage_after" in report:
                before, after = report["coverage_before"], report["coverage_after"]
                native = after["native_instructions"] - before["native_instructions"]
                interpreted = after["interpreted_instructions"] - before["interpreted_instructions"]
                report["coverage_interval"] = {
                    "native_instructions": native, "interpreted_instructions": interpreted,
                    "native_percent": 100 * native / (native + interpreted) if native + interpreted else None,
                    "includes_bios": True}
            (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report.get(key) for key in
                      ("procedure_completed", "gameplay_accepted", "error", "runtime_held", "coverage_interval")}))
    print(f"Private evidence: {output / 'report.json'}")
    return 0 if report["procedure_completed"] else 1


if __name__ == "__main__":
    sys.exit(main())
