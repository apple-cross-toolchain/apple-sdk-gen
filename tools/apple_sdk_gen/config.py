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
    # ── Simulator platforms ──
    "ios-simulator": PlatformConfig(
        name=PlatformName.IOS,
        sdk_prefix="iPhoneSimulator",
        platform_dir="iPhoneSimulator.platform",
        target_triples=["arm64-apple-ios-simulator", "x86_64-apple-ios-simulator"],
        swift_triples=["arm64-apple-ios-simulator", "x86_64-apple-ios-simulator"],
    ),
    "tvos-simulator": PlatformConfig(
        name=PlatformName.TVOS,
        sdk_prefix="AppleTVSimulator",
        platform_dir="AppleTVSimulator.platform",
        target_triples=["arm64-apple-tvos-simulator", "x86_64-apple-tvos-simulator"],
        swift_triples=["arm64-apple-tvos-simulator", "x86_64-apple-tvos-simulator"],
    ),
    "watchos-simulator": PlatformConfig(
        name=PlatformName.WATCHOS,
        sdk_prefix="WatchSimulator",
        platform_dir="WatchSimulator.platform",
        target_triples=["arm64-apple-watchos-simulator", "x86_64-apple-watchos-simulator"],
        swift_triples=["arm64-apple-watchos-simulator", "x86_64-apple-watchos-simulator"],
    ),
    "visionos-simulator": PlatformConfig(
        name=PlatformName.VISIONOS,
        sdk_prefix="XRSimulator",
        platform_dir="XRSimulator.platform",
        target_triples=["arm64-apple-xros-simulator", "x86_64-apple-xros-simulator"],
        swift_triples=["arm64-apple-xros-simulator", "x86_64-apple-xros-simulator"],
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
        "ios-simulator": "ios-simulator",
        "tvos-simulator": "tvos-simulator",
        "watchos-simulator": "watchos-simulator",
        "visionos-simulator": "xros-simulator",
    }.get(platform_key, platform_key)

    targets = []
    for triple in cfg.target_triples:
        arch = triple.split("-")[0]
        targets.append(f"{arch}-{os_name}")
    return targets


# Module names from the documentation API that are NOT real .framework
# bundles in any Apple SDK.  These are REST APIs, web JS libraries,
# documentation topics, Swift stdlib modules, or system dylibs.
NON_FRAMEWORK_MODULES: set[str] = {
    # ── REST APIs and web services ──
    "AdvancedCommerceAPI",
    "AppleMapsServerAPI",
    "AppleMusicAPI",
    "AppleMusicFeed",
    "AppleNews",
    "ApplePayMerchantTokenUsageInformation",
    "ApplePayontheWeb",
    "ApplePayWebMerchantRegistrationAPI",
    "AppLicenseDeliverySDK",
    "AppStoreConnectAPI",
    "AppStoreReceipts",
    "AppStoreServerAPI",
    "AppStoreServerNotifications",
    "AutomaticSignInAPI",
    "ClassKitCatalogAPI",
    "EnterpriseProgramAPI",
    "ExternalPurchaseServerAPI",
    "iWorkDocumentExportingAPI",
    "MerchantTokenNotificationServices",
    "NotaryAPI",
    "RetentionMessaging",
    "RosterAPI",
    "SigninwithApple",
    "SKAdNetworkforWebAds",
    "WeatherKitRESTAPI",
    # ── JavaScript / web libraries ──
    "CKToolJS",
    "CloudKitJS",
    "LivePhotosKitJS",
    "MapKitJS",
    "tvmljs",
    "webkitjs",
    # ── Documentation / meta topics ──
    "BundleResources",
    "SampleCode",
    "Snapshots",
    "TechnologyOverviews",
    "Updates",
    "SiriEventSuggestionsMarkup",
    # ── Miscellaneous non-SDK documentation ──
    "apple_ads",
    "professional_video_applications",
    "quicktime-file-format",
    # ── Swift stdlib modules (not .framework bundles) ──
    "Distributed",
    "ObjectiveC",
    "Observation",
    "PackageDescription",
    "RegexBuilder",
    "Swift",
    "Synchronization",
    "System",
    "Testing",
    # ── System libraries (dylibs, not .framework) ──
    "Compression",
    "DarwinNotify",
    "Dispatch",
    "dnssd",
    "os",
    "XPC",
    # ── Playground-specific ──
    "playgroundbluetooth",
    "playgroundsupport",
    # ── Low-level / kernel documentation ──
    "applicationservices",
    "kernel",
    # ── Other non-framework topics ──
    "AccessoryNotifications",
    "AccountDataTransfer",
    "AccountOrganizationalDataSharing",
    "AppDataTransfer",
    "ApplePencil",
    "SiriKitCloudMedia",
    "watchOS-Apps",
    "DeviceManagement",
}

# Framework name mappings: documentation API name → real .framework name.
# Applied at SDK assembly time so the generated bundle uses the correct name.
FRAMEWORK_NAME_MAPPINGS: dict[str, str] = {
    "PhotoKit": "Photos",
    "iokit": "IOKit",
    "coreservices": "CoreServices",
    "SiriKit": "Intents",
}

# Companion frameworks: when a main framework is assembled, also emit
# TBD-only stubs for its companions (no doc API entry of their own).
COMPANION_FRAMEWORKS: dict[str, list[str]] = {
    "Intents": ["IntentsUI"],
    "Photos": ["PhotosUI"],
    "IdentityLookup": ["IdentityLookupUI"],
    "SharedWithYou": ["SharedWithYouCore"],
}

# Frameworks with no doc API entry that need TBD-only stubs for linking.
SUPPLEMENTARY_FRAMEWORKS: list[str] = [
    "MobileCoreServices",   # Deprecated, re-exports CoreServices
    "OpenAL",               # Deprecated audio API
    "BusinessChat",         # Deprecated
    "Twitter",              # Deprecated
    "CoreMediaIO",          # Camera extensions (iOS 17+)
    "HealthKitUI",          # iOS 8+, in doc API but not in technologies listing
    "MetalPerformancePrimitives",  # arm64e-only, no doc entry
    "RealityFoundation",    # Swift-only, no doc entry
    "SecurityUI",           # No doc entry
    "StickerFoundation",    # arm64e-only, no doc entry
    "StickerKit",           # No doc entry
    "SwiftUICore",          # Swift-only, no doc entry
]

# Private underscore overlay frameworks needed for SwiftUI integration
# at link time.  These get TBD-only stubs (no headers / modulemaps).
SWIFT_OVERLAY_FRAMEWORKS: list[str] = [
    "_AdAttributionKit_StoreKit",
    "_AppIntents_SwiftUI",
    "_AppIntents_UIKit",
    "_AuthenticationServices_SwiftUI",
    "_AVKit_SwiftUI",
    "_CoreData_CloudKit",
    "_CoreLocationUI_SwiftUI",
    "_CoreNFC_UIKit",
    "_DeviceActivity_SwiftUI",
    "_DeviceDiscoveryUI_SwiftUI",
    "_GameController_SwiftUI",
    "_GeoToolbox_AppIntents",
    "_GroupActivities_UIKit",
    "_HomeKit_SwiftUI",
    "_Intents_TipKit",
    "_LocationEssentials",
    "_ManagedAppDistribution_SwiftUI",
    "_MapKit_SwiftUI",
    "_MarketplaceKit_UIKit",
    "_MusicKit_SwiftUI",
    "_PassKit_SwiftUI",
    "_PermissionKit_SwiftUI",
    "_PermissionKit_UIKit",
    "_Photos_AppIntents",
    "_PhotosUI_SwiftUI",
    "_PhotosUI_WidgetKit",
    "_QuickLook_SwiftUI",
    "_RealityKit_SwiftUI",
    "_RelevanceKit_MapKit",
    "_SceneKit_SwiftUI",
    "_SecureElementCredential_SwiftUI",
    "_SecureElementCredential_UIKit",
    "_SpriteKit_SwiftUI",
    "_StoreKit_SwiftUI",
    "_SwiftData_CoreData",
    "_SwiftData_SwiftUI",
    "_Translation_SwiftUI",
    "_WebKit_SwiftUI",
    "_WorkoutKit_SwiftUI",
]

# Per-platform framework exclusions.  These ARE real .framework bundles
# but only on certain platforms — e.g. AppKit exists on macOS, not iOS.
PLATFORM_EXCLUDED_MODULES: dict[str, set[str]] = {
    "ios": {
        # macOS-only
        "AppKit", "Quartz",
        # DriverKit (macOS system extensions)
        "AudioDriverKit", "BlockStorageDeviceDriverKit", "DriverKit",
        "HIDDriverKit", "MIDIDriverKit", "NetworkingDriverKit",
        "PCIDriverKit", "SCSIControllerDriverKit",
        "SCSIPeripheralsDriverKit", "SerialDriverKit",
        "USBDriverKit", "USBSerialDriverKit",
        # Developer tools (not in device SDKs)
        "Xcode", "XCTest", "XCUIAutomation",
        # watchOS-only
        "WatchKit",
        # macOS-only or not a .framework on iOS
        "ShaderGraph", "EndpointSecurity", "MediaExtension",
        "ServiceManagement", "Spatial", "StoreKitTest",
        "WalletOrders", "WalletPasses",
        # dylib, not a .framework (usr/lib/libAppleArchive.tbd)
        "AppleArchive",
    },
    "watchos": {
        "AppKit", "Quartz", "UIKit", "IOKit", "CoreServices",
        "AudioDriverKit", "BlockStorageDeviceDriverKit", "DriverKit",
        "HIDDriverKit", "MIDIDriverKit", "NetworkingDriverKit",
        "PCIDriverKit", "SCSIControllerDriverKit",
        "SCSIPeripheralsDriverKit", "SerialDriverKit",
        "USBDriverKit", "USBSerialDriverKit",
        "Xcode", "XCTest", "XCUIAutomation",
    },
    "tvos": {
        "AppKit", "Quartz", "WatchKit", "IOKit", "CoreServices",
        "AudioDriverKit", "BlockStorageDeviceDriverKit", "DriverKit",
        "HIDDriverKit", "MIDIDriverKit", "NetworkingDriverKit",
        "PCIDriverKit", "SCSIControllerDriverKit",
        "SCSIPeripheralsDriverKit", "SerialDriverKit",
        "USBDriverKit", "USBSerialDriverKit",
        "Xcode", "XCTest", "XCUIAutomation",
    },
}

# Simulator-only exclusions (hardware-only frameworks not in simulator SDKs)
_SIM_ONLY_EXCLUDED: set[str] = {
    "CoreMediaIO", "DockKit", "ThreadNetwork",
    "StickerFoundation", "StickerKit",
}
PLATFORM_EXCLUDED_MODULES["ios-simulator"] = PLATFORM_EXCLUDED_MODULES["ios"] | _SIM_ONLY_EXCLUDED
PLATFORM_EXCLUDED_MODULES["tvos-simulator"] = PLATFORM_EXCLUDED_MODULES["tvos"]
PLATFORM_EXCLUDED_MODULES["watchos-simulator"] = PLATFORM_EXCLUDED_MODULES["watchos"]
PLATFORM_EXCLUDED_MODULES["visionos-simulator"] = set()


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
