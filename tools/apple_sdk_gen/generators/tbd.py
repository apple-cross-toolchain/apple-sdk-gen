from __future__ import annotations

from ..models.symbol import Symbol
from ..utils.usr_parser import FrameworkTBDSymbols


def collect_tbd_symbols(symbols: list[Symbol]) -> FrameworkTBDSymbols:
    tbd_syms = FrameworkTBDSymbols()
    for sym in symbols:
        if sym.usr:
            tbd_syms.add_from_usr(sym.usr)
    return tbd_syms


def generate_tbd(
    framework_name: str,
    symbols: list[Symbol],
    targets: list[str],
    install_name: str | None = None,
    reexports: list[str] | None = None,
) -> str:
    """Generate a TBD v4 stub file for a framework.

    Produces the TBD format directly instead of going through a YAML library
    to avoid anchor/alias references and ensure Apple ld compatibility.
    """
    if install_name is None:
        install_name = f"/System/Library/Frameworks/{framework_name}.framework/{framework_name}"

    tbd_syms = collect_tbd_symbols(symbols)

    targets_str = _format_flow_list(targets)

    lines: list[str] = []
    lines.append("--- !tapi-tbd")
    lines.append("tbd-version:     4")
    lines.append(f"targets:         {targets_str}")
    lines.append(f"install-name:    '{install_name}'")
    lines.append("current-version: 1.0.0")
    lines.append("compatibility-version: 1.0.0")

    if reexports:
        lines.append("reexported-libraries:")
        lines.append(f"  - targets:   {targets_str}")
        lines.append("    libraries:")
        for lib in reexports:
            lines.append(f"      - '{lib}'")

    # Build exports section
    has_symbols = bool(tbd_syms.symbols)
    has_classes = bool(tbd_syms.objc_classes)

    if has_symbols or has_classes:
        lines.append("exports:")
        lines.append(f"  - targets:      {targets_str}")
        if has_symbols:
            lines.append(f"    symbols:      {_format_flow_list(sorted(tbd_syms.symbols))}")
        if has_classes:
            lines.append(f"    objc-classes: {_format_flow_list(sorted(tbd_syms.objc_classes))}")
    else:
        # Emit a stub symbol so the TBD is valid
        lines.append("exports:")
        lines.append(f"  - targets:      {targets_str}")
        safe_name = framework_name.replace(" ", "").replace("/", "")
        lines.append(f"    symbols:      [ _{safe_name}_stub ]")

    lines.append("...")
    return "\n".join(lines) + "\n"


def _format_flow_list(items: list[str]) -> str:
    """Format a list as YAML flow style: [ item1, item2 ]"""
    return "[ " + ", ".join(items) + " ]"
