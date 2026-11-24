import unittest

from tools.apple_sdk_gen.generators.tbd import generate_tbd
from tools.apple_sdk_gen.models.symbol import Symbol
from tools.apple_sdk_gen.models.types import SymbolKind


class FrameworkTBDTest(unittest.TestCase):
    def test_exports_data_constants_but_not_enum_cases(self):
        symbols = [
            Symbol("tag-class", "kUTTagClassMIMEType", SymbolKind.VAR, usr="c:@kUTTagClassMIMEType"),
            Symbol("launch-defaults", "kLSLaunchDefaults", SymbolKind.ENUM_CASE,
                   usr="c:@E@LSLaunchFlags@kLSLaunchDefaults"),
        ]
        stub = generate_tbd("CoreServices", symbols, ["arm64-macos", "x86_64-macos"])

        self.assertIn("_kUTTagClassMIMEType", stub)
        self.assertNotIn("_kLSLaunchDefaults", stub)
