from __future__ import annotations

import logging
from collections import defaultdict

from ..models.symbol import Symbol
from ..models.types import SymbolKind

logger = logging.getLogger(__name__)

SWIFT_INTERFACE_HEADER = """\
// swift-interface-format-version: 1.0
// swift-compiler-version: Apple Swift version 5.9
// swift-module-flags: -module-name {module_name}
"""


def generate_swiftinterface(
    framework_name: str,
    symbols: list[Symbol],
    triple: str,
) -> str:
    """Generate a .swiftinterface file for a framework."""
    lines: list[str] = []
    lines.append(SWIFT_INTERFACE_HEADER.format(module_name=framework_name))
    lines.append(f"import {framework_name}")
    lines.append("")

    # Group symbols: top-level vs children
    top_level: list[Symbol] = []
    children_map: dict[str, list[Symbol]] = defaultdict(list)

    for sym in symbols:
        if not sym.is_swift:
            continue
        if sym.parent_identifier:
            children_map[sym.parent_identifier].append(sym)
        elif sym.kind in (
            SymbolKind.CLASS,
            SymbolKind.STRUCT,
            SymbolKind.ENUM,
            SymbolKind.PROTOCOL,
            SymbolKind.FUNC,
            SymbolKind.VAR,
            SymbolKind.TYPEALIAS,
        ):
            top_level.append(sym)

    for sym in top_level:
        avail = _swift_availability(sym)
        if avail:
            lines.append(avail)

        decl = sym.swift_declaration
        if decl is None:
            continue

        decl_text = decl.render().strip()
        if not decl_text:
            continue

        # Check if this is a type that can have children
        if sym.kind in (SymbolKind.CLASS, SymbolKind.STRUCT, SymbolKind.ENUM, SymbolKind.PROTOCOL):
            lines.append(f"{decl_text} {{")
            # Emit children
            child_syms = children_map.get(sym.identifier, [])
            for child in child_syms:
                child_avail = _swift_availability(child)
                if child_avail:
                    lines.append(f"  {child_avail}")
                if child.swift_declaration:
                    child_text = child.swift_declaration.render().strip()
                    if child_text:
                        lines.append(f"  {child_text}")
            lines.append("}")
        else:
            lines.append(decl_text)

        lines.append("")

    return "\n".join(lines) + "\n"


def _swift_availability(sym: Symbol) -> str | None:
    seen: set[str] = set()
    parts = []
    for avail in sym.availability:
        platform = _swift_platform_name(avail.platform.value)
        if platform is None:
            continue
        if avail.unavailable:
            entry = f"{platform}, unavailable"
        elif avail.deprecated_at:
            intro = avail.introduced_at or "1.0"
            entry = f"{platform}, introduced: {intro}, deprecated: {avail.deprecated_at}"
        elif avail.introduced_at:
            entry = f"{platform}, introduced: {avail.introduced_at}"
        else:
            continue
        if entry not in seen:
            seen.add(entry)
            parts.append(entry)

    if not parts:
        return None
    return "@available(" + ", ".join(parts) + ")"


def _swift_platform_name(name: str) -> str | None:
    mapping = {
        "iOS": "iOS",
        "iPadOS": "iOS",
        "macOS": "macOS",
        "tvOS": "tvOS",
        "watchOS": "watchOS",
        "visionOS": "visionOS",
        "Mac Catalyst": "macCatalyst",
    }
    return mapping.get(name)
