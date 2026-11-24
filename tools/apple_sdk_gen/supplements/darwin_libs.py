from __future__ import annotations

import json
import os
from pathlib import Path

from ..config import tbd_targets_for_platform
from ..generators.tbd import EXPORT_KEYS, tbd_document

DATA_PATH = Path(__file__).parent / "data" / "darwin_libs.json"
BUNDLED_SDK_VERSION = "27.0"

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


def _bundled_libraries(data: dict, tbd_targets: list[str]) -> dict[str, str]:
    libraries = {}
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
        libraries[name] = "".join(documents)
    return libraries


def _symbol_groups(document: dict, section: str) -> list[tuple[list[str], dict[str, list[str]]]]:
    return [(group["targets"], group) for group in document.get(section, [])]


def _render_document(document: dict) -> str:
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
        swift_abi_version=document.get("swift-abi-version", 0),
    )


def select_darwin_libraries(
    sdk_version: str, platforms: list[str], metadata_path: Path | None,
) -> dict[str, dict[str, str]]:
    if metadata_path is None:
        if sdk_version != BUNDLED_SDK_VERSION:
            raise ValueError(
                f"SDK {sdk_version} requires --darwin-library-metadata "
                f"(bundled inventory covers SDK {BUNDLED_SDK_VERSION})"
            )
        data = json.loads(DATA_PATH.read_text())
        return {
            platform: _bundled_libraries(data, tbd_targets_for_platform(platform, sdk_version))
            for platform in platforms
        }

    data = json.loads(metadata_path.read_text())
    if not isinstance(data, dict):
        raise ValueError(f"{metadata_path} must contain a Darwin inventory object")
    actual_version = data.get("sdk_version")
    if actual_version != sdk_version:
        raise ValueError(f"{metadata_path} describes SDK {actual_version!r}, requested {sdk_version}")

    selected = {}
    for platform in platforms:
        libraries = data.get("platforms", {}).get(platform, {})
        missing = [name for name in LIBRARIES if not libraries.get(name)]
        if missing:
            raise ValueError(f"{metadata_path} is missing {platform} libraries: {', '.join(missing)}")
        try:
            selected[platform] = {
                name: "".join(map(_render_document, libraries[name])) for name in LIBRARIES
            }
        except (KeyError, TypeError) as exc:
            raise ValueError(f"{metadata_path} contains invalid TBD documents for {platform}: {exc}") from exc
    return selected


def install_darwin_lib_stubs(sdk_root: Path, libraries: dict[str, str]) -> None:
    usr_lib = sdk_root / "usr" / "lib"
    usr_lib.mkdir(parents=True, exist_ok=True)
    for name, documents in libraries.items():
        (usr_lib / f"{name}.tbd").write_text(documents)
    for link, target in LINKS.items():
        path = usr_lib / f"{link}.tbd"
        if path.exists() or path.is_symlink():
            path.unlink()
        os.symlink(f"{target}.tbd", path)
