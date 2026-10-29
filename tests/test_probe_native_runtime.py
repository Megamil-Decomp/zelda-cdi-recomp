"""Synthetic debug replies only; never launches a runtime or reads media."""

import copy
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location(
    "runtime_probe", Path(__file__).resolve().parents[1] / "scripts/probe_native_runtime.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def target(offset, module=0, digest="a" * 64):
    return {"module": module, "offset": offset, "base": 0x200000,
            "epoch": 1, "frame": 100, "trace_seq": 1000, "hits": 3,
            "sha256": digest}


class SyntheticProbe(mod.Probe):
    def __init__(self, rows, mutate=None):
        super().__init__(0, Path("/unused"), 1)
        self.rows = rows
        self.mutate = mutate
        self.calls = []
        self.parked = {"held": 1, "blocks": 1234}
        self.final = self.parked.copy()

    def pause_stable(self):
        self.calls.append(("pause_stable", {}))
        return self.parked

    def request(self, cmd, **params):
        self.calls.append((cmd, params))
        if cmd == "status":
            return self.final
        assert cmd == "module_targets"
        start, count = params["from"], params["count"]
        reply = {"ok": True, "total": len(self.rows), "dropped": 0,
                 "targets": copy.deepcopy(self.rows[start:start + count])}
        if self.mutate:
            self.mutate(reply, start, count)
        return reply


class ModuleTargetTests(unittest.TestCase):
    def test_collects_all_pages_instead_of_default_first_64(self):
        rows = [target(0x100 + 2 * i) for i in range(250)]
        probe = SyntheticProbe(rows)
        result = probe.module_targets()
        self.assertTrue(result["complete"])
        self.assertEqual(result["targets"], rows)
        self.assertEqual(result["captured"], 250)
        self.assertEqual(probe.calls, [
            ("pause_stable", {}),
            ("module_targets", {"from": 0, "count": 0}),
            ("module_targets", {"from": 0, "count": 128}),
            ("module_targets", {"from": 128, "count": 122}),
            ("module_targets", {"from": 250, "count": 0}),
            ("status", {}),
        ])

    def test_empty_ledger_is_complete_only_after_recheck(self):
        result = SyntheticProbe([]).module_targets()
        self.assertTrue(result["complete"])
        self.assertEqual(result["captured"], 0)
        self.assertEqual(result["pages"], 2)

    def test_short_server_page_does_not_look_complete(self):
        def truncate(reply, start, count):
            if count:
                reply["targets"] = reply["targets"][:1]
        result = SyntheticProbe([target(2), target(4)], truncate).module_targets()
        self.assertFalse(result["complete"])
        self.assertFalse(result["ok"])
        self.assertIn("truncated", result["errors"][0])

    def test_total_change_between_pages_is_rejected(self):
        def change(reply, start, count):
            if start:
                reply["total"] += 1
        result = SyntheticProbe([target(2), target(4)], change).module_targets(page_size=1)
        self.assertFalse(result["complete"])
        self.assertEqual(result["captured"], 1)
        self.assertIn("changed", result["errors"][0])

    def test_final_metadata_change_is_rejected(self):
        def change(reply, start, count):
            if start == 1 and count == 0:
                reply["dropped"] = 1
        result = SyntheticProbe([target(2)], change).module_targets()
        self.assertFalse(result["complete"])
        self.assertIn("changed", result["errors"][0])

    def test_ledger_overflow_retains_rows_but_is_incomplete(self):
        def overflow(reply, start, count):
            reply["dropped"] = 12
        result = SyntheticProbe([target(2)], overflow).module_targets()
        self.assertTrue(result["ok"])
        self.assertFalse(result["complete"])
        self.assertEqual(result["captured"], 1)
        self.assertIn("overflowed", result["errors"][0])

    def test_duplicate_or_alias_records_are_rejected(self):
        for rows in ([target(2), target(2)],
                     [target(2), target(2, module=1)]):
            with self.subTest(rows=rows):
                result = SyntheticProbe(rows).module_targets()
                self.assertFalse(result["complete"])
                self.assertIn("duplicate or aliased", result["errors"][0])

    def test_module_index_cannot_change_identity(self):
        result = SyntheticProbe([target(2), target(4, digest="b" * 64)]).module_targets()
        self.assertFalse(result["complete"])
        self.assertIn("identity changed", result["errors"][0])

    def test_invalid_record_fields(self):
        cases = [("offset", 3), ("offset", True), ("base", 3),
                 ("sha256", "bad"), ("hits", 0), ("epoch", 0),
                 ("frame", -1), ("module", 0xFFFFFFFF)]
        for key, value in cases:
            row = target(2)
            row[key] = value
            with self.subTest(key=key, value=value):
                result = SyntheticProbe([row]).module_targets()
                self.assertFalse(result["complete"])
                self.assertTrue(result["errors"])

    def test_address_overflow_is_rejected(self):
        row = target(0xFFFFFFFE)
        result = SyntheticProbe([row]).module_targets()
        self.assertFalse(result["complete"])
        self.assertIn("overflowing", result["errors"][0])

    def test_runtime_movement_invalidates_capture(self):
        probe = SyntheticProbe([target(2)])
        probe.final = {"held": 1, "blocks": 1235}
        result = probe.module_targets()
        self.assertFalse(result["complete"])
        self.assertIn("runtime moved", result["errors"][0])

    def test_limits_are_finite_and_enforced_before_large_download(self):
        result = SyntheticProbe([target(2), target(4)]).module_targets(max_targets=1)
        self.assertFalse(result["complete"])
        self.assertEqual(result["pages"], 1)
        for options in ({"page_size": 0}, {"page_size": 257}, {"timeout": 61},
                        {"timeout": float("nan")}, {"max_targets": 262145}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                SyntheticProbe([]).module_targets(**options)

    def test_deadline_stops_collection(self):
        probe = SyntheticProbe([target(2)])
        with patch.object(mod.time, "monotonic", side_effect=[1.0, 2.0]):
            result = probe.module_targets(timeout=0.1)
        self.assertFalse(result["complete"])
        self.assertIn("deadline", result["errors"][0])

    def test_connection_failure_returns_partial_evidence(self):
        def fail(reply, start, count):
            if start == 1:
                raise OSError("synthetic disconnect")
        result = SyntheticProbe([target(2), target(4)], fail).module_targets(page_size=1)
        self.assertFalse(result["complete"])
        self.assertEqual(result["captured"], 1)
        self.assertIn("disconnect", result["errors"][0])

    def test_invalid_metadata_or_rejected_page(self):
        cases = [("total", True), ("dropped", -1), ("ok", False), ("targets", None)]
        for key, value in cases:
            def malformed(reply, start, count):
                reply[key] = value
            with self.subTest(key=key):
                result = SyntheticProbe([], malformed).module_targets()
                self.assertFalse(result["complete"])
                self.assertFalse(result["ok"])


class PauseTests(unittest.TestCase):
    def test_pause_requires_positive_acknowledgement(self):
        probe = mod.Probe(0, Path("/unused"), 1)
        probe.request = lambda *args, **kwargs: {"ok": False}
        with self.assertRaisesRegex(RuntimeError, "pause request rejected"):
            probe.pause_stable()

    def test_held_alone_is_not_stable_without_execution_counter(self):
        probe = mod.Probe(0, Path("/unused"), 1)
        probe.request = lambda cmd, **kwargs: {"ok": True} if cmd == "pause" else {"held": 1}
        with self.assertRaisesRegex(RuntimeError, "execution counter"):
            probe.pause_stable()

    def test_pause_requires_held_and_unchanged_execution_counter(self):
        probe = mod.Probe(0, Path("/unused"), 1)
        replies = iter([{"ok": True}, {"blocks": 12, "held": 0},
                        {"blocks": 13, "held": 1}, {"blocks": 13, "held": 1}])
        probe.request = lambda *args, **kwargs: next(replies)
        with patch.object(mod.time, "monotonic", side_effect=[0, .01, .02, .03, .04, .21, .22]), \
                patch.object(mod.time, "sleep"):
            state = probe.pause_stable()
        self.assertEqual(state, {"blocks": 13, "held": 1})


class CoverageTests(unittest.TestCase):
    def observation(self, native=100, interpreted=200, dropped=0):
        return {"interp_report": {"ok": True, "native": native,
                                  "total": interpreted, "dropped": dropped}}

    def test_healthy_measurement_preserves_counts_ratio_and_bios_scope(self):
        result = mod.coverage(self.observation())
        self.assertTrue(result["valid"])
        self.assertEqual(result["native_instructions"], 100)
        self.assertEqual(result["interpreted_instructions"], 200)
        self.assertAlmostEqual(result["native_percent"], 100 / 3)
        self.assertTrue(result["includes_bios"])
        self.assertEqual(result["dropped"], 0)

    def test_missing_or_failed_counter_read_is_not_measured_zero(self):
        for snapshot in (None, {}, {"interp_report": None},
                         {"interp_report": {"error": "synthetic TCP timeout"}},
                         {"interp_report": {"ok": False}},
                         {"interp_report": {"native": 100, "total": 200, "dropped": 0}}):
            with self.subTest(snapshot=snapshot):
                result = mod.coverage(snapshot)
                self.assertFalse(result["valid"])
                self.assertIsNone(result["native_instructions"])
                self.assertIsNone(result["interpreted_instructions"])
                self.assertIsNone(result["native_percent"])
                self.assertTrue(result["error"])

    def test_malformed_or_missing_numeric_counter_invalidates_measurement(self):
        for field in ("native", "total", "dropped"):
            for value in (None, -1, True, "100", 1.5, 1 << 64):
                snapshot = self.observation()
                snapshot["interp_report"][field] = value
                with self.subTest(field=field, value=value):
                    result = mod.coverage(snapshot)
                    self.assertFalse(result["valid"])
                    self.assertIsNone(result["native_percent"])
                    self.assertIn(field, result["error"])
            snapshot = self.observation()
            del snapshot["interp_report"][field]
            self.assertFalse(mod.coverage(snapshot)["valid"])

    def test_real_zero_observation_is_valid_without_a_ratio(self):
        result = mod.coverage(self.observation(0, 0))
        self.assertTrue(result["valid"])
        self.assertEqual(result["native_instructions"], 0)
        self.assertEqual(result["interpreted_instructions"], 0)
        self.assertIsNone(result["native_percent"])

    def test_target_histogram_overflow_remains_visible_with_aggregate_counts(self):
        result = mod.coverage(self.observation(dropped=5))
        self.assertTrue(result["valid"])
        self.assertEqual(result["dropped"], 5)
        self.assertAlmostEqual(result["native_percent"], 100 / 3)

    def test_interval_uses_deltas_instead_of_lifetime_ratio(self):
        before = mod.coverage(self.observation(100, 200))
        after = mod.coverage(self.observation(130, 210))
        interval = mod.coverage_interval(before, after)
        self.assertTrue(interval["valid"])
        self.assertEqual(interval["native_instructions"], 30)
        self.assertEqual(interval["interpreted_instructions"], 10)
        self.assertEqual(interval["native_percent"], 75)
        self.assertTrue(interval["includes_bios"])

    def test_reset_of_either_counter_invalidates_interval(self):
        before = mod.coverage(self.observation())
        for after in (mod.coverage(self.observation(99, 210)),
                      mod.coverage(self.observation(110, 199))):
            interval = mod.coverage_interval(before, after)
            self.assertFalse(interval["valid"])
            self.assertIsNone(interval["native_instructions"])
            self.assertIsNone(interval["interpreted_instructions"])
            self.assertIsNone(interval["native_percent"])
            self.assertIn("reset", interval["error"])

    def test_missing_endpoint_never_produces_a_percentage(self):
        healthy = mod.coverage(self.observation())
        for invalid in (None, {}, mod.coverage({}),
                        {"valid": True, "native_instructions": 4,
                         "interpreted_instructions": True}):
            for before, after in ((invalid, healthy), (healthy, invalid)):
                interval = mod.coverage_interval(before, after)
                self.assertFalse(interval["valid"])
                self.assertIsNone(interval["native_percent"])
                self.assertTrue(interval["error"])

    def test_zero_execution_interval_is_valid_without_a_ratio(self):
        endpoint = mod.coverage(self.observation())
        interval = mod.coverage_interval(endpoint, endpoint)
        self.assertTrue(interval["valid"])
        self.assertEqual(interval["native_instructions"], 0)
        self.assertEqual(interval["interpreted_instructions"], 0)
        self.assertIsNone(interval["native_percent"])
