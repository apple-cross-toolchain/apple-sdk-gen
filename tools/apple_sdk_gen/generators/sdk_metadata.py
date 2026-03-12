from __future__ import annotations

import json
import plistlib


# Per-platform settings for SDKSettings.json.
# Keys match the platform_key strings used throughout the tool.
_PLATFORM_SETTINGS: dict[str, dict] = {
    "ios": {
        "CanonicalName": "iphoneos",
        "DisplayName": "iOS",
        "Archs": ["arm64"],
        "BuildVersionPlatformID": "2",
        "MinimumDeploymentTarget": "16.0",
        "DeviceFamilies": [
            {"Identifier": "1", "Name": "phone", "DisplayName": "iPhone"},
            {"Identifier": "2", "Name": "pad", "DisplayName": "iPad"},
        ],
        "LLVMTargetTripleVendor": "apple",
        "LLVMTargetTripleSys": "ios",
        "ClangRuntimeLibraryPlatformName": "ios",
        "DefaultProperties": {
            "PLATFORM_NAME": "iphoneos",
            "CODE_SIGN_IDENTITY": "Apple Development",
            "DEFAULT_COMPILER": "com.apple.compilers.llvm.clang.1_0",
            "ENTITLEMENTS_REQUIRED": "YES",
            "DEAD_CODE_STRIPPING": "YES",
        },
    },
    "macos": {
        "CanonicalName": "macosx",
        "DisplayName": "macOS",
        "Archs": ["arm64", "x86_64"],
        "BuildVersionPlatformID": "1",
        "MinimumDeploymentTarget": "13.0",
        "DeviceFamilies": [],
        "LLVMTargetTripleVendor": "apple",
        "LLVMTargetTripleSys": "macos",
        "ClangRuntimeLibraryPlatformName": "osx",
        "DefaultProperties": {
            "PLATFORM_NAME": "macosx",
            "CODE_SIGN_IDENTITY": "-",
            "DEFAULT_COMPILER": "com.apple.compilers.llvm.clang.1_0",
            "ENTITLEMENTS_REQUIRED": "NO",
            "DEAD_CODE_STRIPPING": "YES",
        },
    },
    "tvos": {
        "CanonicalName": "appletvos",
        "DisplayName": "tvOS",
        "Archs": ["arm64"],
        "BuildVersionPlatformID": "3",
        "MinimumDeploymentTarget": "16.0",
        "DeviceFamilies": [
            {"Identifier": "3", "Name": "tv", "DisplayName": "Apple TV"},
        ],
        "LLVMTargetTripleVendor": "apple",
        "LLVMTargetTripleSys": "tvos",
        "ClangRuntimeLibraryPlatformName": "tvos",
        "DefaultProperties": {
            "PLATFORM_NAME": "appletvos",
            "CODE_SIGN_IDENTITY": "Apple Development",
            "DEFAULT_COMPILER": "com.apple.compilers.llvm.clang.1_0",
            "ENTITLEMENTS_REQUIRED": "YES",
            "DEAD_CODE_STRIPPING": "YES",
        },
    },
    "watchos": {
        "CanonicalName": "watchos",
        "DisplayName": "watchOS",
        "Archs": ["arm64_32"],
        "BuildVersionPlatformID": "4",
        "MinimumDeploymentTarget": "9.0",
        "DeviceFamilies": [
            {"Identifier": "4", "Name": "watch", "DisplayName": "Apple Watch"},
        ],
        "LLVMTargetTripleVendor": "apple",
        "LLVMTargetTripleSys": "watchos",
        "ClangRuntimeLibraryPlatformName": "watchos",
        "DefaultProperties": {
            "PLATFORM_NAME": "watchos",
            "CODE_SIGN_IDENTITY": "Apple Development",
            "DEFAULT_COMPILER": "com.apple.compilers.llvm.clang.1_0",
            "ENTITLEMENTS_REQUIRED": "YES",
            "DEAD_CODE_STRIPPING": "YES",
        },
    },
    "visionos": {
        "CanonicalName": "xros",
        "DisplayName": "visionOS",
        "Archs": ["arm64"],
        "BuildVersionPlatformID": "11",
        "MinimumDeploymentTarget": "1.0",
        "DeviceFamilies": [
            {"Identifier": "7", "Name": "reality", "DisplayName": "Apple Vision"},
        ],
        "LLVMTargetTripleVendor": "apple",
        "LLVMTargetTripleSys": "xros",
        "ClangRuntimeLibraryPlatformName": "xros",
        "DefaultProperties": {
            "PLATFORM_NAME": "xros",
            "CODE_SIGN_IDENTITY": "Apple Development",
            "DEFAULT_COMPILER": "com.apple.compilers.llvm.clang.1_0",
            "ENTITLEMENTS_REQUIRED": "YES",
            "DEAD_CODE_STRIPPING": "YES",
        },
    },
    # ── Simulator platforms ──
    "ios-simulator": {
        "CanonicalName": "iphonesimulator",
        "DisplayName": "Simulator - iOS",
        "Archs": ["arm64", "x86_64"],
        "BuildVersionPlatformID": "7",
        "MinimumDeploymentTarget": "16.0",
        "DeviceFamilies": [
            {"Identifier": "1", "Name": "phone", "DisplayName": "iPhone"},
            {"Identifier": "2", "Name": "pad", "DisplayName": "iPad"},
        ],
        "LLVMTargetTripleVendor": "apple",
        "LLVMTargetTripleSys": "ios",
        "LLVMTargetTripleEnvironment": "simulator",
        "ClangRuntimeLibraryPlatformName": "iossim",
        "DefaultProperties": {
            "PLATFORM_NAME": "iphonesimulator",
            "CODE_SIGN_IDENTITY": "-",
            "AD_HOC_CODE_SIGNING_ALLOWED": "YES",
            "DEFAULT_COMPILER": "com.apple.compilers.llvm.clang.1_0",
            "ENTITLEMENTS_REQUIRED": "NO",
            "DEAD_CODE_STRIPPING": "YES",
        },
    },
    "tvos-simulator": {
        "CanonicalName": "appletvsimulator",
        "DisplayName": "Simulator - tvOS",
        "Archs": ["arm64", "x86_64"],
        "BuildVersionPlatformID": "8",
        "MinimumDeploymentTarget": "16.0",
        "DeviceFamilies": [
            {"Identifier": "3", "Name": "tv", "DisplayName": "Apple TV"},
        ],
        "LLVMTargetTripleVendor": "apple",
        "LLVMTargetTripleSys": "tvos",
        "LLVMTargetTripleEnvironment": "simulator",
        "ClangRuntimeLibraryPlatformName": "tvossim",
        "DefaultProperties": {
            "PLATFORM_NAME": "appletvsimulator",
            "CODE_SIGN_IDENTITY": "-",
            "AD_HOC_CODE_SIGNING_ALLOWED": "YES",
            "DEFAULT_COMPILER": "com.apple.compilers.llvm.clang.1_0",
            "ENTITLEMENTS_REQUIRED": "NO",
            "DEAD_CODE_STRIPPING": "YES",
        },
    },
    "watchos-simulator": {
        "CanonicalName": "watchsimulator",
        "DisplayName": "Simulator - watchOS",
        "Archs": ["arm64", "x86_64"],
        "BuildVersionPlatformID": "9",
        "MinimumDeploymentTarget": "9.0",
        "DeviceFamilies": [
            {"Identifier": "4", "Name": "watch", "DisplayName": "Apple Watch"},
        ],
        "LLVMTargetTripleVendor": "apple",
        "LLVMTargetTripleSys": "watchos",
        "LLVMTargetTripleEnvironment": "simulator",
        "ClangRuntimeLibraryPlatformName": "watchossim",
        "DefaultProperties": {
            "PLATFORM_NAME": "watchsimulator",
            "CODE_SIGN_IDENTITY": "-",
            "AD_HOC_CODE_SIGNING_ALLOWED": "YES",
            "DEFAULT_COMPILER": "com.apple.compilers.llvm.clang.1_0",
            "ENTITLEMENTS_REQUIRED": "NO",
            "DEAD_CODE_STRIPPING": "YES",
        },
    },
    "visionos-simulator": {
        "CanonicalName": "xrsimulator",
        "DisplayName": "Simulator - visionOS",
        "Archs": ["arm64", "x86_64"],
        "BuildVersionPlatformID": "12",
        "MinimumDeploymentTarget": "1.0",
        "DeviceFamilies": [
            {"Identifier": "7", "Name": "reality", "DisplayName": "Apple Vision"},
        ],
        "LLVMTargetTripleVendor": "apple",
        "LLVMTargetTripleSys": "xros",
        "LLVMTargetTripleEnvironment": "simulator",
        "ClangRuntimeLibraryPlatformName": "xrossim",
        "DefaultProperties": {
            "PLATFORM_NAME": "xrsimulator",
            "CODE_SIGN_IDENTITY": "-",
            "AD_HOC_CODE_SIGNING_ALLOWED": "YES",
            "DEFAULT_COMPILER": "com.apple.compilers.llvm.clang.1_0",
            "ENTITLEMENTS_REQUIRED": "NO",
            "DEAD_CODE_STRIPPING": "YES",
        },
    },
}


def _build_sdk_settings(
    platform_name: str,
    sdk_version: str,
    deployment_target: str | None = None,
    platform_key: str | None = None,
) -> dict:
    """Build the SDKSettings dictionary."""
    if deployment_target is None:
        deployment_target = sdk_version

    plat = _PLATFORM_SETTINGS.get(platform_key or "")

    if plat:
        canonical = f"{plat['CanonicalName']}{sdk_version}"
        default_props = dict(plat["DefaultProperties"])

        supported_target = {
            "Archs": plat["Archs"],
            "DefaultDeploymentTarget": deployment_target,
            "MinimumDeploymentTarget": plat["MinimumDeploymentTarget"],
            "LLVMTargetTripleVendor": plat["LLVMTargetTripleVendor"],
            "LLVMTargetTripleSys": plat["LLVMTargetTripleSys"],
        }
        if "LLVMTargetTripleEnvironment" in plat:
            supported_target["LLVMTargetTripleEnvironment"] = plat["LLVMTargetTripleEnvironment"]
        if plat["DeviceFamilies"]:
            supported_target["DeviceFamilies"] = plat["DeviceFamilies"]

        return {
            "CanonicalName": canonical,
            "DisplayName": plat["DisplayName"],
            "Version": sdk_version,
            "MaximumDeploymentTarget": sdk_version,
            "MinimalDisplayName": sdk_version,
            "IsBaseSDK": "YES",
            "DefaultProperties": default_props,
            "SupportedTargets": {
                plat["CanonicalName"]: supported_target,
            },
        }
    else:
        return {
            "CanonicalName": f"{platform_name.lower()}{sdk_version}",
            "DisplayName": platform_name,
            "Version": sdk_version,
            "MaximumDeploymentTarget": sdk_version,
            "MinimalDisplayName": sdk_version,
            "DefaultProperties": {
                "PLATFORM_NAME": platform_name.lower(),
            },
            "SupportedTargets": {
                platform_name.lower(): {
                    "DefaultDeploymentTarget": deployment_target,
                },
            },
            "IsBaseSDK": "YES",
        }


def generate_sdk_settings(
    platform_name: str,
    sdk_version: str,
    deployment_target: str | None = None,
    platform_key: str | None = None,
) -> str:
    """Generate SDKSettings.json for an SDK."""
    settings = _build_sdk_settings(
        platform_name, sdk_version, deployment_target, platform_key,
    )
    return json.dumps(settings, indent=2) + "\n"


def generate_sdk_settings_plist(
    platform_name: str,
    sdk_version: str,
    deployment_target: str | None = None,
    platform_key: str | None = None,
) -> bytes:
    """Generate SDKSettings.plist (binary plist) for an SDK."""
    settings = _build_sdk_settings(
        platform_name, sdk_version, deployment_target, platform_key,
    )
    return plistlib.dumps(settings, fmt=plistlib.FMT_XML)


def generate_info_plist(
    platform_name: str,
    sdk_version: str,
    platform_key: str | None = None,
) -> str:
    """Generate Info.plist for the platform.

    The ``Name`` key is critical: xcrun matches SDKs by this field
    (e.g. ``iphonesimulator``).
    """
    plat = _PLATFORM_SETTINGS.get(platform_key or "")
    # xcrun matches on the lowercase canonical name (e.g. "iphonesimulator")
    name = plat["CanonicalName"] if plat else platform_name.lower()
    identifier = f"com.apple.platform.{name}" if plat else ""

    default_compiler = "com.apple.compilers.llvm.clang.1_0"

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">',
        '<plist version="1.0">',
        '<dict>',
        '    <key>CFBundleName</key>',
        f'    <string>{platform_name}</string>',
        '    <key>CFBundleShortVersionString</key>',
        f'    <string>{sdk_version}</string>',
        '    <key>CFBundleVersion</key>',
        f'    <string>{sdk_version}</string>',
        # DefaultProperties — environment_plist reads DEFAULT_COMPILER here
        '    <key>DefaultProperties</key>',
        '    <dict>',
        '        <key>DEFAULT_COMPILER</key>',
        f'        <string>{default_compiler}</string>',
    ]
    if plat:
        lines += [
            '        <key>PLATFORM_NAME</key>',
            f'        <string>{plat["DefaultProperties"]["PLATFORM_NAME"]}</string>',
        ]
    lines += [
        '    </dict>',
        '    <key>Name</key>',
        f'    <string>{name}</string>',
        '    <key>Version</key>',
        f'    <string>{sdk_version}</string>',
    ]
    if identifier:
        lines += [
            '    <key>Identifier</key>',
            f'    <string>{identifier}</string>',
        ]
    lines += [
        '</dict>',
        '</plist>',
        '',
    ]
    return '\n'.join(lines)


def generate_system_version_plist(sdk_version: str) -> str:
    """Generate System/Library/CoreServices/SystemVersion.plist.

    The ported ``sw_vers`` tool reads this file to report the macOS
    version.  ``environment_plist`` (from rules_apple) invokes
    ``sw_vers --buildVersion`` so at least one SDK must contain this
    plist for cross-compilation to succeed on Linux.
    """
    return "\n".join([
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" '
        '"http://www.apple.com/DTDs/PropertyList-1.0.dtd">',
        '<plist version="1.0">',
        '<dict>',
        '    <key>ProductBuildVersion</key>',
        f'    <string>0CFFFF</string>',
        '    <key>ProductName</key>',
        '    <string>macOS</string>',
        '    <key>ProductVersion</key>',
        f'    <string>{sdk_version}</string>',
        '</dict>',
        '</plist>',
        '',
    ])


def generate_xcode_version_plist(sdk_version: str) -> str:
    """Generate Xcode.app/Contents/version.plist.

    ``environment_plist`` reads ``CFBundleShortVersionString`` and
    ``ProductBuildVersion`` from this file to populate ``DTXcode`` and
    ``DTXcodeBuild`` in the environment plist.  The version string must
    contain at least two dot-separated components so that the shell
    ``printf '%02d%d%d'`` formatting does not fail.
    """
    # Synthesise an Xcode-style version from the SDK version.
    # e.g. SDK "26.2" → Xcode "16.2" (subtract 10 from major).
    parts = sdk_version.split(".")
    major = int(parts[0]) - 10 if len(parts) >= 1 else 0
    minor = int(parts[1]) if len(parts) >= 2 else 0
    version_str = f"{major}.{minor}"

    return "\n".join([
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" '
        '"http://www.apple.com/DTDs/PropertyList-1.0.dtd">',
        '<plist version="1.0">',
        '<dict>',
        '    <key>CFBundleShortVersionString</key>',
        f'    <string>{version_str}</string>',
        '    <key>ProductBuildVersion</key>',
        '    <string>0CFFFF</string>',
        '</dict>',
        '</plist>',
        '',
    ])
