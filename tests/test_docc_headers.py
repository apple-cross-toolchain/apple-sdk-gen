import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from tools.apple_sdk_gen.assembler.sdk_layout import assemble_sdk
from tools.apple_sdk_gen.crawler.symbol import parse_symbol


CLANG = os.environ.get("CLANG") or shutil.which("clang")


def declaration(text, *platforms):
    return {"languages": ["occ"], "platforms": platforms,
            "tokens": [{"kind": "text", "text": text}]}


def page(title, kind, *declarations):
    return {
        "metadata": {"title": title, "role": "symbol", "symbolKind": kind},
        "primaryContentSections": [{"kind": "declarations", "declarations": declarations}],
    }


class DocC:
    def __init__(self, pages):
        self.pages = pages

    async def fetch_doc(self, path):
        return self.pages[path]

    async def symbols(self):
        return [await parse_symbol(self, path, "Foundation") for path in self.pages]


def assemble_header(directory, platform, symbols):
    sdk = assemble_sdk(directory, platform, "26.0", {"Foundation": symbols})
    return sdk / "System/Library/Frameworks/Foundation.framework/Headers/Foundation.h"


def address_pages(initializer):
    address = "/documentation/foundation/address"
    field_refs = {"number": {"title": "number", "url": f"{address}/number"},
                  "code": {"title": "code", "url": f"{address}/code"},
                  "initializer": {"title": initializer, "url": f"{address}/initializer"}}
    return {
        address: {
            **page("Address", "struct", declaration("typedef struct Address { ... } Address;")),
            "topicSections": [{"identifiers": ["number", "code", "initializer"]}],
            "references": {
                name: {"kind": "symbol", "role": "symbol", **ref}
                for name, ref in field_refs.items()
            },
        },
        f"{address}/number": page("number", "property", declaration("unsigned number;")),
        f"{address}/code": page("code", "property", declaration("unsigned char code;")),
    }


class DocCHeadersTest(unittest.IsolatedAsyncioTestCase):
    async def test_separates_return_type_from_function_name(self):
        # DocC's CFRetain declaration has no whitespace token before CFRetain.
        retain_declaration = {
            "languages": ["occ"],
            "tokens": [
                {"kind": "keyword", "text": "extern"},
                {"kind": "text", "text": " "},
                {"kind": "typeIdentifier", "text": "CFTypeRef"},
                {"kind": "identifier", "text": "CFRetain"},
                {"kind": "text", "text": "("},
                {"kind": "typeIdentifier", "text": "CFTypeRef"},
                {"kind": "text", "text": " "},
                {"kind": "internalParam", "text": "cf"},
                {"kind": "text", "text": ");"},
            ],
        }
        docc = DocC({
            "/documentation/corefoundation/cfretain": page("CFRetain", "func", retain_declaration),
        })
        with tempfile.TemporaryDirectory() as directory:
            header = assemble_header(Path(directory), "macos", await docc.symbols()).read_text()
        self.assertIn("extern CFTypeRef CFRetain(CFTypeRef cf);", header)

    async def test_uses_platform_variant_before_unqualified_declaration(self):
        docc = DocC({
            "/documentation/foundation/handle": page(
                "Handle", "typealias",
                declaration("typedef struct Generic *Handle;"),
                declaration("typedef struct Mobile *Handle;", "iOS"),
                declaration("typedef struct Desktop *Handle;", "macOS"),
            ),
        })
        symbols = await docc.symbols()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            macos = assemble_header(root, "macos", symbols).read_text()
            ios = assemble_header(root, "ios", symbols).read_text()
            watchos = assemble_header(root, "watchos", symbols).read_text()
        self.assertIn("typedef struct Desktop *Handle;", macos)
        self.assertIn("typedef struct Mobile *Handle;", ios)
        self.assertIn("typedef struct Generic *Handle;", watchos)

    @unittest.skipUnless(CLANG, "requires Clang")
    async def test_struct_offsets_follow_memberwise_initializer(self):
        docc = DocC(address_pages("init(code:number:)"))
        with tempfile.TemporaryDirectory() as directory:
            header = assemble_header(Path(directory), "macos", await docc.symbols())
            for arch in ("arm64", "x86_64"):
                with self.subTest(arch=arch):
                    result = subprocess.run(
                        [CLANG, "-target", f"{arch}-apple-macos11", "-ffreestanding",
                         "-std=c11", "-fsyntax-only", "-Werror", "-include", str(header),
                         "-x", "c", "-"],
                        input=(
                            '_Static_assert(__builtin_offsetof(Address, code) == 0, "code");\n'
                            '_Static_assert(__builtin_offsetof(Address, number) == 4, "number");\n'
                        ),
                        text=True, capture_output=True,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)

    async def test_incomplete_initializer_leaves_struct_opaque(self):
        docc = DocC(address_pages("init(code:)"))
        with tempfile.TemporaryDirectory() as directory:
            header = assemble_header(Path(directory), "macos", await docc.symbols()).read_text()
        self.assertIn("typedef struct Address Address;", header)
        self.assertNotIn("struct Address {", header)
