"""Synthetic prepared images and fake CLI Evidence; no engine/media required."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import analyze_rea_module as mod
import prepare_rea_module as prepare
from test_prepare_rea_module import fixture


class AutomatedReaTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.prepared = self.root / "data/private/rea-pilot/prepared"
        self.data = fixture()
        self.info = prepare.prepare(self.data, {"synthetic": True}, self.prepared,
                                    root=self.root)["module"]
        self.registry = {"complete": True, "total": 2, "dropped": 0, "targets": [
            {"sha256": self.info["sha256"], "offset": 0x48, "hits": 1},
            {"sha256": self.info["sha256"], "offset": 0x4A, "hits": 20}]}

    def test_prepared_identity_is_rechecked_before_analysis(self):
        info, _, _ = mod.verified_input(self.prepared)
        self.assertEqual(info, self.info)
        path = self.prepared / "analysis.bin"
        path.write_bytes(path.read_bytes()[:-1] + b"\xff")
        with self.assertRaisesRegex(ValueError, "envelope differs"):
            mod.verified_input(self.prepared)

    def test_seed_cannot_claim_data_as_function_or_escape_code_bounds(self):
        path = self.prepared / "seeds.tsv"
        for content in ("0x148\tfunction\n", "0x101\tcode\n", "0x149\tcode\n"):
            path.write_text(content)
            with self.subTest(content=content), self.assertRaises(ValueError):
                mod.verified_input(self.prepared)

    def test_hotspots_use_exact_identity_and_rank_observed_counts(self):
        selected, all_offsets, info = mod.hotspots(self.registry, self.info, 1)
        self.assertEqual(selected, [0x4A])
        self.assertEqual(all_offsets, [0x48, 0x4A])
        self.assertTrue(info["registry_complete"])
        other = copy.deepcopy(self.registry)
        other["targets"][0]["sha256"] = "a" * 64
        self.assertEqual(mod.hotspots(other, self.info, 3)[0], [0x4A])

    def fake_execution(self, command, env, stdout_path, stderr_path):
        digest = hashlib.sha256((self.prepared / "analysis.bin").read_bytes()).hexdigest()
        operation = {"inspect-native-load-image": "inspect_native_load_image",
                     "function": "analyze_function",
                     "inspect-native-instruction": "inspect_native_instruction"}[command[2]]
        value = {"evidence_id": "ev_synthetic", "operation": operation,
                 "subject": {"digest": {"sha256": digest}, "architecture": "m68k"},
                 "provider": {"id": "ghidra"},
                 "normalized_result": {"status": "verified" if operation == "inspect_native_load_image" else "decoded"}}
        stdout_path.write_text(json.dumps(value))
        stderr_path.write_text("")
        return 0, False

    def run_fake(self, registry=None, execute=None):
        out = self.root / "data/private/rea-pilot/analysis"
        with patch.object(mod, "ROOT", self.root), \
                patch.object(mod, "output_destination", side_effect=lambda p: prepare.output_destination(p, self.root)), \
                patch.object(mod, "execute", side_effect=execute or self.fake_execution):
            report = mod.investigate(self.prepared, out, registry, limit=1)
        return report, out

    def test_full_evidence_is_retained_without_activating_candidate_seeds(self):
        report, out = self.run_fake(self.registry)
        self.assertTrue(report["procedure_completed"])
        self.assertEqual(len(report["operations"]), 3)
        self.assertEqual(report["candidate_seed_count"], 2)
        self.assertFalse(report["candidate_seeds_validated_for_runtime"])
        self.assertFalse(report["runtime_changed"])
        self.assertEqual((out / "unvalidated-module.seeds").read_text().count(self.info["sha256"]), 2)

    def test_partial_capture_can_be_analyzed_but_not_exported_for_recompiler(self):
        registry = copy.deepcopy(self.registry)
        registry["complete"] = False
        report, out = self.run_fake(registry)
        self.assertTrue(report["procedure_completed"])
        self.assertFalse((out / "unvalidated-module.seeds").exists())

    def test_wrong_target_evidence_is_rejected_and_not_retried(self):
        calls = []
        def wrong(*args):
            calls.append(args)
            result = self.fake_execution(*args)
            path = args[2]
            value = json.loads(path.read_text())
            value["subject"]["digest"]["sha256"] = "f" * 64
            path.write_text(json.dumps(value))
            return result
        report, _ = self.run_fake(execute=wrong)
        self.assertFalse(report["procedure_completed"])
        self.assertEqual(len(calls), 1)
        self.assertFalse(report["operations"][0]["identity_verified"])

    def test_missing_identity_is_a_failed_observation_not_an_exception(self):
        def missing(*args):
            result = self.fake_execution(*args)
            path = args[2]
            value = json.loads(path.read_text())
            value["subject"]["digest"] = None
            path.write_text(json.dumps(value))
            return result
        report, _ = self.run_fake(execute=missing)
        self.assertFalse(report["procedure_completed"])
        self.assertFalse(report["operations"][0]["identity_verified"])


if __name__ == "__main__":
    unittest.main()
