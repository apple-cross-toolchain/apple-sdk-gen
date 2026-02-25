from __future__ import annotations

from dataclasses import dataclass, field

from .models.types import PlatformName


@dataclass
class PlatformConfig:
    name: PlatformName
    sdk_prefix: str
    platform_dir: str
    target_triples: list[str] = field(default_factory=list)
    swift_triples: list[str] = field(default_factory=list)


PLATFORM_CONFIGS: dict[str, PlatformConfig] = {
    "ios": PlatformConfig(
        name=PlatformName.IOS,
        sdk_prefix="iPhoneOS",
        platform_dir="iPhoneOS.platform",
        target_triples=["arm64-apple-ios"],
        swift_triples=["arm64-apple-ios"],
    ),
    "macos": PlatformConfig(
        name=PlatformName.MACOS,
        sdk_prefix="MacOSX",
        platform_dir="MacOSX.platform",
        target_triples=["arm64-apple-macos", "x86_64-apple-macos"],
        swift_triples=["arm64-apple-macos", "x86_64-apple-macos"],
    ),
    "tvos": PlatformConfig(
        name=PlatformName.TVOS,
        sdk_prefix="AppleTVOS",
        platform_dir="AppleTVOS.platform",
        target_triples=["arm64-apple-tvos"],
        swift_triples=["arm64-apple-tvos"],
    ),
    "watchos": PlatformConfig(
        name=PlatformName.WATCHOS,
        sdk_prefix="WatchOS",
        platform_dir="WatchOS.platform",
        target_triples=["arm64_32-apple-watchos"],
        swift_triples=["arm64_32-apple-watchos"],
    ),
    "visionos": PlatformConfig(
        name=PlatformName.VISIONOS,
        sdk_prefix="XROS",
        platform_dir="XROS.platform",
        target_triples=["arm64-apple-xros"],
        swift_triples=["arm64-apple-xros"],
    ),
}


def tbd_targets_for_platform(platform_key: str, sdk_version: str) -> list[str]:
    """Generate TBD target strings like 'arm64-ios' for a platform."""
    cfg = PLATFORM_CONFIGS.get(platform_key)
    if not cfg:
        return []
    os_name = {
        "ios": "ios",
        "macos": "macos",
        "tvos": "tvos",
        "watchos": "watchos",
        "visionos": "xros",
    }.get(platform_key, platform_key)

    targets = []
    for triple in cfg.target_triples:
        arch = triple.split("-")[0]
        targets.append(f"{arch}-{os_name}")
    return targets


# Known framework re-export relationships
REEXPORTS: dict[str, list[str]] = {
    "Foundation": [
        "/usr/lib/libobjc.A.dylib",
        "/usr/lib/libSystem.B.dylib",
    ],
    "UIKit": [
        "/System/Library/Frameworks/Foundation.framework/Foundation",
        "/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics",
    ],
    "AppKit": [
        "/System/Library/Frameworks/Foundation.framework/Foundation",
        "/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics",
    ],
    "CoreFoundation": [
        "/usr/lib/libSystem.B.dylib",
    ],
}
