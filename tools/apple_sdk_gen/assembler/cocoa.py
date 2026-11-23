from __future__ import annotations

from pathlib import Path

from ..generators.modulemap import generate_modulemap
from ..generators.tbd import tbd_document


# Apple documents the umbrella's imports separately from the DocC catalog.
# https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/OSX_Technology_Overview/CocoaApplicationLayer/CocoaApplicationLayer.html
COCOA_IMPORTS = ("Foundation", "AppKit", "CoreData")


def assemble_cocoa(frameworks_dir: Path, targets: list[str]) -> None:
    cocoa = frameworks_dir / "Cocoa.framework"
    headers = cocoa / "Headers"
    modules = cocoa / "Modules"
    headers.mkdir(parents=True, exist_ok=True)
    modules.mkdir(parents=True, exist_ok=True)
    (headers / "Cocoa.h").write_text("".join(f"#import <{name}/{name}.h>\n" for name in COCOA_IMPORTS))
    (modules / "module.modulemap").write_text(generate_modulemap("Cocoa"))

    # Verified the install name, version, exports, and direct reexports
    # in the Cocoa image loaded by macOS 26.5.2 on arm64 and x86_64.
    # Use the generated children's flat install names for linker lookup.
    (cocoa / "Cocoa.tbd").write_text(tbd_document(
        targets,
        "/System/Library/Frameworks/Cocoa.framework/Versions/A/Cocoa",
        current_version="24",
        reexports=[f"/System/Library/Frameworks/{name}.framework/{name}" for name in ("AppKit", "CoreData")],
        exports=[(targets, {"symbols": ["_CocoaVersionNumber", "_CocoaVersionString"]})],
    ))
