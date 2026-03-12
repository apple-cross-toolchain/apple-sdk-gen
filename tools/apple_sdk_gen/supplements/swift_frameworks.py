"""Copy framework .swiftmodule directories from a reference SDK.

The Swift compiler needs real ``.swiftinterface`` files for each framework
(e.g. ``SwiftUI.swiftmodule/``, ``Foundation.swiftmodule/``) under each
framework's ``Modules/`` directory.  These are Apple-proprietary artefacts
that cannot be reliably generated from public documentation, so we copy
them from an existing reference SDK tree, overwriting any synthetic stubs
that apple-sdk-gen may have produced.
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from ..config import PLATFORM_CONFIGS

logger = logging.getLogger(__name__)


def install_framework_swiftmodules(
    sdk_root: Path,
    platform_key: str,
    reference_root: Path,
) -> None:
    """Copy ``*.swiftmodule/`` dirs from reference frameworks into *sdk_root*.

    For each framework in the reference SDK that contains a
    ``Modules/<Name>.swiftmodule/`` directory, copy it into the
    corresponding framework in *sdk_root*, replacing any synthetic
    ``.swiftinterface`` files.
    """
    cfg = PLATFORM_CONFIGS.get(platform_key)
    if cfg is None:
        logger.warning("Unknown platform %s, skipping framework swiftmodules", platform_key)
        return

    # Locate the reference SDK for this platform
    ref_sdk = (
        reference_root / "Xcode.app" / "Contents" / "Developer" / "Platforms"
        / cfg.platform_dir / "Developer" / "SDKs" / f"{cfg.sdk_prefix}.sdk"
    )
    if not ref_sdk.is_dir():
        ref_sdk = (
            reference_root / "Contents" / "Developer" / "Platforms"
            / cfg.platform_dir / "Developer" / "SDKs" / f"{cfg.sdk_prefix}.sdk"
        )
    if not ref_sdk.is_dir():
        logger.warning("Reference SDK not found at %s", ref_sdk)
        return

    ref_frameworks = ref_sdk / "System" / "Library" / "Frameworks"
    if not ref_frameworks.is_dir():
        logger.warning("No System/Library/Frameworks/ in reference SDK %s", ref_sdk)
        return

    dst_frameworks = sdk_root / "System" / "Library" / "Frameworks"
    copied = 0

    for fw_dir in sorted(ref_frameworks.iterdir()):
        if not fw_dir.is_dir() or not fw_dir.name.endswith(".framework"):
            continue

        modules_dir = fw_dir / "Modules"
        if not modules_dir.is_dir():
            continue

        for entry in modules_dir.iterdir():
            if not entry.is_dir() or not entry.name.endswith(".swiftmodule"):
                continue

            # Only copy if the destination framework exists (was generated)
            dst_fw = dst_frameworks / fw_dir.name / "Modules" / entry.name
            dst_fw.parent.mkdir(parents=True, exist_ok=True)

            if dst_fw.exists():
                shutil.rmtree(dst_fw)
            shutil.copytree(entry, dst_fw)
            copied += 1

    # Remove synthetic .swiftmodule dirs from frameworks that are C/ObjC-only
    # in the reference SDK (their real Swift overlay lives in usr/lib/swift/).
    # The synthetic stubs shadow the real overlays and cause build failures.
    removed = 0
    if dst_frameworks.is_dir():
        for fw_dir in sorted(dst_frameworks.iterdir()):
            if not fw_dir.is_dir() or not fw_dir.name.endswith(".framework"):
                continue
            modules_dir = fw_dir / "Modules"
            if not modules_dir.is_dir():
                continue
            for entry in sorted(modules_dir.iterdir()):
                if not entry.is_dir() or not entry.name.endswith(".swiftmodule"):
                    continue
                # Check if the reference SDK has this .swiftmodule in the framework
                ref_entry = ref_frameworks / fw_dir.name / "Modules" / entry.name
                if not ref_entry.is_dir():
                    shutil.rmtree(entry)
                    removed += 1

    logger.info(
        "Copied %d framework .swiftmodule dirs, removed %d synthetic stubs from %s",
        copied, removed, ref_sdk,
    )
