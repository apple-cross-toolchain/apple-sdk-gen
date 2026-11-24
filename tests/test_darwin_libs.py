import json
import tempfile
import unittest
from pathlib import Path

import yaml

from tools.apple_sdk_gen.supplements.darwin_libs import (
    LIBRARIES,
    install_darwin_lib_stubs,
    select_darwin_libraries,
)


class DarwinLibrariesTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.metadata = self.root / "darwin.json"

    def write_metadata(self, version):
        targets = ["arm64-macos", "x86_64-macos"]
        child = "/usr/lib/system/libsystem_test.dylib"
        libraries = {
            name: [{"install-name": install_name, "targets": targets}]
            for name, install_name in LIBRARIES.items()
        }
        libraries["libSystem.B"][0]["reexported-libraries"] = [
            {"targets": ["x86_64-macos"], "libraries": [child]}
        ]
        exports = [{"targets": ["x86_64-macos"], "symbols": ["_intel_only"]}]
        if version == "27.0":
            exports.append({"targets": ["arm64-macos"], "symbols": ["_new_api"]})
        libraries["libSystem.B"].append({
            "install-name": child,
            "targets": targets,
            "exports": exports,
            "reexports": [{"targets": ["x86_64-macos"], "symbols": ["_forwarded"]}],
        })
        self.metadata.write_text(json.dumps({"sdk_version": version, "platforms": {"macos": libraries}}))

    def test_selects_only_the_requested_version_and_platform(self):
        self.write_metadata("27.0")
        with self.assertRaisesRegex(ValueError, "describes SDK '27.0', requested 26.5"):
            select_darwin_libraries("26.5", ["macos"], self.metadata)
        with self.assertRaisesRegex(ValueError, "requires --darwin-library-metadata"):
            select_darwin_libraries("26.5", ["macos"], None)
        with self.assertRaisesRegex(ValueError, "missing ios libraries"):
            select_darwin_libraries("27.0", ["macos", "ios"], self.metadata)
        self.assertIn("libSystem.B", select_darwin_libraries("27.0", ["macos"], None)["macos"])

    def test_preserves_document_and_symbol_targets(self):
        self.write_metadata("26.5")
        libraries = select_darwin_libraries("26.5", ["macos"], self.metadata)["macos"]
        install_darwin_lib_stubs(self.root, libraries)
        lib = self.root / "usr/lib"
        self.assertEqual((lib / "libSystem.tbd").readlink(), Path("libSystem.B.tbd"))
        tbd = (lib / "libSystem.B.tbd").read_text().replace("--- !tapi-tbd", "---")
        root, child = list(yaml.safe_load_all(tbd))
        self.assertEqual(
            root["reexported-libraries"],
            [{"targets": ["x86_64-macos"], "libraries": [child["install-name"]]}],
        )
        self.assertEqual(child["exports"], [{"targets": ["x86_64-macos"], "symbols": ["_intel_only"]}])
        self.assertEqual(child["reexports"], [{"targets": ["x86_64-macos"], "symbols": ["_forwarded"]}])

        self.write_metadata("27.0")
        newer = select_darwin_libraries("27.0", ["macos"], self.metadata)
        self.assertIn("_new_api", newer["macos"]["libSystem.B"])
