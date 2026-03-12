"""Copy clang resource directory from a reference Xcode toolchain.

The Swift distribution includes a symlink ``lib/swift/clang -> ../clang/17``
that expects the clang builtin headers (stdarg.h, etc.) to be present at
``lib/clang/17/``.  When using an LLVM binary with a different clang version
(e.g. 21), this symlink dangles.  This supplement copies ``lib/clang/``
from the reference Xcode toolchain so the symlink resolves correctly.
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)


def install_reference_clang_resource(
    output_dir: Path,
    reference_root: Path,
) -> None:
    """Copy ``usr/lib/clang/`` from the reference Xcode Toolchains dir.

    *output_dir* should be the top-level output directory (containing
    ``Xcode.app/``).  *reference_root* is the reference SDK root.
    """
    ref_toolchain_lib = (
        reference_root / "Xcode.app" / "Contents" / "Developer"
        / "Toolchains" / "XcodeDefault.xctoolchain" / "usr" / "lib" / "clang"
    )
    if not ref_toolchain_lib.is_dir():
        ref_toolchain_lib = (
            reference_root / "Contents" / "Developer"
            / "Toolchains" / "XcodeDefault.xctoolchain" / "usr" / "lib" / "clang"
        )
    if not ref_toolchain_lib.is_dir():
        logger.warning("Reference toolchain clang dir not found at %s", ref_toolchain_lib)
        return

    dst_clang = (
        output_dir / "Xcode.app" / "Contents" / "Developer"
        / "Toolchains" / "XcodeDefault.xctoolchain" / "usr" / "lib" / "clang"
    )
    dst_clang.parent.mkdir(parents=True, exist_ok=True)

    if dst_clang.exists():
        shutil.rmtree(dst_clang)

    shutil.copytree(ref_toolchain_lib, dst_clang, symlinks=True)

    logger.info(
        "Copied clang resource directory from %s", ref_toolchain_lib,
    )
