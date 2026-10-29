"""Progress counts and GitHub issue refresh use public, synthetic data only."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from update_backlog import (START, END, issue_status, replace_summary,
                            render_backlog, stats, summary, sync_issues, validate)


def fixture():
    return {"schema_version": 1, "repository": "sample/project",
            "project_url": "https://github.com/users/sample/projects/1/views/2",
            "snapshot_date": "2026-10-29", "items": [
                {"id": "ZCDI-001", "issue_number": 1, "title": "Synthetic delivery",
                 "status": "done", "area": "runtime", "priority": "P1",
                 "acceptance": "Synthetic acceptance criterion.", "evidence": "docs/example.md"},
                {"id": "ZCDI-002", "issue_number": 2, "title": "Synthetic pending work",
                 "status": "validation", "area": "interface", "priority": "P2",
                 "acceptance": "Confirm behavior on a real target.", "evidence": "app/example.c"}]}


class BacklogTests(unittest.TestCase):
    def test_counts_deliveries_without_inventing_partial_progress(self):
        total, counts, percent = stats(fixture()["items"])
        self.assertEqual((total, counts["done"], percent), (2, 1, 50))
        self.assertEqual(stats([])[2], 0)

    def test_cancelled_issue_is_not_a_completed_delivery(self):
        self.assertEqual(issue_status({"state": "closed", "state_reason": "not_planned"}), "backlog")
        self.assertEqual(issue_status({"state": "closed", "state_reason": "completed"}), "done")

    def test_reopened_delivery_returns_to_validation(self):
        self.assertEqual(issue_status({"state": "open", "labels": [{"name": "status:concluido"}]}), "validation")

    def test_conflicting_status_labels_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Conflicting"):
            issue_status({"state": "open", "labels": [{"name": "status:backlog"}, {"name": "status:a-validar"}]})

    def test_sync_does_not_expand_scope_or_import_remote_titles(self):
        data = fixture()
        issues = [{"number": 1, "state": "closed"}, {"number": 2, "state": "closed", "title": "Untrusted replacement"},
                  {"number": 3, "state": "closed"}, {"number": 99, "state": "closed", "pull_request": {}}]
        self.assertEqual(sync_issues(data, issues), 1)
        self.assertEqual(len(data["items"]), 2)
        self.assertEqual(data["items"][1]["title"], "Synthetic pending work")
        self.assertEqual(stats(data["items"])[2], 100)

    def test_missing_issue_refuses_partial_updates(self):
        data = fixture(); before = deepcopy(data)
        with self.assertRaisesRegex(ValueError, "missing"):
            sync_issues(data, [{"number": 1, "state": "open"}])
        self.assertEqual(data, before)

    def test_summary_replacement_preserves_handwritten_readme(self):
        original = "Before\n" + START + "\nold\n" + END + "\nAfter"
        self.assertEqual(replace_summary(original, "new\n"), "Before\n" + START + "\nnew\n" + END + "\nAfter")
        for broken in (START, END + START, START + START + END):
            with self.assertRaises(ValueError): replace_summary(broken, "new")

    def test_private_evidence_and_duplicate_issue_numbers_are_rejected(self):
        for path in ("data/private/report.json", "build/generated.c", "../docs/a.md", ""):
            data = fixture(); data["items"][0]["evidence"] = path
            with self.assertRaises(ValueError): validate(data)
        data = fixture(); data["items"][1]["issue_number"] = 1
        with self.assertRaises(ValueError): validate(data)

    def test_rendering_is_stable_and_links_use_the_right_directory(self):
        data = validate(fixture())
        self.assertEqual(render_backlog(data), render_backlog(data))
        self.assertIn("(BACKLOG.md)", render_backlog(data))
        self.assertIn("(docs/BACKLOG.md)", summary(data, english=True))
        self.assertIn("1 / 2", render_backlog(data))


if __name__ == "__main__":
    unittest.main()
