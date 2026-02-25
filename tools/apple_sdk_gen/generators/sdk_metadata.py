from __future__ import annotations

import json


def generate_sdk_settings(
    platform_name: str,
    sdk_version: str,
    deployment_target: str | None = None,
) -> str:
    """Generate SDKSettings.json for an SDK."""
    if deployment_target is None:
        deployment_target = sdk_version

    settings = {
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

    return json.dumps(settings, indent=2) + "\n"


def generate_info_plist(
    platform_name: str,
    sdk_version: str,
) -> str:
    """Generate a minimal Info.plist for the platform."""
    return f"""\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>{platform_name}</string>
    <key>CFBundleShortVersionString</key>
    <string>{sdk_version}</string>
    <key>CFBundleVersion</key>
    <string>{sdk_version}</string>
</dict>
</plist>
"""
