"""Resolve copied Mach-O dependencies without assuming @rpath means bundled."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from build_macos_app import library_source


class MacDependencyTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve()
        self.binary=self.root/"App/Contents/MacOS/player"
        self.binary.parent.mkdir(parents=True);self.binary.write_bytes(b"synthetic executable")

    def test_rpath_library_is_found_in_sdk_and_must_be_copied(self):
        sdk=self.root/"private-sdk";sdk.mkdir();library=sdk/"libTest.dylib";library.write_bytes(b"synthetic library")
        with patch("build_macos_app.rpaths",return_value=[str(sdk)]):
            self.assertEqual(library_source("@rpath/libTest.dylib",self.binary,self.binary.parent),library)

    def test_loader_and_executable_relative_paths_resolve_to_real_files(self):
        library=self.binary.parent/"libTest.dylib";library.write_bytes(b"synthetic")
        for value in ("@loader_path/libTest.dylib","@executable_path/libTest.dylib"):
            self.assertEqual(library_source(value,self.binary,self.binary.parent),library)

    def test_unresolved_rpath_is_an_error_instead_of_a_silent_unbundled_library(self):
        with patch("build_macos_app.rpaths",return_value=[]):
            with self.assertRaisesRegex(RuntimeError,"Missing dynamic library"):
                library_source("@rpath/missing.dylib",self.binary,self.binary.parent)
