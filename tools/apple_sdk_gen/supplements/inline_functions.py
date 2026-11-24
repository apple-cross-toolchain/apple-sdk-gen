"""Hand-written C bodies for well-known inline functions.

The Apple documentation API exposes these as function declarations without
bodies, causing link errors when code calls e.g. CGPointMake().  We provide
the canonical implementations so the generated headers are self-contained.
"""

from __future__ import annotations

# The installed arm64 and x86_64 CoreGraphics dylibs export the other
# geometry and affine-transform functions. Bind to those implementations.
CORE_GRAPHICS_INLINE_FUNCTIONS = {
    # ── CoreGraphics: CGGeometry ──────────────────────────────────────
    "CGPointMake": """\
CG_INLINE CGPoint CGPointMake(CGFloat x, CGFloat y) {
  CGPoint p; p.x = x; p.y = y; return p;
}""",
    "CGSizeMake": """\
CG_INLINE CGSize CGSizeMake(CGFloat width, CGFloat height) {
  CGSize s; s.width = width; s.height = height; return s;
}""",
    "CGRectMake": """\
CG_INLINE CGRect CGRectMake(CGFloat x, CGFloat y, CGFloat width, CGFloat height) {
  CGRect r; r.origin.x = x; r.origin.y = y; r.size.width = width; r.size.height = height; return r;
}""",
    "CGVectorMake": """\
CG_INLINE CGVector CGVectorMake(CGFloat dx, CGFloat dy) {
  CGVector v; v.dx = dx; v.dy = dy; return v;
}""",
}

# Maps the C function name to its complete definition (including the
# opening brace through the closing brace).  The generator replaces the
# bare declaration with this text verbatim.

INLINE_FUNCTIONS: dict[str, str] = {
    **CORE_GRAPHICS_INLINE_FUNCTIONS,

    # ── Foundation: NSRange ───────────────────────────────────────────
    "NSMakeRange": """\
NS_INLINE NSRange NSMakeRange(NSUInteger loc, NSUInteger len) {
  NSRange r; r.location = loc; r.length = len; return r;
}""",
    "NSMaxRange": """\
NS_INLINE NSUInteger NSMaxRange(NSRange range) {
  return range.location + range.length;
}""",
    "NSLocationInRange": """\
NS_INLINE BOOL NSLocationInRange(NSUInteger loc, NSRange range) {
  return (loc >= range.location) && (loc - range.location < range.length);
}""",
    "NSEqualRanges": """\
NS_INLINE BOOL NSEqualRanges(NSRange range1, NSRange range2) {
  return range1.location == range2.location && range1.length == range2.length;
}""",

    # ── Foundation: NSPoint / NSSize / NSRect (macOS) ─────────────────
    "NSMakePoint": """\
NS_INLINE NSPoint NSMakePoint(CGFloat x, CGFloat y) {
  NSPoint p; p.x = x; p.y = y; return p;
}""",
    "NSMakeSize": """\
NS_INLINE NSSize NSMakeSize(CGFloat w, CGFloat h) {
  NSSize s; s.width = w; s.height = h; return s;
}""",
    "NSMakeRect": """\
NS_INLINE NSRect NSMakeRect(CGFloat x, CGFloat y, CGFloat w, CGFloat h) {
  NSRect r; r.origin.x = x; r.origin.y = y; r.size.width = w; r.size.height = h; return r;
}""",
    "NSMaxX": """\
NS_INLINE CGFloat NSMaxX(NSRect aRect) {
  return aRect.origin.x + aRect.size.width;
}""",
    "NSMaxY": """\
NS_INLINE CGFloat NSMaxY(NSRect aRect) {
  return aRect.origin.y + aRect.size.height;
}""",
    "NSMidX": """\
NS_INLINE CGFloat NSMidX(NSRect aRect) {
  return aRect.origin.x + aRect.size.width / 2.0;
}""",
    "NSMidY": """\
NS_INLINE CGFloat NSMidY(NSRect aRect) {
  return aRect.origin.y + aRect.size.height / 2.0;
}""",
    "NSMinX": """\
NS_INLINE CGFloat NSMinX(NSRect aRect) {
  return aRect.origin.x;
}""",
    "NSMinY": """\
NS_INLINE CGFloat NSMinY(NSRect aRect) {
  return aRect.origin.y;
}""",
    "NSWidth": """\
NS_INLINE CGFloat NSWidth(NSRect aRect) {
  return aRect.size.width;
}""",
    "NSHeight": """\
NS_INLINE CGFloat NSHeight(NSRect aRect) {
  return aRect.size.height;
}""",
    "NSPointInRect": """\
NS_INLINE BOOL NSPointInRect(NSPoint aPoint, NSRect aRect) {
  return (aPoint.x >= aRect.origin.x && aPoint.x < NSMaxX(aRect) &&
          aPoint.y >= aRect.origin.y && aPoint.y < NSMaxY(aRect));
}""",
    "NSEqualPoints": """\
NS_INLINE BOOL NSEqualPoints(NSPoint aPoint, NSPoint bPoint) {
  return aPoint.x == bPoint.x && aPoint.y == bPoint.y;
}""",
    "NSEqualSizes": """\
NS_INLINE BOOL NSEqualSizes(NSSize aSize, NSSize bSize) {
  return aSize.width == bSize.width && aSize.height == bSize.height;
}""",
    "NSEqualRects": """\
NS_INLINE BOOL NSEqualRects(NSRect aRect, NSRect bRect) {
  return NSEqualPoints(aRect.origin, bRect.origin) && NSEqualSizes(aRect.size, bRect.size);
}""",
    "NSIsEmptyRect": """\
NS_INLINE BOOL NSIsEmptyRect(NSRect aRect) {
  return aRect.size.width <= 0 || aRect.size.height <= 0;
}""",

    # ── CoreFoundation: CFRange ───────────────────────────────────────
    "CFRangeMake": """\
CF_INLINE CFRange CFRangeMake(CFIndex loc, CFIndex len) {
  CFRange range; range.location = loc; range.length = len; return range;
}""",

    # ── UIKit: UIEdgeInsets / UIOffset ────────────────────────────────
    "UIEdgeInsetsMake": """\
NS_INLINE UIEdgeInsets UIEdgeInsetsMake(CGFloat top, CGFloat left, CGFloat bottom, CGFloat right) {
  UIEdgeInsets insets; insets.top = top; insets.left = left; insets.bottom = bottom; insets.right = right; return insets;
}""",
    "UIEdgeInsetsEqualToEdgeInsets": """\
NS_INLINE BOOL UIEdgeInsetsEqualToEdgeInsets(UIEdgeInsets insets1, UIEdgeInsets insets2) {
  return insets1.top == insets2.top && insets1.left == insets2.left && insets1.bottom == insets2.bottom && insets1.right == insets2.right;
}""",
    "UIEdgeInsetsInsetRect": """\
NS_INLINE CGRect UIEdgeInsetsInsetRect(CGRect rect, UIEdgeInsets insets) {
  return CGRectMake(rect.origin.x + insets.left,
                    rect.origin.y + insets.top,
                    rect.size.width - insets.left - insets.right,
                    rect.size.height - insets.top - insets.bottom);
}""",
    "UIOffsetMake": """\
NS_INLINE UIOffset UIOffsetMake(CGFloat horizontal, CGFloat vertical) {
  UIOffset offset; offset.horizontal = horizontal; offset.vertical = vertical; return offset;
}""",
    "UIOffsetEqualToOffset": """\
NS_INLINE BOOL UIOffsetEqualToOffset(UIOffset offset1, UIOffset offset2) {
  return offset1.horizontal == offset2.horizontal && offset1.vertical == offset2.vertical;
}""",

    # ── UIKit: NSDirectionalEdgeInsets ────────────────────────────────
    "NSDirectionalEdgeInsetsMake": """\
NS_INLINE NSDirectionalEdgeInsets NSDirectionalEdgeInsetsMake(CGFloat top, CGFloat leading, CGFloat bottom, CGFloat trailing) {
  NSDirectionalEdgeInsets insets; insets.top = top; insets.leading = leading; insets.bottom = bottom; insets.trailing = trailing; return insets;
}""",

    # ── CoreMedia: CMTime ─────────────────────────────────────────────
    "CMTimeMake": """\
NS_INLINE CMTime CMTimeMake(int64_t value, int32_t timescale) {
  CMTime t; t.value = value; t.timescale = timescale; t.flags = kCMTimeFlags_Valid; t.epoch = 0; return t;
}""",
    "CMTimeMakeWithSeconds": """\
NS_INLINE CMTime CMTimeMakeWithSeconds(Float64 seconds, int32_t preferredTimescale) {
  CMTime t; t.value = (int64_t)(seconds * preferredTimescale); t.timescale = preferredTimescale; t.flags = kCMTimeFlags_Valid; t.epoch = 0; return t;
}""",
    "CMTimeGetSeconds": """\
NS_INLINE Float64 CMTimeGetSeconds(CMTime time) {
  if (time.timescale == 0) return 0;
  return (Float64)time.value / (Float64)time.timescale;
}""",

    # ── CoreMedia: CMTimeRange ────────────────────────────────────────
    "CMTimeRangeMake": """\
NS_INLINE CMTimeRange CMTimeRangeMake(CMTime start, CMTime duration) {
  CMTimeRange range; range.start = start; range.duration = duration; return range;
}""",

    # ── simd: basic constructors ──────────────────────────────────────
    "simd_make_float2": """\
static inline simd_float2 simd_make_float2(float x, float y) {
  simd_float2 v = {x, y}; return v;
}""",
    "simd_make_float3": """\
static inline simd_float3 simd_make_float3(float x, float y, float z) {
  simd_float3 v = {x, y, z}; return v;
}""",
    "simd_make_float4": """\
static inline simd_float4 simd_make_float4(float x, float y, float z, float w) {
  simd_float4 v = {x, y, z, w}; return v;
}""",
}
