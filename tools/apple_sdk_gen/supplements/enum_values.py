"""Known enum case values for Apple frameworks.

The documentation API provides enum case names but not their numeric values.
This module provides the canonical values for the most commonly used enums
so the generated headers produce correct code.

For enums not listed here, the generator uses auto-increment (0, 1, 2, ...)
for regular enums and power-of-two (1, 2, 4, 8, ...) for NS_OPTIONS bitmasks.
"""

from __future__ import annotations

# case_name -> numeric value (as a string for direct emission)
KNOWN_ENUM_VALUES: dict[str, str] = {
    # ── Foundation: NSComparisonResult ────────────────────────────────
    "NSOrderedAscending": "-1",
    "NSOrderedSame": "0",
    "NSOrderedDescending": "1",

    # ── Foundation: NSStringEncoding ──────────────────────────────────
    "NSASCIIStringEncoding": "1",
    "NSNEXTSTEPStringEncoding": "2",
    "NSJapaneseEUCStringEncoding": "3",
    "NSUTF8StringEncoding": "4",
    "NSISOLatin1StringEncoding": "5",
    "NSSymbolStringEncoding": "6",
    "NSNonLossyASCIIStringEncoding": "7",
    "NSShiftJISStringEncoding": "8",
    "NSISOLatin2StringEncoding": "9",
    "NSUnicodeStringEncoding": "10",
    "NSWindowsCP1251StringEncoding": "11",
    "NSWindowsCP1252StringEncoding": "12",
    "NSWindowsCP1253StringEncoding": "13",
    "NSWindowsCP1254StringEncoding": "14",
    "NSWindowsCP1250StringEncoding": "15",
    "NSISO2022JPStringEncoding": "21",
    "NSMacOSRomanStringEncoding": "30",
    "NSUTF16StringEncoding": "10",
    "NSUTF16BigEndianStringEncoding": "0x90000100",
    "NSUTF16LittleEndianStringEncoding": "0x94000100",
    "NSUTF32StringEncoding": "0x8c000100",
    "NSUTF32BigEndianStringEncoding": "0x98000100",
    "NSUTF32LittleEndianStringEncoding": "0x9c000100",

    # ── Foundation: NSStringCompareOptions ────────────────────────────
    "NSCaseInsensitiveSearch": "1",
    "NSLiteralSearch": "2",
    "NSBackwardsSearch": "4",
    "NSAnchoredSearch": "8",
    "NSNumericSearch": "64",
    "NSDiacriticInsensitiveSearch": "128",
    "NSWidthInsensitiveSearch": "256",
    "NSForcedOrderingSearch": "512",
    "NSRegularExpressionSearch": "1024",

    # ── Foundation: NSURLBookmarkCreationOptions ──────────────────────
    # (bitmask – covered by OPTIONS_ENUMS fallback)

    # ── Foundation: NSCalendarUnit ────────────────────────────────────
    "NSCalendarUnitEra": "2",
    "NSCalendarUnitYear": "4",
    "NSCalendarUnitMonth": "8",
    "NSCalendarUnitDay": "16",
    "NSCalendarUnitHour": "32",
    "NSCalendarUnitMinute": "64",
    "NSCalendarUnitSecond": "128",
    "NSCalendarUnitWeekday": "512",
    "NSCalendarUnitWeekdayOrdinal": "1024",
    "NSCalendarUnitQuarter": "2048",
    "NSCalendarUnitWeekOfMonth": "4096",
    "NSCalendarUnitWeekOfYear": "8192",
    "NSCalendarUnitYearForWeekOfYear": "16384",
    "NSCalendarUnitNanosecond": "32768",
    "NSCalendarUnitCalendar": "(1 << 20)",
    "NSCalendarUnitTimeZone": "(1 << 21)",

    # ── Foundation: NSOperationQueuePriority ──────────────────────────
    "NSOperationQueuePriorityVeryLow": "-8",
    "NSOperationQueuePriorityLow": "-4",
    "NSOperationQueuePriorityNormal": "0",
    "NSOperationQueuePriorityHigh": "4",
    "NSOperationQueuePriorityVeryHigh": "8",

    # ── Foundation: NSQualityOfService ────────────────────────────────
    "NSQualityOfServiceUserInteractive": "0x21",
    "NSQualityOfServiceUserInitiated": "0x19",
    "NSQualityOfServiceUtility": "0x11",
    "NSQualityOfServiceBackground": "0x09",
    "NSQualityOfServiceDefault": "-1",

    # ── Foundation: NSURLRequestCachePolicy ───────────────────────────
    "NSURLRequestUseProtocolCachePolicy": "0",
    "NSURLRequestReloadIgnoringLocalCacheData": "1",
    "NSURLRequestReloadIgnoringLocalAndRemoteCacheData": "4",
    "NSURLRequestReturnCacheDataElseLoad": "2",
    "NSURLRequestReturnCacheDataDontLoad": "3",
    "NSURLRequestReloadRevalidatingCacheData": "5",

    # ── Foundation: NSJSONReadingOptions ──────────────────────────────
    "NSJSONReadingMutableContainers": "1",
    "NSJSONReadingMutableLeaves": "2",
    "NSJSONReadingFragmentsAllowed": "4",
    "NSJSONReadingJSON5Allowed": "8",
    "NSJSONReadingTopLevelDictionaryAssumed": "16",

    # ── Foundation: NSJSONWritingOptions ──────────────────────────────
    "NSJSONWritingPrettyPrinted": "1",
    "NSJSONWritingSortedKeys": "2",
    "NSJSONWritingFragmentsAllowed": "4",
    "NSJSONWritingWithoutEscapingSlashes": "8",

    # ── Foundation: NSDataReadingOptions ──────────────────────────────
    "NSDataReadingMappedIfSafe": "1",
    "NSDataReadingUncached": "2",
    "NSDataReadingMappedAlways": "8",

    # ── Foundation: NSPropertyListMutabilityOptions ───────────────────
    "NSPropertyListImmutable": "0",
    "NSPropertyListMutableContainers": "1",
    "NSPropertyListMutableContainersAndLeaves": "2",

    # ── Foundation: NSPropertyListFormat ──────────────────────────────
    "NSPropertyListOpenStepFormat": "1",
    "NSPropertyListXMLFormat_v1_0": "100",
    "NSPropertyListBinaryFormat_v1_0": "200",

    # ── CoreGraphics: CGBlendMode ────────────────────────────────────
    "kCGBlendModeNormal": "0",
    "kCGBlendModeMultiply": "1",
    "kCGBlendModeScreen": "2",
    "kCGBlendModeOverlay": "3",
    "kCGBlendModeDarken": "4",
    "kCGBlendModeLighten": "5",
    "kCGBlendModeColorDodge": "6",
    "kCGBlendModeColorBurn": "7",
    "kCGBlendModeSoftLight": "8",
    "kCGBlendModeHardLight": "9",
    "kCGBlendModeDifference": "10",
    "kCGBlendModeExclusion": "11",
    "kCGBlendModeHue": "12",
    "kCGBlendModeSaturation": "13",
    "kCGBlendModeColor": "14",
    "kCGBlendModeLuminosity": "15",
    "kCGBlendModeClear": "16",
    "kCGBlendModeCopy": "17",
    "kCGBlendModeSourceIn": "18",
    "kCGBlendModeSourceOut": "19",
    "kCGBlendModeSourceAtop": "20",
    "kCGBlendModeDestinationOver": "21",
    "kCGBlendModeDestinationIn": "22",
    "kCGBlendModeDestinationOut": "23",
    "kCGBlendModeDestinationAtop": "24",
    "kCGBlendModeXOR": "25",
    "kCGBlendModePlusDarker": "26",
    "kCGBlendModePlusLighter": "27",

    # ── CoreGraphics: CGLineJoin ─────────────────────────────────────
    "kCGLineJoinMiter": "0",
    "kCGLineJoinRound": "1",
    "kCGLineJoinBevel": "2",

    # ── CoreGraphics: CGLineCap ──────────────────────────────────────
    "kCGLineCapButt": "0",
    "kCGLineCapRound": "1",
    "kCGLineCapSquare": "2",

    # ── CoreGraphics: CGPathFillRule ─────────────────────────────────
    "kCGPathFillRuleWinding": "0",
    "kCGPathFillRuleEvenOdd": "1",

    # ── CoreGraphics: CGImageAlphaInfo ───────────────────────────────
    "kCGImageAlphaNone": "0",
    "kCGImageAlphaPremultipliedLast": "1",
    "kCGImageAlphaPremultipliedFirst": "2",
    "kCGImageAlphaLast": "3",
    "kCGImageAlphaFirst": "4",
    "kCGImageAlphaNoneSkipLast": "5",
    "kCGImageAlphaNoneSkipFirst": "6",
    "kCGImageAlphaOnly": "7",

    # ── CoreGraphics: CGColorRenderingIntent ─────────────────────────
    "kCGRenderingIntentDefault": "0",
    "kCGRenderingIntentAbsoluteColorimetric": "1",
    "kCGRenderingIntentRelativeColorimetric": "2",
    "kCGRenderingIntentPerceptual": "3",
    "kCGRenderingIntentSaturation": "4",

    # ── CoreGraphics: CGInterpolationQuality ─────────────────────────
    "kCGInterpolationDefault": "0",
    "kCGInterpolationNone": "1",
    "kCGInterpolationLow": "2",
    "kCGInterpolationMedium": "4",
    "kCGInterpolationHigh": "3",

    # ── CoreGraphics: CGColorSpaceModel ──────────────────────────────
    "kCGColorSpaceModelUnknown": "-1",
    "kCGColorSpaceModelMonochrome": "0",
    "kCGColorSpaceModelRGB": "1",
    "kCGColorSpaceModelCMYK": "2",
    "kCGColorSpaceModelLab": "3",
    "kCGColorSpaceModelDeviceN": "4",
    "kCGColorSpaceModelIndexed": "5",
    "kCGColorSpaceModelPattern": "6",
    "kCGColorSpaceModelXYZ": "7",

    # ── UIKit: UIViewAutoresizing ────────────────────────────────────
    "UIViewAutoresizingNone": "0",
    "UIViewAutoresizingFlexibleLeftMargin": "1",
    "UIViewAutoresizingFlexibleWidth": "2",
    "UIViewAutoresizingFlexibleRightMargin": "4",
    "UIViewAutoresizingFlexibleTopMargin": "8",
    "UIViewAutoresizingFlexibleHeight": "16",
    "UIViewAutoresizingFlexibleBottomMargin": "32",

    # ── UIKit: UIViewContentMode ─────────────────────────────────────
    "UIViewContentModeScaleToFill": "0",
    "UIViewContentModeScaleAspectFit": "1",
    "UIViewContentModeScaleAspectFill": "2",
    "UIViewContentModeRedraw": "3",
    "UIViewContentModeCenter": "4",
    "UIViewContentModeTop": "5",
    "UIViewContentModeBottom": "6",
    "UIViewContentModeLeft": "7",
    "UIViewContentModeRight": "8",
    "UIViewContentModeTopLeft": "9",
    "UIViewContentModeTopRight": "10",
    "UIViewContentModeBottomLeft": "11",
    "UIViewContentModeBottomRight": "12",

    # ── UIKit: UIControlState ────────────────────────────────────────
    "UIControlStateNormal": "0",
    "UIControlStateHighlighted": "1",
    "UIControlStateDisabled": "2",
    "UIControlStateSelected": "4",
    "UIControlStateFocused": "8",

    # ── UIKit: UIControlEvents ───────────────────────────────────────
    "UIControlEventTouchDown": "1",
    "UIControlEventTouchDownRepeat": "2",
    "UIControlEventTouchDragInside": "4",
    "UIControlEventTouchDragOutside": "8",
    "UIControlEventTouchDragEnter": "16",
    "UIControlEventTouchDragExit": "32",
    "UIControlEventTouchUpInside": "64",
    "UIControlEventTouchUpOutside": "128",
    "UIControlEventTouchCancel": "256",
    "UIControlEventValueChanged": "4096",
    "UIControlEventPrimaryActionTriggered": "8192",
    "UIControlEventEditingDidBegin": "65536",
    "UIControlEventEditingChanged": "131072",
    "UIControlEventEditingDidEnd": "262144",
    "UIControlEventEditingDidEndOnExit": "524288",
    "UIControlEventAllTouchEvents": "0x00000FFF",
    "UIControlEventAllEditingEvents": "0x000F0000",
    "UIControlEventAllEvents": "0xFFFFFFFF",

    # ── UIKit: UITextAutocapitalizationType ───────────────────────────
    "UITextAutocapitalizationTypeNone": "0",
    "UITextAutocapitalizationTypeWords": "1",
    "UITextAutocapitalizationTypeSentences": "2",
    "UITextAutocapitalizationTypeAllCharacters": "3",

    # ── UIKit: UITableViewStyle ──────────────────────────────────────
    "UITableViewStylePlain": "0",
    "UITableViewStyleGrouped": "1",
    "UITableViewStyleInsetGrouped": "2",

    # ── UIKit: UITableViewCellStyle ──────────────────────────────────
    "UITableViewCellStyleDefault": "0",
    "UITableViewCellStyleValue1": "1",
    "UITableViewCellStyleValue2": "2",
    "UITableViewCellStyleSubtitle": "3",

    # ── UIKit: UITableViewCellAccessoryType ──────────────────────────
    "UITableViewCellAccessoryNone": "0",
    "UITableViewCellAccessoryDisclosureIndicator": "1",
    "UITableViewCellAccessoryDetailDisclosureButton": "2",
    "UITableViewCellAccessoryCheckmark": "3",
    "UITableViewCellAccessoryDetailButton": "4",

    # ── UIKit: UITableViewCellSelectionStyle ─────────────────────────
    "UITableViewCellSelectionStyleNone": "0",
    "UITableViewCellSelectionStyleBlue": "1",
    "UITableViewCellSelectionStyleGray": "2",
    "UITableViewCellSelectionStyleDefault": "3",

    # ── UIKit: UIStatusBarStyle ──────────────────────────────────────
    "UIStatusBarStyleDefault": "0",
    "UIStatusBarStyleLightContent": "1",
    "UIStatusBarStyleDarkContent": "3",

    # ── UIKit: UIInterfaceOrientation ────────────────────────────────
    "UIInterfaceOrientationUnknown": "0",
    "UIInterfaceOrientationPortrait": "1",
    "UIInterfaceOrientationPortraitUpsideDown": "2",
    "UIInterfaceOrientationLandscapeLeft": "4",
    "UIInterfaceOrientationLandscapeRight": "3",

    # ── UIKit: UIUserInterfaceStyle ──────────────────────────────────
    "UIUserInterfaceStyleUnspecified": "0",
    "UIUserInterfaceStyleLight": "1",
    "UIUserInterfaceStyleDark": "2",

    # ── UIKit: UIModalPresentationStyle ──────────────────────────────
    "UIModalPresentationStyleFullScreen": "0",
    "UIModalPresentationStylePageSheet": "1",
    "UIModalPresentationStyleFormSheet": "2",
    "UIModalPresentationStyleCurrentContext": "3",
    "UIModalPresentationStyleCustom": "4",
    "UIModalPresentationStyleOverFullScreen": "5",
    "UIModalPresentationStyleOverCurrentContext": "6",
    "UIModalPresentationStylePopover": "7",
    "UIModalPresentationStyleAutomatic": "-2",

    # ── UIKit: UIModalTransitionStyle ────────────────────────────────
    "UIModalTransitionStyleCoverVertical": "0",
    "UIModalTransitionStyleFlipHorizontal": "1",
    "UIModalTransitionStyleCrossDissolve": "2",
    "UIModalTransitionStylePartialCurl": "3",

    # ── UIKit: UITextFieldViewMode ───────────────────────────────────
    "UITextFieldViewModeNever": "0",
    "UITextFieldViewModeWhileEditing": "1",
    "UITextFieldViewModeUnlessEditing": "2",
    "UITextFieldViewModeAlways": "3",

    # ── UIKit: UILayoutConstraintAxis ────────────────────────────────
    "UILayoutConstraintAxisHorizontal": "0",
    "UILayoutConstraintAxisVertical": "1",

    # ── UIKit: NSLayoutRelation ──────────────────────────────────────
    "NSLayoutRelationLessThanOrEqual": "-1",
    "NSLayoutRelationEqual": "0",
    "NSLayoutRelationGreaterThanOrEqual": "1",

    # ── UIKit: NSLayoutAttribute ─────────────────────────────────────
    "NSLayoutAttributeLeft": "1",
    "NSLayoutAttributeRight": "2",
    "NSLayoutAttributeTop": "3",
    "NSLayoutAttributeBottom": "4",
    "NSLayoutAttributeLeading": "5",
    "NSLayoutAttributeTrailing": "6",
    "NSLayoutAttributeWidth": "7",
    "NSLayoutAttributeHeight": "8",
    "NSLayoutAttributeCenterX": "9",
    "NSLayoutAttributeCenterY": "10",
    "NSLayoutAttributeLastBaseline": "11",
    "NSLayoutAttributeFirstBaseline": "12",
    "NSLayoutAttributeNotAnAttribute": "0",

    # ── UIKit: UIStackViewAlignment ──────────────────────────────────
    "UIStackViewAlignmentFill": "0",
    "UIStackViewAlignmentLeading": "1",
    "UIStackViewAlignmentTop": "1",
    "UIStackViewAlignmentFirstBaseline": "2",
    "UIStackViewAlignmentCenter": "3",
    "UIStackViewAlignmentTrailing": "4",
    "UIStackViewAlignmentBottom": "4",
    "UIStackViewAlignmentLastBaseline": "5",

    # ── UIKit: UIStackViewDistribution ───────────────────────────────
    "UIStackViewDistributionFill": "0",
    "UIStackViewDistributionFillEqually": "1",
    "UIStackViewDistributionFillProportionally": "2",
    "UIStackViewDistributionEqualSpacing": "3",
    "UIStackViewDistributionEqualCentering": "4",

    # ── CoreMedia: CMTimeFlags ───────────────────────────────────────
    "kCMTimeFlags_Valid": "1",
    "kCMTimeFlags_HasBeenRounded": "2",
    "kCMTimeFlags_PositiveInfinity": "4",
    "kCMTimeFlags_NegativeInfinity": "8",
    "kCMTimeFlags_Indefinite": "16",
    "kCMTimeFlags_ImpliedValueFlagsMask": "28",

    # ── CoreAnimation: CAEdgeAntialiasingMask ────────────────────────
    "kCALayerLeftEdge": "1",
    "kCALayerRightEdge": "2",
    "kCALayerBottomEdge": "4",
    "kCALayerTopEdge": "8",
}

# Enum names that use NS_OPTIONS (bitmask) semantics.
# For unlisted cases, the generator falls back to power-of-two assignment.
OPTIONS_ENUMS: set[str] = {
    "NSStringCompareOptions",
    "NSCalendarUnit",
    "NSDataReadingOptions",
    "NSJSONReadingOptions",
    "NSJSONWritingOptions",
    "UIViewAutoresizing",
    "UIControlState",
    "UIControlEvents",
    "NSKeyValueObservingOptions",
    "NSDirectionalRectEdge",
    "NSRectEdge",
    "UISwipeGestureRecognizerDirection",
    "UIInterfaceOrientationMask",
    "CMTimeFlags",
    "CAEdgeAntialiasingMask",
    "UIDataDetectorTypes",
    "UIAccessibilityTraits",
    "NSLayoutFormatOptions",
    "CGBitmapInfo",
    "CGEventFlags",
    "CGImageByteOrderInfo",
}


def get_case_value(case_name: str) -> str | None:
    """Look up the numeric value for a known enum case."""
    return KNOWN_ENUM_VALUES.get(case_name)


def is_options_enum(enum_name: str) -> bool:
    """Check whether an enum uses NS_OPTIONS bitmask semantics."""
    return enum_name in OPTIONS_ENUMS
