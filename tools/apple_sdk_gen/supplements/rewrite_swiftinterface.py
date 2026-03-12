"""Rewrite swift-compiler-version in .swiftinterface files.

Apple's .swiftinterface files record the Apple Swift compiler version
(e.g. ``Apple Swift version 6.2``).  The open-source Swift compiler
rejects interfaces built by a different compiler.  This module rewrites
the ``swift-compiler-version:`` header line to match the host compiler,
allowing the interfaces to be loaded.
"""

from __future__ import annotations

import logging
import re
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

_compiler_version: str | None = None


def _detect_swift_version(swift_path: str = "swiftc") -> str:
    """Run ``swiftc --version`` and return the version string."""
    global _compiler_version
    if _compiler_version is not None:
        return _compiler_version
    try:
        out = subprocess.check_output(
            [swift_path, "--version"], stderr=subprocess.STDOUT, text=True,
        )
        # e.g. "Swift version 6.2.3 (swift-6.2.3-RELEASE)"
        m = re.search(r"(Swift version \S+ \([^)]+\))", out)
        if m:
            _compiler_version = m.group(1)
            return _compiler_version
    except Exception:
        pass
    _compiler_version = "Swift version 6.2.3 (swift-6.2.3-RELEASE)"
    return _compiler_version


def rewrite_swiftinterface_versions(root: Path, swift_path: str = "swiftc") -> int:
    """Rewrite ``swift-compiler-version:`` in all .swiftinterface files under *root*.

    Returns the number of files rewritten.
    """
    version = _detect_swift_version(swift_path)
    count = 0
    for path in root.rglob("*.swiftinterface"):
        if _rewrite_one(path, version):
            count += 1
    return count


def _rewrite_one(path: Path, version: str) -> bool:
    """Rewrite a single .swiftinterface file. Returns True if modified."""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return False

    original = text

    # Rewrite swift-compiler-version line
    text = re.sub(
        r"^(// swift-compiler-version: ).*$",
        rf"\g<1>{version}",
        text,
        count=1,
        flags=re.MULTILINE,
    )

    # Rewrite -interface-compiler-version in swift-module-flags-ignorable
    # Extract major.minor from e.g. "Swift version 6.2.3 (swift-6.2.3-RELEASE)"
    parts = version.split()
    iface_ver = "6.2"
    for p in parts:
        m = re.match(r"(\d+\.\d+)", p)
        if m:
            iface_ver = m.group(1)
            break
    text = re.sub(
        r"-interface-compiler-version \S+",
        f"-interface-compiler-version {iface_ver}",
        text,
    )

    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False
