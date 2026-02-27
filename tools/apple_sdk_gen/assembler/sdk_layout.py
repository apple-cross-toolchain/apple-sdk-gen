from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from ..config import (
    COMPANION_FRAMEWORKS,
    FRAMEWORK_NAME_MAPPINGS,
    PLATFORM_CONFIGS,
    PLATFORM_EXCLUDED_MODULES,
    REEXPORTS,
    SUPPLEMENTARY_FRAMEWORKS,
    SWIFT_OVERLAY_FRAMEWORKS,
    PlatformConfig,
    tbd_targets_for_platform,
)
from ..generators.modulemap import generate_modulemap
from ..generators.objc_header import generate_umbrella_header
from ..generators.sdk_metadata import generate_info_plist, generate_sdk_settings
from ..generators.swiftinterface import generate_swiftinterface
from ..generators.tbd import generate_tbd
from ..models.symbol import Symbol

logger = logging.getLogger(__name__)


@dataclass
class FrameworkOutput:
    name: str
    symbols: list[Symbol]


def assemble_sdk(
    output_dir: Path,
    platform_key: str,
    sdk_version: str,
    frameworks: dict[str, list[Symbol]],
    include_swift: bool = False,
) -> Path:
    """Assemble a complete SDK directory structure.

    Returns the path to the generated SDK root.
    """
    cfg = PLATFORM_CONFIGS.get(platform_key)
    if cfg is None:
        raise ValueError(f"Unknown platform: {platform_key}")

    # Replicate Xcode.app directory hierarchy
    platforms_dir = output_dir / "Xcode.app" / "Contents" / "Developer" / "Platforms"
    base_sdk_name = f"{cfg.sdk_prefix}.sdk"
    versioned_sdk_name = f"{cfg.sdk_prefix}{sdk_version}.sdk"
    sdks_dir = platforms_dir / cfg.platform_dir / "Developer" / "SDKs"
    sdk_root = sdks_dir / base_sdk_name

    # Create SDK root and metadata
    sdk_root.mkdir(parents=True, exist_ok=True)

    # Versioned symlink: e.g. iPhoneOS18.0.sdk → iPhoneOS.sdk
    versioned_link = sdks_dir / versioned_sdk_name
    if versioned_link.exists() or versioned_link.is_symlink():
        versioned_link.unlink()
    versioned_link.symlink_to(base_sdk_name)

    # SDKSettings.json (enhanced with per-platform data)
    settings = generate_sdk_settings(
        cfg.sdk_prefix, sdk_version, platform_key=platform_key,
    )
    (sdk_root / "SDKSettings.json").write_text(settings)

    # Platform Info.plist
    platform_dir = platforms_dir / cfg.platform_dir
    info_plist = generate_info_plist(cfg.sdk_prefix, sdk_version)
    (platform_dir / "Info.plist").write_text(info_plist)

    # TBD targets for this platform
    tbd_targets = tbd_targets_for_platform(platform_key, sdk_version)
    excluded = PLATFORM_EXCLUDED_MODULES.get(platform_key, set())

    # Generate each framework
    for fw_name, symbols in frameworks.items():
        # Apply name mapping (doc API name → real framework name)
        mapped_name = FRAMEWORK_NAME_MAPPINGS.get(fw_name, fw_name)

        _assemble_framework(
            sdk_root=sdk_root,
            framework_name=mapped_name,
            doc_name=fw_name,
            symbols=symbols,
            all_frameworks=frameworks,
            tbd_targets=tbd_targets,
            include_swift=include_swift,
            platform_config=cfg,
        )

        # Emit TBD-only stubs for companion frameworks
        for companion in COMPANION_FRAMEWORKS.get(mapped_name, []):
            if companion not in excluded:
                _assemble_tbd_only_framework(sdk_root, companion, tbd_targets)

    # Emit TBD-only stubs for supplementary frameworks (no doc API entry)
    for supp_name in SUPPLEMENTARY_FRAMEWORKS:
        if supp_name not in excluded:
            _assemble_tbd_only_framework(sdk_root, supp_name, tbd_targets)

    # Generate TBD-only overlay frameworks for SwiftUI integration
    if include_swift:
        for overlay_name in SWIFT_OVERLAY_FRAMEWORKS:
            if overlay_name not in excluded:
                _assemble_tbd_only_framework(sdk_root, overlay_name, tbd_targets)

    logger.info("Assembled SDK at %s (%d frameworks)", sdk_root, len(frameworks))
    return sdk_root


def _assemble_framework(
    sdk_root: Path,
    framework_name: str,
    doc_name: str,
    symbols: list[Symbol],
    all_frameworks: dict[str, list[Symbol]],
    tbd_targets: list[str],
    include_swift: bool,
    platform_config: PlatformConfig,
) -> None:
    fw_dir = sdk_root / "System" / "Library" / "Frameworks" / f"{framework_name}.framework"

    # Headers
    headers_dir = fw_dir / "Headers"
    headers_dir.mkdir(parents=True, exist_ok=True)

    # Build a global symbol lookup for cross-referencing, keyed by normalized path
    all_symbols: dict[str, Symbol] = {}
    for fw_syms in all_frameworks.values():
        for sym in fw_syms:
            if sym.identifier and "/documentation/" in sym.identifier:
                path = "/documentation/" + sym.identifier.split("/documentation/", 1)[1]
                all_symbols[path.lower().rstrip("/")] = sym

    header_content = generate_umbrella_header(
        framework_name, symbols, all_symbols=all_symbols
    )
    (headers_dir / f"{framework_name}.h").write_text(header_content)

    # Generate per-symbol stub headers for import compatibility
    # (e.g. #import <UIKit/UIView.h> → re-exports umbrella)
    seen_names = {framework_name}
    for sym in symbols:
        name = sym.objc_name or sym.title
        if not name or name in seen_names:
            continue
        if sym.parent_identifier:
            continue
        # Skip names that aren't valid header filenames
        if not name.isidentifier() or len(name) > 200:
            continue
        seen_names.add(name)
        stub = (
            f"// Auto-generated stub \u2014 all declarations are in {framework_name}.h\n"
            f"#import <{framework_name}/{framework_name}.h>\n"
        )
        (headers_dir / f"{name}.h").write_text(stub)

    # Modules
    modules_dir = fw_dir / "Modules"
    modules_dir.mkdir(parents=True, exist_ok=True)

    modulemap = generate_modulemap(framework_name)
    (modules_dir / "module.modulemap").write_text(modulemap)

    # Swift interfaces
    if include_swift:
        for triple in platform_config.swift_triples:
            swift_mod_dir = modules_dir / f"{framework_name}.swiftmodule"
            swift_mod_dir.mkdir(parents=True, exist_ok=True)

            swiftinterface = generate_swiftinterface(framework_name, symbols, triple)
            (swift_mod_dir / f"{triple}.swiftinterface").write_text(swiftinterface)

    # TBD stub — use mapped name for install path, doc name for re-export lookup
    reexports = REEXPORTS.get(framework_name) or REEXPORTS.get(doc_name)
    tbd_content = generate_tbd(
        framework_name,
        symbols,
        targets=tbd_targets,
        reexports=reexports,
    )
    (fw_dir / f"{framework_name}.tbd").write_text(tbd_content)

    logger.debug("Generated framework %s (%d symbols)", framework_name, len(symbols))


def _assemble_tbd_only_framework(
    sdk_root: Path,
    name: str,
    tbd_targets: list[str],
) -> None:
    """Create a minimal .framework with only a TBD stub (no headers/modulemap).

    Used for private underscore overlay frameworks needed at link time.
    """
    fw_dir = sdk_root / "System" / "Library" / "Frameworks" / f"{name}.framework"
    fw_dir.mkdir(parents=True, exist_ok=True)

    targets_str = ", ".join(tbd_targets)
    install_name = f"/System/Library/Frameworks/{name}.framework/{name}"

    tbd_content = (
        f"--- !tapi-tbd\n"
        f"tbd-version:     4\n"
        f"targets:         [{targets_str}]\n"
        f"install-name:    '{install_name}'\n"
        f"...\n"
    )
    (fw_dir / f"{name}.tbd").write_text(tbd_content)
