from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from ..config import PLATFORM_CONFIGS, REEXPORTS, PlatformConfig, tbd_targets_for_platform
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

    sdk_name = f"{cfg.sdk_prefix}{sdk_version}.sdk"
    sdk_root = output_dir / cfg.platform_dir / "Developer" / "SDKs" / sdk_name

    # Create SDK root and metadata
    sdk_root.mkdir(parents=True, exist_ok=True)

    # SDKSettings.json
    settings = generate_sdk_settings(cfg.sdk_prefix, sdk_version)
    (sdk_root / "SDKSettings.json").write_text(settings)

    # Platform Info.plist
    platform_dir = output_dir / cfg.platform_dir
    info_plist = generate_info_plist(cfg.sdk_prefix, sdk_version)
    (platform_dir / "Info.plist").write_text(info_plist)

    # TBD targets for this platform
    tbd_targets = tbd_targets_for_platform(platform_key, sdk_version)

    # Generate each framework
    for fw_name, symbols in frameworks.items():
        _assemble_framework(
            sdk_root=sdk_root,
            framework_name=fw_name,
            symbols=symbols,
            all_frameworks=frameworks,
            tbd_targets=tbd_targets,
            include_swift=include_swift,
            platform_config=cfg,
        )

    logger.info("Assembled SDK at %s (%d frameworks)", sdk_root, len(frameworks))
    return sdk_root


def _assemble_framework(
    sdk_root: Path,
    framework_name: str,
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

    # TBD stub
    reexports = REEXPORTS.get(framework_name)
    tbd_content = generate_tbd(
        framework_name,
        symbols,
        targets=tbd_targets,
        reexports=reexports,
    )
    (fw_dir / f"{framework_name}.tbd").write_text(tbd_content)

    logger.debug("Generated framework %s (%d symbols)", framework_name, len(symbols))
