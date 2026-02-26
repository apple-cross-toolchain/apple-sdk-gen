from __future__ import annotations

import logging
from collections import defaultdict

from ..models.availability import availability_macro, deprecated_macro
from ..models.symbol import Symbol
from ..models.types import SymbolKind
from ..supplements.enum_values import get_case_value, is_options_enum
from ..supplements.inline_functions import INLINE_FUNCTIONS

logger = logging.getLogger(__name__)

# Compatibility macros needed for generated headers
COMPAT_PREAMBLE = """\
#pragma once

/* ── Base types ──────────────────────────────────────────────────────
   Use real ObjC runtime headers when present (--include-libc installs
   them from apple-oss-distributions/objc4).  Otherwise provide minimal
   inline definitions so the stub headers compile standalone.
   ─────────────────────────────────────────────────────────────────── */
#ifndef _APPLE_SDK_GEN_COMPAT_TYPES_
#define _APPLE_SDK_GEN_COMPAT_TYPES_ 1

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#if __has_include(<objc/objc.h>)
#  import <objc/objc.h>
#else
typedef bool BOOL;
#  define YES ((BOOL)1)
#  define NO  ((BOOL)0)
typedef struct objc_class *Class;
typedef struct objc_object *id;
typedef struct objc_selector *SEL;
typedef id (*IMP)(id, SEL, ...);
#  ifndef nil
#    define nil ((id)0)
#  endif
#  ifndef Nil
#    define Nil ((Class)0)
#  endif
#endif

#if __has_include(<objc/NSObjCRuntime.h>)
#  import <objc/NSObjCRuntime.h>
#else
#  if __LP64__
typedef long NSInteger;
typedef unsigned long NSUInteger;
#  else
typedef int NSInteger;
typedef unsigned int NSUInteger;
#  endif
#  define NSIntegerMax    __LONG_MAX__
#  define NSIntegerMin    (-__LONG_MAX__-1L)
#  define NSUIntegerMax   (2UL*__LONG_MAX__+1UL)
#  define NSNotFound      NSIntegerMax
#endif

#endif /* _APPLE_SDK_GEN_COMPAT_TYPES_ */

/* --- Availability --- */
#ifndef API_AVAILABLE
#define API_AVAILABLE(...)
#endif
#ifndef API_DEPRECATED
#define API_DEPRECATED(...)
#endif
#ifndef API_DEPRECATED_WITH_REPLACEMENT
#define API_DEPRECATED_WITH_REPLACEMENT(...)
#endif
#ifndef API_UNAVAILABLE
#define API_UNAVAILABLE(...)
#endif

/* --- Nullability --- */
#ifndef NS_ASSUME_NONNULL_BEGIN
#define NS_ASSUME_NONNULL_BEGIN _Pragma("clang assume_nonnull begin")
#endif
#ifndef NS_ASSUME_NONNULL_END
#define NS_ASSUME_NONNULL_END _Pragma("clang assume_nonnull end")
#endif

/* --- Swift interop --- */
#ifndef NS_SWIFT_NAME
#define NS_SWIFT_NAME(x)
#endif
#ifndef NS_REFINED_FOR_SWIFT
#define NS_REFINED_FOR_SWIFT
#endif
#ifndef NS_SWIFT_UNAVAILABLE
#define NS_SWIFT_UNAVAILABLE(x)
#endif
#ifndef NS_SWIFT_SENDABLE
#define NS_SWIFT_SENDABLE
#endif
#ifndef NS_SWIFT_NONSENDABLE
#define NS_SWIFT_NONSENDABLE
#endif
#ifndef NS_SWIFT_UI_ACTOR
#define NS_SWIFT_UI_ACTOR
#endif
#ifndef NS_SWIFT_ASYNC
#define NS_SWIFT_ASYNC(x)
#endif
#ifndef NS_SWIFT_ASYNC_NAME
#define NS_SWIFT_ASYNC_NAME(x)
#endif
#ifndef NS_SWIFT_ASYNC_THROWS_ON_FALSE
#define NS_SWIFT_ASYNC_THROWS_ON_FALSE(x)
#endif

/* --- Enum / options macros --- */
#ifndef NS_ENUM
#define NS_ENUM(_type, _name) enum _name : _type _name; enum _name : _type
#endif
#ifndef NS_OPTIONS
#define NS_OPTIONS(_type, _name) enum _name : _type _name; enum _name : _type
#endif
#ifndef NS_CLOSED_ENUM
#define NS_CLOSED_ENUM(_type, _name) enum _name : _type _name; enum _name : _type
#endif
#ifndef CF_ENUM
#define CF_ENUM(_type, _name) enum _name : _type _name; enum _name : _type
#endif
#ifndef CF_OPTIONS
#define CF_OPTIONS(_type, _name) enum _name : _type _name; enum _name : _type
#endif
#ifndef CF_CLOSED_ENUM
#define CF_CLOSED_ENUM(_type, _name) enum _name : _type _name; enum _name : _type
#endif
#ifndef NS_TYPED_ENUM
#define NS_TYPED_ENUM
#endif
#ifndef NS_TYPED_EXTENSIBLE_ENUM
#define NS_TYPED_EXTENSIBLE_ENUM
#endif
#ifndef NS_STRING_ENUM
#define NS_STRING_ENUM
#endif
#ifndef NS_EXTENSIBLE_STRING_ENUM
#define NS_EXTENSIBLE_STRING_ENUM
#endif
#ifndef NS_ERROR_ENUM
#define NS_ERROR_ENUM(_domain) NS_ENUM(NSInteger,
#endif

/* --- Inline / extern --- */
#ifndef NS_INLINE
#define NS_INLINE static inline
#endif
#ifndef CF_INLINE
#define CF_INLINE static inline
#endif
#ifndef CG_INLINE
#define CG_INLINE static inline
#endif
#ifndef CG_EXTERN
#define CG_EXTERN extern
#endif
#ifndef CF_EXPORT
#define CF_EXPORT extern
#endif
#ifndef FOUNDATION_EXPORT
#define FOUNDATION_EXPORT extern
#endif
#ifndef FOUNDATION_EXTERN
#define FOUNDATION_EXTERN extern
#endif
#ifndef UIKIT_EXTERN
#define UIKIT_EXTERN extern
#endif

/* --- Method attributes --- */
#ifndef NS_DESIGNATED_INITIALIZER
#define NS_DESIGNATED_INITIALIZER
#endif
#ifndef NS_UNAVAILABLE
#define NS_UNAVAILABLE __attribute__((unavailable))
#endif
#ifndef NS_REQUIRES_SUPER
#define NS_REQUIRES_SUPER __attribute__((objc_requires_super))
#endif
#ifndef NS_NOESCAPE
#define NS_NOESCAPE __attribute__((noescape))
#endif
#ifndef NS_RETURNS_RETAINED
#define NS_RETURNS_RETAINED __attribute__((ns_returns_retained))
#endif
#ifndef NS_RETURNS_NOT_RETAINED
#define NS_RETURNS_NOT_RETAINED __attribute__((ns_returns_not_retained))
#endif
#ifndef NS_RETURNS_INNER_POINTER
#define NS_RETURNS_INNER_POINTER __attribute__((objc_returns_inner_pointer))
#endif
#ifndef NS_ROOT_CLASS
#define NS_ROOT_CLASS __attribute__((objc_root_class))
#endif
#ifndef NS_REQUIRES_NIL_TERMINATION
#define NS_REQUIRES_NIL_TERMINATION __attribute__((sentinel(0,1)))
#endif

/* --- Deprecation / class availability --- */
#ifndef NS_CLASS_AVAILABLE
#define NS_CLASS_AVAILABLE(...)
#endif
#ifndef NS_CLASS_DEPRECATED
#define NS_CLASS_DEPRECATED(...)
#endif
#ifndef NS_CLASS_AVAILABLE_IOS
#define NS_CLASS_AVAILABLE_IOS(...)
#endif
#ifndef NS_CLASS_DEPRECATED_IOS
#define NS_CLASS_DEPRECATED_IOS(...)
#endif
#ifndef NS_DEPRECATED
#define NS_DEPRECATED(...)
#endif
#ifndef NS_DEPRECATED_IOS
#define NS_DEPRECATED_IOS(...)
#endif
#ifndef NS_AVAILABLE
#define NS_AVAILABLE(...)
#endif
#ifndef NS_AVAILABLE_IOS
#define NS_AVAILABLE_IOS(...)
#endif

/* --- Format functions --- */
#ifndef NS_FORMAT_FUNCTION
#define NS_FORMAT_FUNCTION(F,A) __attribute__((format(__NSString__, F, A)))
#endif
#ifndef NS_FORMAT_ARGUMENT
#define NS_FORMAT_ARGUMENT(A) __attribute__((format_arg(A)))
#endif

/* --- Extern C --- */
#ifndef CF_EXTERN_C_BEGIN
#define CF_EXTERN_C_BEGIN extern "C" {
#endif
#ifndef CF_EXTERN_C_END
#define CF_EXTERN_C_END }
#endif

/* --- Header audit --- */
#ifndef NS_HEADER_AUDIT_BEGIN
#define NS_HEADER_AUDIT_BEGIN(x)
#endif
#ifndef NS_HEADER_AUDIT_END
#define NS_HEADER_AUDIT_END(x)
#endif

/* --- Misc --- */
#ifndef NS_DURING
#define NS_DURING
#endif
#ifndef NS_HANDLER
#define NS_HANDLER
#endif
#ifndef NS_ENDHANDLER
#define NS_ENDHANDLER
#endif
#ifndef NS_VALID_UNTIL_END_OF_SCOPE
#define NS_VALID_UNTIL_END_OF_SCOPE __attribute__((objc_precise_lifetime))
#endif
#ifndef NS_AUTOMATED_REFCOUNT_UNAVAILABLE
#define NS_AUTOMATED_REFCOUNT_UNAVAILABLE
#endif
"""


def generate_umbrella_header(
    framework_name: str,
    symbols: list[Symbol],
    all_symbols: dict[str, Symbol] | None = None,
) -> str:
    """Generate the main umbrella header for a framework."""
    lines: list[str] = []
    lines.append(f"// {framework_name}.h - Generated by apple-sdk-gen")
    lines.append(f"// This is a stub header for cross-compilation")
    lines.append("")
    lines.append(COMPAT_PREAMBLE)
    lines.append("")

    # Collect imports for cross-framework references
    imports = _collect_imports(symbols, framework_name)
    for imp in sorted(imports):
        lines.append(f"#import <{imp}/{imp}.h>")
    if imports:
        lines.append("")

    # Group symbols by kind for proper ordering
    groups = _group_symbols(symbols)

    # Forward declarations
    forward_classes = set()
    forward_protocols = set()
    for sym in symbols:
        if sym.kind == SymbolKind.CLASS:
            forward_classes.add(sym.objc_name)
        elif sym.kind == SymbolKind.PROTOCOL:
            forward_protocols.add(sym.objc_name)

    if forward_classes:
        for cls in sorted(forward_classes):
            lines.append(f"@class {cls};")
        lines.append("")

    if forward_protocols:
        for proto in sorted(forward_protocols):
            lines.append(f"@protocol {proto};")
        lines.append("")

    # Emit typedefs and enums first
    for sym in groups.get("typedef", []):
        decl = _render_symbol_declaration(sym)
        if decl:
            lines.append(decl)
            lines.append("")

    for sym in groups.get("enum", []):
        enum_def = _render_enum_definition(sym, symbols, all_symbols)
        if enum_def:
            lines.append(enum_def)
            lines.append("")

    # Emit global variables
    for sym in groups.get("var", []):
        decl = _render_symbol_declaration(sym)
        if decl:
            lines.append(decl)
            lines.append("")

    # Emit global functions (substituting inline bodies where known)
    for sym in groups.get("func", []):
        func_name = sym.objc_name
        if func_name in INLINE_FUNCTIONS:
            lines.append(INLINE_FUNCTIONS[func_name])
            lines.append("")
        else:
            decl = _render_symbol_declaration(sym)
            if decl:
                lines.append(decl)
                lines.append("")

    # Emit protocols
    for sym in groups.get("protocol", []):
        block = _render_interface_block(sym, symbols, all_symbols)
        if block:
            lines.append(block)
            lines.append("")

    # Emit classes
    for sym in groups.get("class", []):
        block = _render_interface_block(sym, symbols, all_symbols)
        if block:
            lines.append(block)
            lines.append("")

    # Emit structs (with field definitions where possible)
    for sym in groups.get("struct", []):
        struct_def = _render_struct_definition(sym, symbols, all_symbols)
        if struct_def:
            lines.append(struct_def)
            lines.append("")

    return "\n".join(lines)


def _collect_imports(symbols: list[Symbol], framework_name: str) -> set[str]:
    imports: set[str] = set()
    for sym in symbols:
        for rel in sym.relationships:
            for ident in rel.identifiers:
                if "com.externally.resolved.symbol" in ident:
                    continue
                if "/documentation/" in ident:
                    parts = ident.split("/documentation/", 1)[1].split("/")
                    if parts and parts[0].lower() != framework_name.lower():
                        imports.add(parts[0])
    # Always import Foundation for non-Foundation frameworks
    if framework_name != "Foundation" and framework_name != "ObjectiveC":
        imports.add("Foundation")
    return imports


def _group_symbols(symbols: list[Symbol]) -> dict[str, list[Symbol]]:
    groups: dict[str, list[Symbol]] = defaultdict(list)
    seen: set[str] = set()
    for sym in symbols:
        if not sym.is_objc:
            continue
        # Deduplicate by identifier
        key = sym.identifier or sym.title
        if key in seen:
            continue
        seen.add(key)

        if sym.kind == SymbolKind.CLASS:
            groups["class"].append(sym)
        elif sym.kind == SymbolKind.PROTOCOL:
            groups["protocol"].append(sym)
        elif sym.kind == SymbolKind.ENUM:
            groups["enum"].append(sym)
        elif sym.kind in (SymbolKind.TYPEALIAS, SymbolKind.TYPEDEF):
            groups["typedef"].append(sym)
        elif sym.kind == SymbolKind.FUNC:
            groups["func"].append(sym)
        elif sym.kind == SymbolKind.VAR:
            groups["var"].append(sym)
        elif sym.kind == SymbolKind.STRUCT:
            groups["struct"].append(sym)
    return groups


def _render_symbol_declaration(sym: Symbol) -> str | None:
    if not sym.objc_declaration:
        return None

    decl_text = sym.objc_declaration.render().strip()
    if not decl_text:
        return None

    avail = availability_macro(sym)
    dep = deprecated_macro(sym)
    suffix = ""
    if dep:
        suffix = f" {dep}"
    elif avail:
        suffix = f" {avail}"

    # Ensure declaration ends with semicolon if it's a simple decl
    if not decl_text.endswith(";") and not decl_text.endswith("}"):
        decl_text += ";"

    return f"{decl_text}{suffix}"


def _render_interface_block(
    sym: Symbol,
    all_framework_symbols: list[Symbol],
    all_symbols: dict[str, Symbol] | None = None,
) -> str | None:
    if not sym.is_objc:
        return None

    lines: list[str] = []
    avail = availability_macro(sym)
    avail_str = f" {avail}" if avail else ""

    if sym.kind == SymbolKind.PROTOCOL:
        lines.append(f"@protocol {sym.objc_name}{avail_str}")
    elif sym.kind == SymbolKind.CLASS:
        superclass = _resolve_superclass(sym)
        protocols = _resolve_protocols(sym)
        proto_str = f" <{', '.join(protocols)}>" if protocols else ""
        if superclass:
            lines.append(f"@interface {sym.objc_name} : {superclass}{proto_str}{avail_str}")
        else:
            lines.append(f"@interface {sym.objc_name}{proto_str}{avail_str}")
    else:
        return None

    # Find child members
    children = _find_children(sym, all_framework_symbols, all_symbols)
    for child in children:
        if not child.objc_declaration:
            continue
        child_decl = child.objc_declaration.render().strip()
        if not child_decl:
            continue
        child_avail = availability_macro(child)
        child_suffix = f" {child_avail}" if child_avail else ""
        if not child_decl.endswith(";"):
            child_decl += ";"
        lines.append(f"{child_decl}{child_suffix}")

    lines.append("@end")
    return "\n".join(lines)


def _render_enum_definition(
    sym: Symbol,
    all_framework_symbols: list[Symbol],
    all_symbols: dict[str, Symbol] | None = None,
) -> str | None:
    """Render an enum with case values from child symbols and the known-values table."""
    if not sym.is_objc:
        return None

    decl_text = sym.objc_declaration.render().strip() if sym.objc_declaration else ""
    if not decl_text:
        return None

    avail = availability_macro(sym)
    suffix = f" {avail}" if avail else ""

    # If the declaration already has a body, pass through
    if "{" in decl_text:
        if not decl_text.endswith(";"):
            decl_text += ";"
        return f"{decl_text}{suffix}"

    # Find child enum cases
    children = _find_children(sym, all_framework_symbols, all_symbols)
    cases = [c for c in children if c.kind == SymbolKind.ENUM_CASE]

    if not cases:
        # Fall back to bare declaration
        if not decl_text.endswith(";"):
            decl_text += ";"
        return f"{decl_text}{suffix}"

    # Determine if this is an NS_OPTIONS bitmask enum
    enum_name = sym.objc_name
    options = is_options_enum(enum_name) or "NS_OPTIONS" in decl_text or "CF_OPTIONS" in decl_text

    # Build enum body
    # Extract the base type from the declaration, e.g.
    #   "typedef NS_ENUM(NSInteger, NSComparisonResult)"  ->  header is same
    #   "enum NSComparisonResult : NSInteger"              ->  need to open body
    # We re-emit the declaration up to (but not including) the trailing ;, then { cases }
    header = decl_text.rstrip(";").rstrip()

    case_lines = []
    for i, case_sym in enumerate(cases):
        case_name = case_sym.objc_name or case_sym.title
        known_val = get_case_value(case_name)
        if known_val is not None:
            case_lines.append(f"    {case_name} = {known_val},")
        elif options:
            # Power-of-two fallback for bitmask enums
            case_lines.append(f"    {case_name} = (1 << {i}),")
        else:
            # Auto-increment: just emit the name and let the compiler assign
            case_lines.append(f"    {case_name} = {i},")

    lines = [f"{header} {{{suffix}"]
    lines.extend(case_lines)
    lines.append("};")
    return "\n".join(lines)


def _render_struct_definition(
    sym: Symbol,
    all_framework_symbols: list[Symbol],
    all_symbols: dict[str, Symbol] | None = None,
) -> str | None:
    """Render a struct with field definitions from child symbols."""
    if not sym.is_objc:
        return None

    decl_text = sym.objc_declaration.render().strip() if sym.objc_declaration else ""
    if not decl_text:
        return None

    avail = availability_macro(sym)
    suffix = f" {avail}" if avail else ""

    # If the declaration already has a body, pass through
    if "{" in decl_text:
        if not decl_text.endswith(";"):
            decl_text += ";"
        return f"{decl_text}{suffix}"

    # Try to build the struct body from child symbols
    children = _find_children(sym, all_framework_symbols, all_symbols)
    fields = []
    for child in children:
        if child.kind not in (SymbolKind.PROPERTY, SymbolKind.VAR):
            continue
        field_line = _normalize_struct_field(child)
        if field_line:
            fields.append(f"    {field_line}")

    if not fields:
        # Fall back to forward declaration
        if not decl_text.endswith(";"):
            decl_text += ";"
        return f"{decl_text}{suffix}"

    # Build "struct Name { ... };" from the declaration
    struct_name = sym.objc_name
    # Extract the typedef prefix if present, e.g. "typedef struct CGPoint CGPoint"
    # Common patterns:
    #   "struct CGPoint;"
    #   "typedef struct CGPoint CGPoint;"
    #   "typedef struct CGPoint { ... } CGPoint;"
    lines = []
    if decl_text.startswith("typedef"):
        lines.append(f"typedef struct {struct_name} {{")
    else:
        lines.append(f"struct {struct_name} {{")
    lines.extend(fields)
    if decl_text.startswith("typedef"):
        lines.append(f"}} {struct_name};{suffix}")
    else:
        lines.append(f"}};{suffix}")
    return "\n".join(lines)


def _normalize_struct_field(child: Symbol) -> str | None:
    """Convert a child symbol into a C struct field declaration.

    Handles both C-style ("CGFloat x;") and Swift-style ("var x: CGFloat")
    declarations that come from the ObjC or Swift declaration.
    """
    # Prefer ObjC declaration
    if child.objc_declaration:
        decl = child.objc_declaration.render().strip()
        if decl:
            # Already C-style: "CGFloat x" or "CGFloat x;"
            if not decl.endswith(";"):
                decl += ";"
            return decl

    # Fall back to Swift declaration and convert
    if child.swift_declaration:
        decl = child.swift_declaration.render().strip()
        if decl:
            return _swift_field_to_c(decl, child.title)

    return None


# Maps Swift types seen in struct fields to their C equivalents
_SWIFT_TO_C_TYPES: dict[str, str] = {
    "Double": "double",
    "Float": "float",
    "Float64": "Float64",
    "Float32": "Float32",
    "Int": "NSInteger",
    "UInt": "NSUInteger",
    "Int8": "int8_t",
    "Int16": "int16_t",
    "Int32": "int32_t",
    "Int64": "int64_t",
    "UInt8": "uint8_t",
    "UInt16": "uint16_t",
    "UInt32": "uint32_t",
    "UInt64": "uint64_t",
    "Bool": "BOOL",
    "CGFloat": "CGFloat",
    "CGPoint": "CGPoint",
    "CGSize": "CGSize",
    "CGRect": "CGRect",
    "CFIndex": "CFIndex",
    "CFRange": "CFRange",
    "CFTimeInterval": "CFTimeInterval",
    "CMTimeValue": "int64_t",
    "CMTimeScale": "int32_t",
    "CMTimeFlags": "uint32_t",
    "CMTimeEpoch": "int64_t",
}


def _swift_field_to_c(swift_decl: str, field_name: str) -> str | None:
    """Convert 'var x: CGFloat' to 'CGFloat x;'."""
    # Pattern: "var name: Type" or "let name: Type"
    stripped = swift_decl.strip().rstrip(";")
    if stripped.startswith(("var ", "let ")):
        stripped = stripped[4:].strip()
    colon_idx = stripped.find(":")
    if colon_idx < 0:
        return None
    swift_type = stripped[colon_idx + 1:].strip()
    c_type = _SWIFT_TO_C_TYPES.get(swift_type, swift_type)
    return f"{c_type} {field_name};"


def _resolve_superclass(sym: Symbol) -> str | None:
    for rel in sym.relationships:
        if rel.kind == "inheritsFrom":
            for ident in rel.identifiers:
                # Extract class name from identifier
                if "c:objc(cs)" in ident:
                    return ident.split("c:objc(cs)")[-1]
                # Try to extract from doc path
                if "/documentation/" in ident:
                    parts = ident.split("/")
                    return parts[-1]
    return None


def _resolve_protocols(sym: Symbol) -> list[str]:
    protocols = []
    for rel in sym.relationships:
        if rel.kind == "conformsTo":
            for ident in rel.identifiers:
                if "c:objc(pl)" in ident:
                    protocols.append(ident.split("c:objc(pl)")[-1])
                elif "/documentation/" in ident:
                    parts = ident.split("/")
                    name = parts[-1]
                    # Only include if it looks like a protocol name
                    if name and name[0].isupper():
                        protocols.append(name)
    return protocols


def _normalize_path(identifier: str) -> str:
    """Extract and normalize the documentation path for comparison.

    Handles both formats:
    - doc://com.apple.foundation/documentation/Foundation/NSString/length
    - /documentation/foundation/nsstring/length
    """
    if "/documentation/" in identifier:
        path = "/documentation/" + identifier.split("/documentation/", 1)[1]
    else:
        path = identifier
    return path.lower().rstrip("/")


def _find_children(
    parent: Symbol,
    all_framework_symbols: list[Symbol],
    all_symbols: dict[str, Symbol] | None = None,
) -> list[Symbol]:
    child_paths_normalized = {_normalize_path(cp) for cp in parent.children}

    children: list[Symbol] = []
    seen: set[str] = set()

    for sym in all_framework_symbols:
        if not sym.identifier:
            continue
        norm = _normalize_path(sym.identifier)
        if norm in child_paths_normalized and norm not in seen:
            seen.add(norm)
            children.append(sym)

    if all_symbols:
        for cp in parent.children:
            norm = _normalize_path(cp)
            if norm in seen:
                continue
            if norm in all_symbols:
                seen.add(norm)
                children.append(all_symbols[norm])

    return children
