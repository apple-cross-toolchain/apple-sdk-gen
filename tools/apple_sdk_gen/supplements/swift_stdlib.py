"""Copy Swift stdlib .swiftinterface files from a reference SDK.

The Swift compiler needs the standard-library ``.swiftinterface`` files
(e.g. ``Swift.swiftmodule/``, ``_Concurrency.swiftmodule/``) under
``<SDK>/usr/lib/swift/`` to compile for Apple targets.  These are
Apple-proprietary artefacts that cannot be generated from public
documentation, so we copy them from an existing reference SDK tree.
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from ..config import PLATFORM_CONFIGS

logger = logging.getLogger(__name__)


def install_swift_stdlib(
    sdk_root: Path,
    platform_key: str,
    reference_root: Path,
) -> None:
    """Copy ``usr/lib/swift/*.swiftmodule/`` from *reference_root* into *sdk_root*.

    *reference_root* should point to the top-level ``Xcode.app/`` (or
    equivalent) tree that contains the full Apple SDK.  The function
    resolves the correct platform SDK under it and copies all
    ``.swiftmodule`` directories that contain ``.swiftinterface`` files.
    """
    cfg = PLATFORM_CONFIGS.get(platform_key)
    if cfg is None:
        logger.warning("Unknown platform %s, skipping Swift stdlib", platform_key)
        return

    # Locate the reference SDK for this platform
    ref_sdk = (
        reference_root / "Xcode.app" / "Contents" / "Developer" / "Platforms"
        / cfg.platform_dir / "Developer" / "SDKs" / f"{cfg.sdk_prefix}.sdk"
    )
    if not ref_sdk.is_dir():
        # Try without the Xcode.app prefix (flat layout)
        ref_sdk = (
            reference_root / "Contents" / "Developer" / "Platforms"
            / cfg.platform_dir / "Developer" / "SDKs" / f"{cfg.sdk_prefix}.sdk"
        )
    if not ref_sdk.is_dir():
        logger.warning("Reference SDK not found at %s", ref_sdk)
        return

    ref_swift_dir = ref_sdk / "usr" / "lib" / "swift"
    if not ref_swift_dir.is_dir():
        logger.warning("No usr/lib/swift/ in reference SDK %s", ref_sdk)
        return

    dst_swift_dir = sdk_root / "usr" / "lib" / "swift"
    dst_swift_dir.mkdir(parents=True, exist_ok=True)

    copied = 0
    for entry in sorted(ref_swift_dir.iterdir()):
        if entry.is_dir() and entry.suffix == ".swiftmodule":
            dst = dst_swift_dir / entry.name
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(entry, dst)
            copied += 1

    # Also copy auxiliary files (layouts-*.yaml, libcxxshim.*, etc.)
    for entry in sorted(ref_swift_dir.iterdir()):
        if entry.is_file() and not entry.name.endswith(".tbd"):
            dst = dst_swift_dir / entry.name
            if not dst.exists():
                shutil.copy2(entry, dst)

    logger.info(
        "Copied %d Swift stdlib .swiftmodule dirs from %s", copied, ref_sdk,
    )
