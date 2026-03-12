"""Copy usr/lib/*.tbd from a reference SDK.

The reference SDK contains authoritative TBD stubs for system libraries
(libSystem.B, libc, libobjc, libdispatch, etc.) with complete symbol lists
and properly structured re-exports.  This supplement copies them over the
generated stubs, which may be incomplete or incorrectly structured.
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from ..config import PLATFORM_CONFIGS

logger = logging.getLogger(__name__)


def install_reference_libs(
    sdk_root: Path,
    platform_key: str,
    reference_root: Path,
) -> None:
    """Copy ``usr/lib/*.tbd`` and ``usr/lib/system/`` from the reference SDK."""
    cfg = PLATFORM_CONFIGS.get(platform_key)
    if cfg is None:
        logger.warning("Unknown platform %s, skipping reference libs", platform_key)
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

    ref_lib = ref_sdk / "usr" / "lib"
    if not ref_lib.is_dir():
        logger.warning("No usr/lib/ in reference SDK %s", ref_sdk)
        return

    dst_lib = sdk_root / "usr" / "lib"
    dst_lib.mkdir(parents=True, exist_ok=True)

    # Copy all .tbd files from usr/lib/
    copied = 0
    for tbd in sorted(ref_lib.glob("*.tbd")):
        shutil.copy2(tbd, dst_lib / tbd.name)
        copied += 1

    # Copy usr/lib/system/ directory (sub-library TBDs)
    ref_system = ref_lib / "system"
    if ref_system.is_dir():
        dst_system = dst_lib / "system"
        if dst_system.exists():
            shutil.rmtree(dst_system)
        shutil.copytree(ref_system, dst_system, symlinks=True)
        system_count = sum(1 for _ in dst_system.glob("*.tbd"))
        logger.info("Copied %d system sub-library TBDs", system_count)

    logger.info(
        "Copied %d usr/lib/*.tbd from reference SDK %s", copied, ref_sdk,
    )
