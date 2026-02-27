# apple-sdk-gen: Known Limitations and Workarounds

The Apple Developer Documentation JSON API (`developer.apple.com/tutorials/data/documentation/`)
provides excellent type signatures, platform availability, and relationship data — but it was
designed for documentation rendering, not SDK generation. Several categories of information
needed for fully compilable SDKs are absent.

## Summary

| Limitation | Impact | Workaround Feasibility |
|---|---|---|
| No C stdlib/POSIX headers | Cannot compile anything that `#include`s libc | **Solvable** — fetch from apple-oss-distributions |
| No enum raw values | Enum constants have placeholder values | **Solvable** — scrape from open-source headers |
| No struct field layouts | Struct bodies are empty | **Partially solvable** — infer from field types |
| No preprocessor macro bodies | `NS_ENUM`, `NS_OPTIONS` etc. missing | **Solvable** — ship a static compatibility header |
| No inline function bodies | `NSMakeRange`, `CGPointMake` etc. are stubs | **Solvable** — ship a static compatibility header |
| Category origin flattened | All methods attributed to base class | **Partially solvable** — heuristic splitting |

---

## 1. No C Standard Library / POSIX Headers

**Problem:** The API covers only Apple frameworks (Foundation, UIKit, etc.). Standard C library
functions (`printf`, `malloc`, `strlen`) and POSIX APIs (`open`, `read`, `pthread_*`) are
completely absent. `darwin.json` returns 404.

**Impact:** Virtually all compiled code depends on libc. Without `<stdio.h>`, `<stdlib.h>`,
`<string.h>`, `<unistd.h>`, etc., nothing compiles.

**Workaround:** Fetch headers from Apple's open-source distributions. The C library headers
ship as part of macOS and are published at:

- **Libc headers**: https://github.com/apple-oss-distributions/Libc
- **xnu (kernel headers, sys/\*, mach/\*)**: https://github.com/apple-oss-distributions/xnu
- **libpthread**: https://github.com/apple-oss-distributions/libpthread
- **Libsystem**: https://github.com/apple-oss-distributions/Libsystem

These repos contain the exact headers shipped in macOS SDKs. A supplementary script can:
1. Clone the relevant repos at the tag matching the target SDK version
2. Copy `usr/include/` into the generated SDK at `<sdk>/usr/include/`
3. Add a `usr/lib/libSystem.B.tbd` stub for linking

This fully solves the libc gap. The headers are platform-independent (same across all Apple
platforms for the C standard subset), and the TBD stubs only need to export `libSystem.B.dylib`.

---

## 2. No Enum Raw Values

**Problem:** The API documents enum case names and backing types but not numeric values.
For example, `NSOrderedAscending` is documented as `case orderedAscending` with no mention
of its value `-1`.

**Impact:** Code using enum values as compile-time constants (e.g., switch cases, bitfield
checks with `NS_OPTIONS`) will get wrong values. Linking still works since enums are typically
inlined by the compiler, but behavior would be incorrect.

**Workaround options:**

1. **Scrape from open-source headers** (best): Many Foundation/CoreFoundation enums are defined
   in headers published at apple-oss-distributions. Parse the `#define` or `NS_ENUM` blocks
   to extract numeric values. A script can:
   - Fetch `NSObjCRuntime.h`, `NSRange.h`, etc. from the Libc/Foundation repos
   - Parse `= value` assignments in enum declarations
   - Inject them into generated headers

2. **Hardcode known values**: Maintain a lookup table of critical enum values
   (`NSOrderedAscending = -1`, `NSOrderedSame = 0`, `NSOrderedDescending = 1`, etc.).
   The most important ~200 enums (Foundation, UIKit, CoreGraphics) are stable across releases.

3. **Auto-increment placeholder**: Assign `0, 1, 2, ...` values. This is correct for many
   enums that start at 0 and increment (the default C behavior), but wrong for enums with
   explicit values or `NS_OPTIONS` bitmasks.

---

## 3. No Struct Field Memory Layouts

**Problem:** The API provides struct field names and types (`CGPoint` has `x: CGFloat` and
`y: CGFloat`) but not byte offsets, field sizes, alignment, or padding. The struct declaration
token is just `struct CGPoint` with no body.

**Impact:** Generated struct declarations have empty bodies. Code that accesses struct fields
(`point.x`) won't compile. Code that passes structs by value across ABI boundaries may
silently corrupt data if the layout is wrong.

**Workaround options:**

1. **Reconstruct from field types** (recommended): Since the API provides field names and
   types, and C struct layout follows deterministic ABI rules, we can reconstruct the layout:
   - Fetch child symbol pages to get field names + types
   - Emit `struct CGPoint { CGFloat x; CGFloat y; };`
   - The compiler will compute the correct layout from the types

   This works for all structs composed of known types. The generator already collects child
   symbols — it just needs to emit them as struct fields instead of standalone declarations.

2. **Fetch from open-source headers**: Same as the enum workaround — parse struct definitions
   from apple-oss-distributions headers for CoreGraphics, Foundation, etc.

---

## 4. No Preprocessor Macro Definitions

**Problem:** Critical macros like `NS_ENUM`, `NS_OPTIONS`, `NS_ASSUME_NONNULL_BEGIN`,
`CF_ENUM`, `__attribute__` wrappers, `TARGET_OS_IPHONE`, etc. are either missing entirely
(404 for `NS_ENUM`) or documented without their expansion (signature only, no `#define` body).

**Impact:** ObjC headers use these macros pervasively. Without them, generated headers don't
compile.

**Workaround:** Ship a static **compatibility header** with the generated SDK. The macros
are stable across SDK versions and can be defined once:

```c
// apple_sdk_gen_compat.h — ship with generated SDKs

#ifndef NS_ENUM
#define NS_ENUM(_type, _name) enum _name : _type _name; enum _name : _type
#endif
#ifndef NS_OPTIONS
#define NS_OPTIONS(_type, _name) enum _name : _type _name; enum _name : _type
#endif
#ifndef NS_CLOSED_ENUM
#define NS_CLOSED_ENUM(_type, _name) enum _name : _type _name; enum _name : _type
#endif
#ifndef NS_ASSUME_NONNULL_BEGIN
#define NS_ASSUME_NONNULL_BEGIN _Pragma("clang assume_nonnull begin")
#endif
#ifndef NS_ASSUME_NONNULL_END
#define NS_ASSUME_NONNULL_END _Pragma("clang assume_nonnull end")
#endif
// ... ~50 more macros
```

The generated umbrella headers already include a compatibility preamble with the most critical
macros. This preamble can be expanded to cover all needed macros.

Alternatively, copy `NSObjCRuntime.h` and `CFBase.h` from apple-oss-distributions — these
two files define the vast majority of Objective-C infrastructure macros.

---

## 5. No Inline Function Bodies

**Problem:** Functions like `NSMakeRange`, `CGPointMake`, `CGRectMake`, `NSMaxRange`,
`NSLocationInRange`, and many CoreFoundation helpers are `static inline` in the real SDK
headers. The API documents only their signatures, not their implementations.

**Impact:** If declared as external symbols, they fail at link time (they don't exist in
dylibs — they're header-only). If omitted, code using them doesn't compile.

**Workaround options:**

1. **Ship a static inline implementations header** (recommended): These functions are trivial
   constructors/accessors with stable implementations:

   ```c
   // apple_sdk_gen_inlines.h
   NS_INLINE NSRange NSMakeRange(NSUInteger loc, NSUInteger len) {
       NSRange r; r.location = loc; r.length = len; return r;
   }
   NS_INLINE CGPoint CGPointMake(CGFloat x, CGFloat y) {
       CGPoint p; p.x = x; p.y = y; return p;
   }
   NS_INLINE CGFloat NSMaxX(CGRect r) { return r.origin.x + r.size.width; }
   // ... ~100 more
   ```

   There are roughly 100-150 inline functions across Foundation, CoreGraphics, and
   CoreFoundation. Their implementations haven't changed in decades.

2. **Fetch from open-source headers**: Extract inline function bodies from
   `NSRange.h`, `CGGeometry.h`, etc. in apple-oss-distributions.

---

## 6. ObjC Category Origin Information Flattened

**Problem:** The API merges all methods (including those from categories defined in other
frameworks) onto the base class. For example, `NSString`'s `draw(at:withAttributes:)` (which
comes from UIKit's `NSStringDrawing` category) appears as a Foundation method with no
indication of its actual origin.

**Impact:** Generated headers put all methods in a single `@interface` block. This works
for compilation but:
- Violates the framework modularity (methods requiring UIKit appear in Foundation headers)
- May cause linker errors if a method's implementing framework isn't linked
- Doesn't match the real SDK's header-per-category structure

**Workaround options:**

1. **Accept the flattening** (pragmatic): For cross-compilation linking, having all methods
   in one `@interface` block actually works fine. The TBD stubs handle symbol resolution.
   The only issue is code organization, not functionality.

2. **Heuristic splitting**: Use platform availability as a signal — if a method on
   `NSString` is only available on iOS (not macOS), it likely comes from UIKit. The
   `metadata.modules` field occasionally hints at the origin module.

3. **Cross-reference with real SDK headers**: Parse the actual Xcode SDK headers to build
   a mapping of `(class, method) → category → framework`. Apply this mapping when generating
   headers. This requires macOS + Xcode for the initial mapping but the result can be
   serialized and reused.

---

## Recommended Approach: Hybrid Generation

The most practical path to fully compilable SDKs combines this tool with supplementary data:

1. **Run `apple-sdk-gen`** for framework-level ObjC headers, TBD stubs, modulemaps, and
   Swift interfaces (what this tool does)
2. **Overlay C stdlib headers** from apple-oss-distributions repos
3. **Ship a static compatibility header** for macros and inline functions
4. **Optionally scrape enum values** from open-source headers

This hybrid approach produces SDKs that work for cross-compilation linking without
requiring macOS or Xcode, while acknowledging that the documentation API alone cannot
provide a complete SDK.
