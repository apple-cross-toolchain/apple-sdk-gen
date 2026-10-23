from __future__ import annotations

import argparse
import asyncio
import sys

from .config import PLATFORM_CONFIGS
from .generators.sdk_metadata import default_xcode_build, default_xcode_version


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="apple-sdk-gen",
        description="Generate Apple SDK stubs from public documentation API",
    )

    parser.add_argument(
        "--platforms",
        type=str,
        default="ios,macos",
        help="Comma-separated platforms: " + ",".join(PLATFORM_CONFIGS.keys()),
    )
    parser.add_argument(
        "--sdk-version",
        type=str,
        required=True,
        help="SDK version (e.g., 17.0, 18.0)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="./output",
        help="Output directory",
    )
    parser.add_argument(
        "--cache-dir",
        type=str,
        default="./.cache",
        help="Cache directory for API responses",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=10,
        help="Maximum concurrent API requests",
    )
    parser.add_argument(
        "--rate-limit",
        type=float,
        default=10.0,
        help="API requests per second",
    )
    parser.add_argument(
        "--all-frameworks",
        action="store_true",
        help="Generate all available frameworks",
    )
    parser.add_argument(
        "--frameworks",
        type=str,
        default=None,
        help="Comma-separated list of framework names to generate",
    )
    parser.add_argument(
        "--exclude-frameworks",
        type=str,
        default=None,
        help="Comma-separated list of framework names to exclude",
    )
    parser.add_argument(
        "--include-swift",
        action="store_true",
        help="Generate .swiftinterface files",
    )
    parser.add_argument(
        "--include-libc",
        action="store_true",
        help="Download and install C stdlib/POSIX headers from Apple OSS",
    )
    parser.add_argument(
        "--include-cxx",
        action="store_true",
        help="Download and install C++ standard library headers from LLVM",
    )
    parser.add_argument(
        "--include-simulators",
        action="store_true",
        help="Also generate simulator SDKs for each device platform",
    )
    parser.add_argument(
        "--swift-stdlib-path",
        type=str,
        default=None,
        help="Path to a reference SDK root (Xcode.app/) to copy Swift stdlib "
             ".swiftinterface files from (usr/lib/swift/*.swiftmodule/)",
    )
    parser.add_argument(
        "--swift-version",
        type=str,
        default=None,
        help="swift.org release whose macOS package supplies the Darwin Swift "
             "runtime, shims and clang resource directory (e.g. 6.4.0)",
    )
    parser.add_argument(
        "--swift-pkg",
        type=str,
        default=None,
        help="Local copy of that package instead of downloading it",
    )
    parser.add_argument(
        "--swift-pkg-sha256",
        type=str,
        default=None,
        help="Expected sha256 of the package",
    )
    parser.add_argument(
        "--xcode-version",
        type=str,
        default=None,
        help="Xcode version recorded in version.plist (default: derived from --sdk-version)",
    )
    parser.add_argument(
        "--xcode-build",
        type=str,
        default=None,
        help="Xcode build recorded in version.plist (default: <major>A0)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="count",
        default=0,
        help="Increase verbosity (-v for INFO, -vv for DEBUG)",
    )

    args = parser.parse_args(argv)

    if args.swift_pkg and not args.swift_version:
        parser.error("--swift-pkg requires --swift-version")
    args.xcode_version = args.xcode_version or default_xcode_version(args.sdk_version)
    args.xcode_build = args.xcode_build or default_xcode_build(args.xcode_version)

    # Validate platforms
    platforms = [p.strip() for p in args.platforms.split(",")]
    for p in platforms:
        if p not in PLATFORM_CONFIGS:
            parser.error(f"Unknown platform: {p}. Available: {', '.join(PLATFORM_CONFIGS.keys())}")
    args.platforms = platforms

    # Expand simulator variants for each device platform
    if args.include_simulators:
        sim_keys = []
        for p in platforms:
            sim_key = f"{p}-simulator"
            if sim_key in PLATFORM_CONFIGS and sim_key not in platforms:
                sim_keys.append(sim_key)
        args.platforms.extend(sim_keys)

    # Parse framework lists
    if args.frameworks:
        args.frameworks = {f.strip() for f in args.frameworks.split(",")}
    if args.exclude_frameworks:
        args.exclude_frameworks = {f.strip() for f in args.exclude_frameworks.split(",")}

    return args


def main() -> None:
    args = parse_args()

    # Defer import to avoid circular deps and allow async
    from .main import run
    asyncio.run(run(args))
