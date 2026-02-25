"""Download and install C standard library / POSIX headers from Apple OSS.

These headers populate ``<sdk>/usr/include/`` so that code using
``#include <stdio.h>``, ``#include <pthread.h>`` etc. can compile against
the generated SDK stubs.

Three GitHub repositories are used:

- **apple-oss-distributions/Libc** – stdio, stdlib, string, math, …
- **apple-oss-distributions/xnu** – sys/, mach/, machine/, arm/, …
- **apple-oss-distributions/libpthread** – pthread.h, sched.h

A matching ``libSystem.B.tbd`` stub is generated so that ``-lSystem``
resolves at link time.
"""

from __future__ import annotations

import io
import logging
import zipfile
from pathlib import Path
from urllib.request import urlopen, Request

logger = logging.getLogger(__name__)

# Maps SDK version → (Libc tag, xnu tag, libpthread tag).
# Tags are taken from the corresponding macOS/iOS release trains.
VERSION_TAGS: dict[str, tuple[str, str, str]] = {
    "15.0": ("Libc-1534.81.1", "xnu-10002.1.13", "libpthread-485.60.2"),
    "15.2": ("Libc-1534.81.1", "xnu-10002.41.9", "libpthread-485.60.2"),
    "16.0": ("Libc-1583.40.7", "xnu-10063.61.3", "libpthread-519.40.4"),
    "17.0": ("Libc-1583.100.4", "xnu-10063.121.3", "libpthread-519.100.3"),
    "18.0": ("Libc-1583.100.4", "xnu-11215.1.10", "libpthread-519.100.3"),
    "18.2": ("Libc-1583.100.4", "xnu-11215.61.5", "libpthread-519.100.3"),
    # Fallback: use latest known tags
}

_GITHUB_ZIP = "https://github.com/apple-oss-distributions/{repo}/archive/refs/tags/{tag}.zip"


# ── Extraction rules ────────────────────────────────────────────────
# Each entry is (repo, tag-key-index, src_prefix, dst_prefix) where
# src_prefix is the path inside the archive to copy from and dst_prefix
# is the destination under <sdk>/usr/include/.

_LIBC_HEADERS = [
    # Basic C headers from Libc/include
    ("include/", ""),
]

_XNU_HEADERS = [
    # BSD sys/ headers
    ("bsd/sys/", "sys/"),
    ("bsd/machine/", "machine/"),
    ("bsd/arm/", "arm/"),
    ("bsd/i386/", "i386/"),
    ("bsd/net/", "net/"),
    ("bsd/netinet/", "netinet/"),
    ("bsd/netinet6/", "netinet6/"),
    # EXTERNAL_HEADERS — mach/, architecture/ etc.
    ("EXTERNAL_HEADERS/", ""),
    # osfmk mach headers
    ("osfmk/mach/", "mach/"),
    ("bsd/sys/_types/", "sys/_types/"),
    ("bsd/i386/_types.h", "i386/_types.h"),
    ("bsd/arm/_types.h", "arm/_types.h"),
]

_LIBPTHREAD_HEADERS = [
    ("include/pthread/", "pthread/"),
    ("include/pthread.h", "pthread.h"),
    ("include/sched.h", "sched.h"),
]


def install_libc_headers(
    sdk_root: Path,
    sdk_version: str,
    tbd_targets: list[str],
    cache_dir: Path,
) -> None:
    """Download Apple OSS headers and install them into the SDK."""
    tags = VERSION_TAGS.get(sdk_version)
    if tags is None:
        # Fall back to latest known
        tags = list(VERSION_TAGS.values())[-1]
        logger.warning(
            "No exact libc tags for SDK %s, falling back to %s",
            sdk_version, tags,
        )

    libc_tag, xnu_tag, pthread_tag = tags

    usr_include = sdk_root / "usr" / "include"
    usr_include.mkdir(parents=True, exist_ok=True)

    # Download and extract each repo
    _extract_repo("Libc", libc_tag, _LIBC_HEADERS, usr_include, cache_dir)
    _extract_repo("xnu", xnu_tag, _XNU_HEADERS, usr_include, cache_dir)
    _extract_repo("libpthread", pthread_tag, _LIBPTHREAD_HEADERS, usr_include, cache_dir)

    # Generate libSystem.B.tbd
    _generate_libsystem_tbd(sdk_root, tbd_targets)

    logger.info("Installed libc headers into %s", usr_include)


def _download_zip(repo: str, tag: str, cache_dir: Path) -> Path:
    """Download a GitHub archive zip, caching to disk."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    cached = cache_dir / f"{repo}-{tag}.zip"
    if cached.exists():
        logger.debug("Using cached %s", cached)
        return cached

    url = _GITHUB_ZIP.format(repo=repo, tag=tag)
    logger.info("Downloading %s ...", url)

    req = Request(url, headers={"User-Agent": "apple-sdk-gen/1.0"})
    with urlopen(req, timeout=120) as resp:
        data = resp.read()

    cached.write_bytes(data)
    return cached


def _extract_repo(
    repo: str,
    tag: str,
    rules: list[tuple[str, str]],
    usr_include: Path,
    cache_dir: Path,
) -> None:
    """Extract header files from a GitHub archive zip into usr/include."""
    zip_path = _download_zip(repo, tag, cache_dir)

    with zipfile.ZipFile(zip_path) as zf:
        # The archive root is "{repo}-{tag}/"
        prefix = f"{repo}-{tag}/"
        members = zf.namelist()

        for src_rule, dst_rule in rules:
            full_src = prefix + src_rule
            for member in members:
                if not member.startswith(full_src):
                    continue
                # Skip directories
                if member.endswith("/"):
                    continue
                # Only extract .h files
                if not member.endswith(".h"):
                    continue

                rel = member[len(full_src):]
                dst = usr_include / dst_rule / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(zf.read(member))

    logger.debug("Extracted %s headers from %s-%s", repo, repo, tag)


def _generate_libsystem_tbd(sdk_root: Path, tbd_targets: list[str]) -> None:
    """Generate a minimal libSystem.B.tbd stub."""
    usr_lib = sdk_root / "usr" / "lib"
    usr_lib.mkdir(parents=True, exist_ok=True)

    targets_str = ", ".join(tbd_targets)

    tbd = f"""\
--- !tapi-tbd
tbd-version:     4
targets:         [{targets_str}]
install-name:    '/usr/lib/libSystem.B.dylib'
current-version: 1345.100.2
exports:
  - targets:     [{targets_str}]
    re-exports:
      - '/usr/lib/system/libsystem_c.dylib'
      - '/usr/lib/system/libsystem_kernel.dylib'
      - '/usr/lib/system/libsystem_malloc.dylib'
      - '/usr/lib/system/libsystem_pthread.dylib'
      - '/usr/lib/system/libsystem_platform.dylib'
      - '/usr/lib/system/libsystem_info.dylib'
      - '/usr/lib/system/libdyld.dylib'
      - '/usr/lib/system/libsystem_blocks.dylib'
      - '/usr/lib/system/libsystem_darwin.dylib'
      - '/usr/lib/system/libsystem_m.dylib'
      - '/usr/lib/system/libsystem_trace.dylib'
      - '/usr/lib/system/libxpc.dylib'
      - '/usr/lib/system/libdispatch.dylib'
      - '/usr/lib/system/libcorecrypto.dylib'
      - '/usr/lib/system/libcommonCrypto.dylib'
      - '/usr/lib/system/libsystem_asl.dylib'
      - '/usr/lib/system/libsystem_notify.dylib'
      - '/usr/lib/system/libsystem_networkextension.dylib'
      - '/usr/lib/system/libsystem_sandbox.dylib'
      - '/usr/lib/system/libsystem_featureflags.dylib'
      - '/usr/lib/system/libsystem_collections.dylib'
      - '/usr/lib/system/libsystem_containermanager.dylib'
      - '/usr/lib/system/libsystem_configuration.dylib'
      - '/usr/lib/system/libsystem_coreservices.dylib'
      - '/usr/lib/system/libsystem_dnssd.dylib'
      - '/usr/lib/system/libsystem_msgh.dylib'
      - '/usr/lib/system/libcompiler_rt.dylib'
      - '/usr/lib/system/libunc.dylib'
      - '/usr/lib/system/libcopyfile.dylib'
      - '/usr/lib/system/libremovefile.dylib'
      - '/usr/lib/system/libkeymgr.dylib'
      - '/usr/lib/system/libmacho.dylib'
      - '/usr/lib/system/libquarantine.dylib'
...
"""
    (usr_lib / "libSystem.B.tbd").write_text(tbd)

    # Also create a libc.tbd symlink-equivalent that re-exports libSystem
    libc_tbd = f"""\
--- !tapi-tbd
tbd-version:     4
targets:         [{targets_str}]
install-name:    '/usr/lib/libc.dylib'
current-version: 1345.100.2
exports:
  - targets:     [{targets_str}]
    re-exports:
      - '/usr/lib/libSystem.B.dylib'
...
"""
    (usr_lib / "libc.tbd").write_text(libc_tbd)

    logger.debug("Generated libSystem.B.tbd and libc.tbd")
