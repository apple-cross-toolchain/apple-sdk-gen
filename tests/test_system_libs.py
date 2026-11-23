from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tools.apple_sdk_gen.supplements.system_libs import install_system_lib_stubs


class SystemLibraryStubsTest(unittest.TestCase):
    def test_exports_on_adjacent_source_lines_are_written_separately(self):
        expected_exports = {
            "libresolv.9": {"_res_9_nametotype", "_res_9_nclose", "_res_9_nsearch"},
            "libz.1": {"_deflateParams", "_deflatePending", "_zlibCompileFlags", "_zlibVersion"},
        }
        with TemporaryDirectory() as directory:
            sdk = Path(directory)
            install_system_lib_stubs(sdk, ["arm64-macos", "x86_64-macos"])

            for library, expected in expected_exports.items():
                with self.subTest(library=library):
                    stub = sdk / "usr" / "lib" / f"{library}.tbd"
                    exports = {
                        line.strip()[2:]
                        for line in stub.read_text().splitlines()
                        if line.startswith("      - ")
                    }
                    self.assertLessEqual(expected, exports)


if __name__ == "__main__":
    unittest.main()
