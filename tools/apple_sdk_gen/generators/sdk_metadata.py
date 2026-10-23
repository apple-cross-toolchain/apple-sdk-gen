from __future__ import annotations

import json
import plistlib

from ..config import PLATFORM_CONFIGS

DEFAULT_COMPILER = "com.apple.compilers.llvm.clang.1_0"

_PHONE = {"Identifier": "1", "Name": "phone", "DisplayName": "iPhone"}
_PAD = {"Identifier": "2", "Name": "pad", "DisplayName": "iPad"}
_TV = {"Identifier": "3", "Name": "tv", "DisplayName": "Apple TV"}
_WATCH = {"Identifier": "4", "Name": "watch", "DisplayName": "Apple Watch"}
_MAC = {"Name": "mac", "DisplayName": "Mac"}
_VISION = {"Identifier": "7", "Name": "vision", "DisplayName": "Apple Vision"}

_DEVICES = {
    "ios": {
        "name": "iphoneos",
        "family": "iphoneos",
        "family_name": "iOS",
        "display": "iOS",
        "product": "iPhone OS",
        "sys": "ios",
        "runtime": "ios",
        "build_id": "2",
        "minimum": "15.0",
        "families": [_PHONE, _PAD],
    },
    "macos": {
        "name": "macosx",
        "family": "macosx",
        "family_name": "macOS",
        "display": "macOS",
        "product": "macOS",
        "sys": "macos",
        "runtime": "osx",
        "build_id": "1",
        "minimum": "12.0",
        "families": [_MAC],
    },
    "tvos": {
        "name": "appletvos",
        "family": "appletvos",
        "family_name": "tvOS",
        "display": "tvOS",
        "product": "Apple TVOS",
        "sys": "tvos",
        "runtime": "tvos",
        "build_id": "3",
        "minimum": "15.0",
        "families": [_TV],
    },
    "watchos": {
        "name": "watchos",
        "family": "watchos",
        "family_name": "watchOS",
        "display": "watchOS",
        "product": "Watch OS",
        "sys": "watchos",
        "runtime": "watchos",
        "build_id": "4",
        "minimum": "9.0",
        "families": [_WATCH],
    },
    "visionos": {
        "name": "xros",
        "family": "xros",
        "family_name": "xrOS",
        "display": "visionOS",
        "product": "xrOS",
        "sys": "xros",
        "runtime": "xros",
        "build_id": "11",
        "minimum": "1.0",
        "families": [_VISION],
    },
}

_SIMULATORS = {
    "ios-simulator": ("ios", "iphonesimulator", "iossim", "7"),
    "tvos-simulator": ("tvos", "appletvsimulator", "tvossim", "8"),
    "watchos-simulator": ("watchos", "watchsimulator", "watchossim", "9"),
    "visionos-simulator": ("visionos", "xrsimulator", "xrossim", "12"),
}

PLATFORMS = {key: dict(value, env="") for key, value in _DEVICES.items()}
for _key, (_device, _name, _runtime, _build_id) in _SIMULATORS.items():
    PLATFORMS[_key] = dict(
        _DEVICES[_device],
        name=_name,
        env="simulator",
        runtime=_runtime,
        build_id=_build_id,
        display="Simulator - " + _DEVICES[_device]["display"],
    )

_VISIONOS_VERSIONS = [
    ("17.1", "1.0"),
    ("17.4", "1.1"),
    ("17.5", "1.2"),
    ("18.0", "2.0"),
    ("18.1", "2.1"),
    ("18.2", "2.2"),
    ("18.3", "2.3"),
    ("18.4", "2.4"),
    ("18.5", "2.5"),
    ("18.6", "2.6"),
]


def default_xcode_version(sdk_version: str) -> str:
    major, _, minor = sdk_version.partition(".")
    if int(major) >= 26:
        return sdk_version
    return "{}.{}".format(int(major) - 10, minor or "0")


def default_xcode_build(xcode_version: str) -> str:
    return xcode_version.split(".")[0] + "A0"


def _archs(platform_key: str) -> list[str]:
    return [triple.split("-")[0] for triple in PLATFORM_CONFIGS[platform_key].target_triples]


def _version_map(platform_key: str, sdk_version: str) -> dict:
    if PLATFORMS[platform_key]["sys"] != "xros":
        return {}
    pairs = list(_VISIONOS_VERSIONS)
    for major in range(26, int(sdk_version.split(".")[0]) + 1):
        pairs.append(("{}.0".format(major), "{}.0".format(major)))
    pairs.append((sdk_version, sdk_version))
    forward = {ios: xros for ios, xros in pairs}
    backward = {xros: ios for ios, xros in pairs}
    return {
        "VersionMap": {
            "iOS_visionOS": forward,
            "iOS_xrOS": forward,
            "visionOS_iOS": backward,
            "xrOS_iOS": backward,
        },
    }


def _default_properties(platform_key: str) -> dict[str, str]:
    platform = PLATFORMS[platform_key]
    properties = {
        "DEAD_CODE_STRIPPING": "YES",
        "DEFAULT_COMPILER": DEFAULT_COMPILER,
        "PLATFORM_NAME": platform["name"],
    }
    if platform["env"] or platform["sys"] == "macos":
        properties.update({"CODE_SIGN_IDENTITY": "-", "ENTITLEMENTS_REQUIRED": "NO"})
    else:
        properties.update({"CODE_SIGN_IDENTITY": "Apple Development", "ENTITLEMENTS_REQUIRED": "YES"})
    if platform["env"]:
        properties["AD_HOC_CODE_SIGNING_ALLOWED"] = "YES"
    return properties


def sdk_settings(platform_key: str, sdk_version: str) -> dict:
    platform = PLATFORMS[platform_key]
    target = {
        "Archs": _archs(platform_key),
        "BuildVersionPlatformID": platform["build_id"],
        "ClangRuntimeLibraryPlatformName": platform["runtime"],
        "DefaultDeploymentTarget": sdk_version,
        "DeviceFamilies": platform["families"],
        "LLVMTargetTripleEnvironment": platform["env"],
        "LLVMTargetTripleSys": platform["sys"],
        "LLVMTargetTripleVendor": "apple",
        "MaximumDeploymentTarget": sdk_version + ".99",
        "MinimumDeploymentTarget": platform["minimum"],
        "PlatformFamilyName": platform["family_name"],
        "SystemPrefix": "",
    }
    return dict(_version_map(platform_key, sdk_version), **{
        "CanonicalName": platform["name"] + sdk_version,
        "CustomProperties": {},
        "DefaultDeploymentTarget": sdk_version,
        "DefaultProperties": _default_properties(platform_key),
        "DisplayName": "{} {}".format(platform["display"], sdk_version),
        "IsBaseSDK": "YES",
        "MaximumDeploymentTarget": sdk_version + ".99",
        "MinimalDisplayName": sdk_version,
        "SupportedTargets": {platform["name"]: target},
        "Version": sdk_version,
    })


def generate_sdk_settings(platform_key: str, sdk_version: str) -> str:
    return json.dumps(sdk_settings(platform_key, sdk_version), indent=2, sort_keys=True) + "\n"


def generate_sdk_settings_plist(platform_key: str, sdk_version: str) -> bytes:
    return plistlib.dumps(sdk_settings(platform_key, sdk_version), sort_keys=True)


def generate_info_plist(platform_key: str, sdk_version: str) -> bytes:
    platform = PLATFORMS[platform_key]
    sdk_prefix = PLATFORM_CONFIGS[platform_key].sdk_prefix
    return plistlib.dumps({
        "AdditionalInfo": {
            "CFBundleSupportedPlatforms": [sdk_prefix],
            "DTPlatformName": platform["name"],
            "DTPlatformVersion": sdk_version,
        },
        "CFBundleIdentifier": "com.apple.platform." + platform["name"],
        "CFBundleName": sdk_prefix,
        "CFBundleShortVersionString": sdk_version,
        "CFBundleVersion": sdk_version,
        "DefaultProperties": {
            "DEFAULT_COMPILER": DEFAULT_COMPILER,
            "PLATFORM_NAME": platform["name"],
        },
        "Description": platform["family_name"] + (" Simulator" if platform["env"] else ""),
        "FamilyIdentifier": platform["family"],
        "FamilyName": platform["family_name"],
        "Identifier": "com.apple.platform." + platform["name"],
        "Name": platform["name"],
        "Type": "Platform",
        "Version": sdk_version,
    }, sort_keys=True)


def generate_system_version_plist(platform_key: str, sdk_version: str, build: str) -> bytes:
    return plistlib.dumps({
        "ProductBuildVersion": build,
        "ProductName": PLATFORMS[platform_key]["product"],
        "ProductVersion": sdk_version,
    }, sort_keys=True)


def generate_xcode_version_plist(xcode_version: str, xcode_build: str) -> bytes:
    return plistlib.dumps({
        "CFBundleShortVersionString": xcode_version,
        "CFBundleVersion": xcode_version,
        "ProductBuildVersion": xcode_build,
    }, sort_keys=True)
