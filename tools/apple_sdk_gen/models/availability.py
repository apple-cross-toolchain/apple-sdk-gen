from __future__ import annotations

from ..models.symbol import PlatformAvailability, Symbol
from ..models.types import PlatformName
from ..utils.version import Version


def is_available(
    symbol: Symbol,
    platform: PlatformName,
    sdk_version: str,
) -> bool:
    target = Version.parse(sdk_version)
    for avail in symbol.availability:
        if avail.platform != platform:
            continue
        if avail.unavailable:
            return False
        if avail.introduced_at:
            introduced = Version.parse(avail.introduced_at)
            if introduced > target:
                return False
        return True
    # If no availability info for this platform, assume not available
    # unless no availability info exists at all (assume available)
    if not symbol.availability:
        return True
    return False


def availability_macro(symbol: Symbol) -> str | None:
    seen: set[str] = set()
    parts = []
    for avail in symbol.availability:
        if avail.unavailable:
            continue
        if not avail.introduced_at:
            continue
        macro_name = _platform_macro_name(avail.platform)
        if macro_name is None:
            continue
        entry = f"{macro_name}({avail.introduced_at})"
        if entry not in seen:
            seen.add(entry)
            parts.append(entry)

    if not parts:
        return None
    return f"API_AVAILABLE({', '.join(parts)})"


def deprecated_macro(symbol: Symbol) -> str | None:
    parts = []
    for avail in symbol.availability:
        if not avail.deprecated_at:
            continue
        macro_name = _platform_macro_name(avail.platform)
        if macro_name is None:
            continue
        intro = avail.introduced_at or "1.0"
        parts.append(f"{macro_name}({intro}, {avail.deprecated_at})")

    if not parts:
        return None
    return f"API_DEPRECATED(\"\", {', '.join(parts)})"


def _platform_macro_name(platform: PlatformName) -> str | None:
    mapping = {
        PlatformName.IOS: "ios",
        PlatformName.IPADOS: "ios",
        PlatformName.MACOS: "macos",
        PlatformName.TVOS: "tvos",
        PlatformName.WATCHOS: "watchos",
        PlatformName.VISIONOS: "visionos",
        PlatformName.MAC_CATALYST: "macCatalyst",
    }
    return mapping.get(platform)
