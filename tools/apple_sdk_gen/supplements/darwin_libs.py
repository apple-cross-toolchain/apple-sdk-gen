from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from ..generators.tbd import tbd_document

logger = logging.getLogger(__name__)

DATA_PATH = Path(__file__).parent / "data" / "darwin_libs.json"

LIBRARIES = ("libSystem.B", "libobjc.A", "libc++.1", "libc++abi")

LINKS = {
    "libSystem": "libSystem.B",
    "libc": "libSystem.B",
    "libobjc": "libobjc.A",
    "libc++": "libc++.1",
}


def _symbol_groups(document: dict, section: str):
    return [
        (group["targets"], {key: values for key, values in group.items() if key != "targets"})
        for group in document.get(section, [])
    ]


def _document(document: dict) -> str:
    return tbd_document(
        document["targets"],
        document["install-name"],
        exports=_symbol_groups(document, "exports"),
        reexported_symbols=_symbol_groups(document, "reexports"),
        current_version=document.get("current-version"),
        compatibility_version=document.get("compatibility-version"),
        reexported_libraries=[
            (group["targets"], group["libraries"])
            for group in document.get("reexported-libraries", [])
        ],
        flags=document.get("flags", []),
    )


def install_darwin_lib_stubs(sdk_root: Path, platform_key: str) -> None:
    data = json.loads(DATA_PATH.read_text()).get(platform_key, {})
    missing = [name for name in LIBRARIES if not data.get(name)]
    if missing:
        raise ValueError(f"Darwin library metadata for {platform_key} is missing {', '.join(missing)}")

    usr_lib = sdk_root / "usr" / "lib"
    usr_lib.mkdir(parents=True, exist_ok=True)
    for name in LIBRARIES:
        (usr_lib / f"{name}.tbd").write_text("".join(map(_document, data[name])))
    for link, target in LINKS.items():
        path = usr_lib / f"{link}.tbd"
        if path.exists() or path.is_symlink():
            path.unlink()
        os.symlink(f"{target}.tbd", path)
    logger.info("Installed %d Darwin library stubs from %s", len(LIBRARIES), DATA_PATH.name)
