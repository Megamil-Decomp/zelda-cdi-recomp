#!/usr/bin/env python3
"""Run a bounded, repeatable REA investigation on a prepared private module.

Runs static analysis only. Never launches a game, changes a source image,
promotes seeds, or installs/registers tools. Full REA Evidence stays private.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys

from prepare_rea_module import (MAX_MODULE_BYTES, MODULE_BASE, ROOT, analysis_image,
                                inspect_module, observed_seeds, output_destination)


def read_json(path, maximum=32 * 1024 * 1024):
    if path.stat().st_size > maximum:
        raise ValueError("JSON exceeds finite input limit")
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError("JSON input must be an object")
    return value


def verified_input(directory):
    """Recheck bytes instead of trusting a stale analysis manifest."""
    directory = directory.resolve()
    manifest = read_json(directory / "manifest.json", 1024 * 1024)
    paths = [directory / name for name in ("module.bin", "analysis.bin", "seeds.tsv")]
    if any(path.is_symlink() or path.resolve().parent != directory for path in paths):
        raise ValueError("prepared files must be regular files inside the input directory")
    module, envelope, seeds = paths
    if module.stat().st_size > MAX_MODULE_BYTES or envelope.stat().st_size > MAX_MODULE_BYTES + MODULE_BASE:
        raise ValueError("prepared image exceeds finite size limit")
    data = module.read_bytes()
    info = inspect_module(data)
    if manifest.get("analysis_only") is not True or manifest.get("module") != info:
        raise ValueError("prepared module identity/metadata mismatch")
    if envelope.read_bytes() != analysis_image(data):
        raise ValueError("analysis envelope differs from preserved module and synthetic prefix")
    digest = hashlib.sha256(envelope.read_bytes()).hexdigest()
    if manifest.get("analysis_sha256") != digest:
        raise ValueError("analysis envelope SHA-256 mismatch")
    if seeds.stat().st_size > 2 * 1024 * 1024:
        raise ValueError("analysis seed file exceeds finite size limit")
    count = 0
    for line in seeds.read_text().splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        words = line.split()
        if len(words) != 2 or words[1] != "code" or not words[0].startswith("0x"):
            raise ValueError("only explicit code seeds are allowed")
        offset = int(words[0], 16) - MODULE_BASE
        if offset & 1 or not info["metadata_end"] <= offset < info["code_limit_exclusive"]:
            raise ValueError("analysis seed is outside validated module code bounds")
        count += 1
    if count > 32770:
        raise ValueError("too many analysis seeds")
    return info, envelope, seeds


def hotspots(document, info, limit):
    offsets, coverage = observed_seeds(document, info)
    registry = document.get("module_targets", document)
    hits = {}
    for row in registry["targets"]:
        if row["sha256"].lower() == info["sha256"]:
            hits[row["offset"]] = hits.get(row["offset"], 0) + row["hits"]
    ordered = sorted(offsets, key=lambda offset: (-hits[offset], offset))
    return ordered[:limit], offsets, coverage


def execute(command, env, stdout_path, stderr_path, timeout=180):
    """Give owned CLI helpers a graceful cancellation interval on timeout."""
    with stdout_path.open("xb") as out, stderr_path.open("xb") as err:
        process = subprocess.Popen(command, env=env, stdout=out, stderr=err,
                                   start_new_session=True)
        try:
            return process.wait(timeout), False
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(10)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(5)
            return process.returncode, True


def investigate(prepared, output, targets=None, limit=3):
    if type(limit) is not int or not 0 <= limit <= 16:
        raise ValueError("hotspot limit must be between 0 and 16")
    info, envelope, seeds = verified_input(prepared)
    destination = output_destination(output)
    selected, candidates, target_info = [], [], None
    if targets is not None:
        selected, candidates, target_info = hotspots(targets, info, limit)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.mkdir()
    env = os.environ.copy()
    env["REA_GHIDRA_SEED_FILE"] = str(seeds)
    envelope_digest = hashlib.sha256(envelope.read_bytes()).hexdigest()
    common = ["--target-format", "raw-binary", "--architecture", "m68k",
              "--entry-point", "0x0", "--provider", "ghidra", "--json"]
    jobs = [("load-image", "inspect-native-load-image", []),
            ("entry-function", "function", [hex(MODULE_BASE + info["entry_offset"])])]
    jobs += [(f"hotspot-{offset:x}", "inspect-native-instruction",
              [hex(MODULE_BASE + offset)]) for offset in selected]
    report = {"module": info, "input": str(prepared.resolve()),
              "observed_targets": target_info, "operations": [],
              "static_analysis_only": True, "runtime_changed": False,
              "limitations": ["Code seeds do not prove function boundaries or ISA legality.",
                              "The envelope shifts module addresses by 0x100; absolute literals are not relocated.",
                              "Ghidra accepts a 68040 superset and does not model the OS-9 ABI.",
                              "Pseudocode and static observations do not prove execution equivalence."]}
    for label, operation, selectors in jobs:
        command = [sys.executable, str(ROOT / "scripts/run_rea.py"), operation,
                   str(envelope), *selectors, *common]
        code, timed_out = execute(command, env, destination / (label + ".json"),
                                  destination / (label + ".stderr"))
        item = {"label": label, "command": command, "exit_code": code,
                "timed_out": timed_out, "evidence_id": None, "success": False}
        try:
            evidence = read_json(destination / (label + ".json"), 16 * 1024 * 1024)
            item["evidence_id"] = evidence.get("evidence_id")
            expected_operation = {"inspect-native-load-image": "inspect_native_load_image",
                                  "function": "analyze_function",
                                  "inspect-native-instruction": "inspect_native_instruction"}[operation]
            subject = evidence.get("subject", {})
            provider = evidence.get("provider", {})
            digest = subject.get("digest") if isinstance(subject, dict) else None
            item["identity_verified"] = (isinstance(subject, dict) and
                isinstance(digest, dict) and digest.get("sha256") == envelope_digest and
                subject.get("architecture") == "m68k" and
                isinstance(provider, dict) and provider.get("id") == "ghidra" and
                evidence.get("operation") == expected_operation)
            item["success"] = (code == 0 and isinstance(item["evidence_id"], str) and
                               item["identity_verified"])
            item["operation"] = evidence.get("operation")
            result = evidence.get("normalized_result")
            if isinstance(result, dict):
                item["status"] = result.get("status")
            if label == "load-image":
                item["success"] = item["success"] and item.get("status") == "verified"
            if not item["success"]:
                item["error"] = evidence.get("message", "analysis did not return verified Evidence")
        except (OSError, ValueError) as exc:
            item["error"] = str(exc)
        report["operations"].append(item)
        (destination / "report.json").write_text(json.dumps(report, indent=2) + "\n")
        if not item["success"]:
            break
    report["procedure_completed"] = (len(report["operations"]) == len(jobs) and
                                     all(item["success"] for item in report["operations"]))
    # These are explicit experimental inputs to the strict emitter, never
    # automatically passed to a build or activated in the user's application.
    if target_info and target_info["registry_complete"]:
        (destination / "unvalidated-module.seeds").write_text(
            "# Experimental: requires strict emission and runtime comparison.\n" +
            "".join(f"{info['sha256']} {offset:08x}\n" for offset in candidates))
        report["candidate_seed_count"] = len(candidates)
        report["candidate_seeds_validated_for_runtime"] = False
    (destination / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prepared", type=Path)
    parser.add_argument("--targets", type=Path)
    parser.add_argument("--hotspots", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = investigate(args.prepared, args.output,
                             read_json(args.targets) if args.targets else None, args.hotspots)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"REA investigation failed: {exc}\n")
    print(f"REA operations completed: {report['procedure_completed']}; private report: {args.output / 'report.json'}")
    return 0 if report["procedure_completed"] else 1


if __name__ == "__main__":
    sys.exit(main())
