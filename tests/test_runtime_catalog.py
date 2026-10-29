"""Private candidate identity selection without real runtimes or game media."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_macos_app import load_runtime_catalog


class RuntimeCatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.entries = {}
        for game in ("faces", "gamelon", "adventure"):
            path = self.root / "build" / game
            path.parent.mkdir(exist_ok=True)
            path.write_bytes(("synthetic runtime " + game).encode())
            self.entries[game] = {"path": "build/" + game,
                                  "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        self.catalog = self.root / "catalog.json"

    def load(self):
        self.catalog.write_text(json.dumps({"schema_version": 1, "runtimes": self.entries}))
        return load_runtime_catalog(self.catalog, self.root)

    def test_explicit_selection_returns_resolved_verified_candidates(self):
        chosen = self.load()
        self.assertEqual(chosen["adventure"]["path"], (self.root / "build/adventure").resolve())
        self.assertEqual(chosen["faces"]["sha256"], self.entries["faces"]["sha256"])

    def test_missing_title_cannot_silently_fall_back_to_an_old_build(self):
        del self.entries["gamelon"]
        with self.assertRaisesRegex(ValueError, "exactly"):
            self.load()

    def test_changed_candidate_is_rejected(self):
        (self.root / "build/adventure").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "identity changed"):
            self.load()

    def test_traversal_or_symlink_cannot_escape_private_roots(self):
        outside = self.root / "public-binary"
        outside.write_bytes(b"synthetic")
        link = self.root / "build/link"
        link.symlink_to(outside)
        for value in ("build/../public-binary", "build/link"):
            self.entries["faces"]["path"] = value
            with self.assertRaisesRegex(ValueError, "private directories"):
                self.load()

    def test_unknown_title_and_malformed_digest_are_rejected(self):
        self.entries["faces"]["sha256"] = "abc"
        with self.assertRaisesRegex(ValueError, "complete SHA"):
            self.load()
        self.entries["unknown"] = self.entries["faces"]
        with self.assertRaisesRegex(ValueError, "exactly"):
            self.load()

    def test_status_cannot_inject_extra_lines_into_the_manifest_label(self):
        self.entries["adventure"]["status_text"] = "test\naccepted"
        with self.assertRaisesRegex(ValueError, "status text"):
            self.load()


if __name__ == "__main__":
    unittest.main()
