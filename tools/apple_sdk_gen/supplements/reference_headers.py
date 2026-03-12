"""Copy usr/include/ from a reference SDK.

When a reference SDK is available, its ``usr/include/`` tree contains
complete, correctly-generated C/POSIX headers and properly structured
module maps that the Swift compiler needs to compile real framework
``.swiftinterface`` files.  This supplement copies the entire tree,
replacing any synthetic stubs that earlier supplements may have produced.
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from ..config import PLATFORM_CONFIGS

logger = logging.getLogger(__name__)


def install_reference_headers(
    sdk_root: Path,
    platform_key: str,
    reference_root: Path,
) -> None:
    """Copy ``usr/include/`` from the reference SDK into *sdk_root*."""
    cfg = PLATFORM_CONFIGS.get(platform_key)
    if cfg is None:
        logger.warning("Unknown platform %s, skipping reference headers", platform_key)
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

    ref_include = ref_sdk / "usr" / "include"
    if not ref_include.is_dir():
        logger.warning("No usr/include/ in reference SDK %s", ref_sdk)
        return

    dst_include = sdk_root / "usr" / "include"

    # Remove the generated usr/include and replace with the reference copy
    if dst_include.exists():
        shutil.rmtree(dst_include)

    shutil.copytree(ref_include, dst_include, symlinks=True)

    logger.info(
        "Copied usr/include/ from reference SDK %s", ref_sdk,
    )
