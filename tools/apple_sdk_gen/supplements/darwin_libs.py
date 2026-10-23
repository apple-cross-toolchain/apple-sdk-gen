from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from ..generators.tbd import EXPORT_KEYS, tbd_document

logger = logging.getLogger(__name__)

DATA_PATH = Path(__file__).parent / "data" / "darwin_libs.json"

LIBRARIES = {
    "libSystem.B": "/usr/lib/libSystem.B.dylib",
    "libobjc.A": "/usr/lib/libobjc.A.dylib",
    "libc++.1": "/usr/lib/libc++.1.dylib",
    "libc++abi": "/usr/lib/libc++abi.dylib",
}

LINKS = {
    "libSystem": "libSystem.B",
    "libc": "libSystem.B",
    "libobjc": "libobjc.A",
    "libc++": "libc++.1",
}


def _document(targets: list[str], install_name: str, record: dict, data: dict) -> str:
    return tbd_document(
        targets,
        install_name,
        exports=[(targets, {key: record.get(key, []) for key in EXPORT_KEYS})],
        current_version=record.get("current-version"),
        compatibility_version=record.get("compatibility-version"),
        reexports=[name for name in record.get("reexported-libraries", []) if name in data],
        flags=record.get("flags", []),
    )


def install_darwin_lib_stubs(sdk_root: Path, tbd_targets: list[str]) -> None:
    data = json.loads(DATA_PATH.read_text())
    usr_lib = sdk_root / "usr" / "lib"
    usr_lib.mkdir(parents=True, exist_ok=True)
    for name, install_name in LIBRARIES.items():
        documents = []
        pending = [install_name]
        seen: set[str] = set()
        while pending:
            current = pending.pop(0)
            if current in seen or current not in data:
                continue
            seen.add(current)
            record = data[current]
            documents.append(_document(tbd_targets, current, record, data))
            pending.extend(record.get("reexported-libraries", []))
        (usr_lib / f"{name}.tbd").write_text("".join(documents))
    for link, target in LINKS.items():
        path = usr_lib / f"{link}.tbd"
        if path.exists() or path.is_symlink():
            path.unlink()
        os.symlink(f"{target}.tbd", path)
    logger.info("Installed %d Darwin library stubs from %s", len(LIBRARIES), DATA_PATH.name)
