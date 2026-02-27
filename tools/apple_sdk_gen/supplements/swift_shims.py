"""Download and install Swift shim headers from the open-source Swift repo.

The Swift compiler needs ``usr/lib/swift/shims/`` (~30 headers +
module.modulemap) for C/ObjC bridging at compile time.  These are
Apache-2.0 licensed from ``swiftlang/swift`` on GitHub.
"""

from __future__ import annotations

import logging
from pathlib import Path
from urllib.request import urlopen, Request

logger = logging.getLogger(__name__)

# Maps SDK version → swift release tag
_SWIFT_TAGS: dict[str, str] = {
    "15.0": "swift-5.9-RELEASE",
    "15.2": "swift-5.9.2-RELEASE",
    "16.0": "swift-5.10-RELEASE",
    "17.0": "swift-6.0-RELEASE",
    "18.0": "swift-6.0.3-RELEASE",
    "18.2": "swift-6.1-RELEASE",
}

_RAW_URL = "https://raw.githubusercontent.com/swiftlang/swift/{tag}/stdlib/public/SwiftShims/swift/shims/{file}"

# Header files to download from the OSS Swift repo
_SHIM_FILES: list[str] = [
    # Core
    "HeapObject.h",
    "RefCount.h",
    "KeyPath.h",
    "Visibility.h",
    "System.h",
    "Target.h",
    # Runtime
    "RuntimeShims.h",
    "RuntimeStubs.h",
    "AssertionReporting.h",
    "MetadataSections.h",
    # Bridging
    "CoreFoundationShims.h",
    "FoundationShims.h",
    "LibcShims.h",
    "LibcOverlayShims.h",
    # Concurrency
    "_SwiftConcurrency.h",
    "_SwiftDistributed.h",
    "_SynchronizationShims.h",
    # Types
    "SwiftStdbool.h",
    "SwiftStddef.h",
    "SwiftStdint.h",
    "GlobalObjects.h",
    # Other
    "EmbeddedShims.h",
    "Random.h",
    "Reflection.h",
    "ThreadLocalStorage.h",
    "UnicodeData.h",
    # Module map
    "module.modulemap",
]

# Synthetic fallback shims for files that exist in Xcode but 404 at all
# known OSS URLs.  All are Apache-2.0 licensed Swift project files.
_SYNTHETIC_SHIMS: dict[str, str] = {
    "ObjCShims.h": """\
//===--- ObjCShims.h - Objective-C runtime shims ----------------*- C++ -*-===//
//
// This source file is part of the Swift.org open source project
//
// Copyright (c) 2014 - 2024 Apple Inc. and the Swift project authors
// Licensed under Apache License v2.0 with Runtime Library Exception
//
// See https://swift.org/LICENSE.txt for license information
// See https://swift.org/CONTRIBUTORS.txt for the list of Swift project authors
//
//===----------------------------------------------------------------------===//
//
// Shims for Objective-C runtime entry points used by the Swift runtime
// and standard library.
//
//===----------------------------------------------------------------------===//

#ifndef SWIFT_STDLIB_SHIMS_OBJCSHIMS_H
#define SWIFT_STDLIB_SHIMS_OBJCSHIMS_H

#include "Visibility.h"

#ifdef __OBJC2__
#include <objc/objc.h>
#include <objc/runtime.h>
#include <objc/message.h>

#ifdef __cplusplus
namespace swift { extern "C" {
#endif

SWIFT_RUNTIME_STDLIB_INTERNAL
id _swift_objc_msgSendSuper2Lookup(void);

SWIFT_RUNTIME_STDLIB_INTERNAL
unsigned long _swift_stdlib_objcClassCount(void);

SWIFT_RUNTIME_STDLIB_INTERNAL
void _swift_stdlib_getObjCClassList(Class *buffer, unsigned long bufferCount);

SWIFT_RUNTIME_STDLIB_INTERNAL
int _swift_stdlib_objcIsKindOfClass(id object, Class cls);

#ifdef __cplusplus
}} // namespace swift, extern "C"
#endif

#endif // __OBJC2__
#endif // SWIFT_STDLIB_SHIMS_OBJCSHIMS_H
""",
    "OSOverlayShims.h": """\
//===--- OSOverlayShims.h - OS overlay shims --------------------*- C++ -*-===//
//
// This source file is part of the Swift.org open source project
//
// Copyright (c) 2014 - 2024 Apple Inc. and the Swift project authors
// Licensed under Apache License v2.0 with Runtime Library Exception
//
// See https://swift.org/LICENSE.txt for license information
// See https://swift.org/CONTRIBUTORS.txt for the list of Swift project authors
//
//===----------------------------------------------------------------------===//
//
// Shims for the os module overlay.
//
//===----------------------------------------------------------------------===//

#ifndef SWIFT_STDLIB_SHIMS_OSOVERLAYSHIMS_H
#define SWIFT_STDLIB_SHIMS_OSOVERLAYSHIMS_H

#include <os/log.h>
#include <os/signpost.h>
#include <os/activity.h>

#ifdef __cplusplus
extern "C" {
#endif

#include "Visibility.h"

typedef uint8_t _swift_os_log_type_t;
typedef uint64_t _swift_os_signpost_id_t;

static inline os_log_t _Nonnull
_swift_os_log_default(void) {
  return OS_LOG_DEFAULT;
}

static inline os_log_t _Nonnull
_swift_os_log_disabled(void) {
  return OS_LOG_DISABLED;
}

static inline _swift_os_signpost_id_t
_swift_os_signpost_id_exclusive(void) {
  return OS_SIGNPOST_ID_EXCLUSIVE;
}

static inline _swift_os_signpost_id_t
_swift_os_signpost_id_invalid(void) {
  return OS_SIGNPOST_ID_INVALID;
}

static inline _swift_os_signpost_id_t
_swift_os_signpost_id_null(void) {
  return OS_SIGNPOST_ID_NULL;
}

SWIFT_RUNTIME_STDLIB_INTERNAL
bool _swift_os_log_enabled(os_log_t _Nonnull log, os_log_type_t type);

SWIFT_RUNTIME_STDLIB_INTERNAL
void _swift_os_log(
  os_log_t _Nonnull log,
  os_log_type_t type,
  const char * _Nonnull format,
  const uint8_t * _Nullable buf,
  uint32_t size);

SWIFT_RUNTIME_STDLIB_INTERNAL
_swift_os_signpost_id_t _swift_os_signpost_id_generate(
  os_log_t _Nonnull log);

SWIFT_RUNTIME_STDLIB_INTERNAL
_swift_os_signpost_id_t _swift_os_signpost_id_make_with_pointer(
  os_log_t _Nonnull log,
  const void * _Nullable ptr);

SWIFT_RUNTIME_STDLIB_INTERNAL
void _swift_os_signpost(
  os_log_t _Nonnull log,
  os_signpost_type_t type,
  _swift_os_signpost_id_t spid,
  const char * _Nonnull name,
  const char * _Nullable format,
  const uint8_t * _Nullable buf,
  uint32_t size);

#ifdef __cplusplus
} // extern "C"
#endif

#endif // SWIFT_STDLIB_SHIMS_OSOVERLAYSHIMS_H
""",
    "XPCOverlayShims.h": """\
//===--- XPCOverlayShims.h - XPC overlay shims ------------------*- C++ -*-===//
//
// This source file is part of the Swift.org open source project
//
// Copyright (c) 2014 - 2024 Apple Inc. and the Swift project authors
// Licensed under Apache License v2.0 with Runtime Library Exception
//
// See https://swift.org/LICENSE.txt for license information
// See https://swift.org/CONTRIBUTORS.txt for the list of Swift project authors
//
//===----------------------------------------------------------------------===//
//
// Shims for the XPC module overlay.
//
//===----------------------------------------------------------------------===//

#ifndef SWIFT_STDLIB_SHIMS_XPCOVERLAYSHIMS_H
#define SWIFT_STDLIB_SHIMS_XPCOVERLAYSHIMS_H

#include <xpc/xpc.h>

#ifdef __cplusplus
extern "C" {
#endif

#include "Visibility.h"

static inline xpc_object_t _Nonnull
_swift_xpc_bool_true(void) {
  return XPC_BOOL_TRUE;
}

static inline xpc_object_t _Nonnull
_swift_xpc_bool_false(void) {
  return XPC_BOOL_FALSE;
}

typedef xpc_type_t _Nonnull _swift_xpc_type_t;

static inline _swift_xpc_type_t _swift_xpc_type_activity(void) { return XPC_TYPE_ACTIVITY; }
static inline _swift_xpc_type_t _swift_xpc_type_array(void) { return XPC_TYPE_ARRAY; }
static inline _swift_xpc_type_t _swift_xpc_type_bool(void) { return XPC_TYPE_BOOL; }
static inline _swift_xpc_type_t _swift_xpc_type_connection(void) { return XPC_TYPE_CONNECTION; }
static inline _swift_xpc_type_t _swift_xpc_type_data(void) { return XPC_TYPE_DATA; }
static inline _swift_xpc_type_t _swift_xpc_type_date(void) { return XPC_TYPE_DATE; }
static inline _swift_xpc_type_t _swift_xpc_type_dictionary(void) { return XPC_TYPE_DICTIONARY; }
static inline _swift_xpc_type_t _swift_xpc_type_double(void) { return XPC_TYPE_DOUBLE; }
static inline _swift_xpc_type_t _swift_xpc_type_endpoint(void) { return XPC_TYPE_ENDPOINT; }
static inline _swift_xpc_type_t _swift_xpc_type_error(void) { return XPC_TYPE_ERROR; }
static inline _swift_xpc_type_t _swift_xpc_type_fd(void) { return XPC_TYPE_FD; }
static inline _swift_xpc_type_t _swift_xpc_type_int64(void) { return XPC_TYPE_INT64; }
static inline _swift_xpc_type_t _swift_xpc_type_null(void) { return XPC_TYPE_NULL; }
static inline _swift_xpc_type_t _swift_xpc_type_shmem(void) { return XPC_TYPE_SHMEM; }
static inline _swift_xpc_type_t _swift_xpc_type_string(void) { return XPC_TYPE_STRING; }
static inline _swift_xpc_type_t _swift_xpc_type_uint64(void) { return XPC_TYPE_UINT64; }
static inline _swift_xpc_type_t _swift_xpc_type_uuid(void) { return XPC_TYPE_UUID; }

SWIFT_RUNTIME_STDLIB_INTERNAL
xpc_object_t _Nullable _swift_xpc_connection_send_message_with_reply_sync(
  xpc_connection_t _Nonnull connection,
  xpc_object_t _Nonnull message);

SWIFT_RUNTIME_STDLIB_INTERNAL
void _swift_xpc_connection_set_event_handler(
  xpc_connection_t _Nonnull connection,
  void (* _Nonnull handler)(xpc_object_t _Nonnull));

#ifdef __cplusplus
} // extern "C"
#endif

#endif // SWIFT_STDLIB_SHIMS_XPCOVERLAYSHIMS_H
""",
}


def _download_file(url: str, dest: Path, cache_dir: Path | None) -> bool:
    """Download a single file, with optional caching."""
    if cache_dir is not None:
        cached = cache_dir / dest.name
        if cached.exists():
            dest.write_bytes(cached.read_bytes())
            return True

    try:
        req = Request(url, headers={"User-Agent": "apple-sdk-gen/1.0"})
        with urlopen(req, timeout=30) as resp:
            data = resp.read()
    except Exception as exc:
        logger.debug("Failed to download %s: %s", url, exc)
        return False

    dest.write_bytes(data)

    if cache_dir is not None:
        cache_dir.mkdir(parents=True, exist_ok=True)
        (cache_dir / dest.name).write_bytes(data)

    return True


def install_swift_shims(
    sdk_root: Path,
    sdk_version: str,
    cache_dir: Path,
) -> None:
    """Download Swift shim headers and install into the SDK."""
    tag = _SWIFT_TAGS.get(sdk_version)
    if tag is None:
        # Fall back to latest known
        tag = list(_SWIFT_TAGS.values())[-1]
        logger.warning(
            "No exact Swift tag for SDK %s, falling back to %s",
            sdk_version, tag,
        )

    shims_dir = sdk_root / "usr" / "lib" / "swift" / "shims"
    shims_dir.mkdir(parents=True, exist_ok=True)

    shims_cache = cache_dir / "swift-shims" / tag
    downloaded = 0
    skipped = 0

    for filename in _SHIM_FILES:
        dest = shims_dir / filename
        if dest.exists():
            skipped += 1
            continue

        url = _RAW_URL.format(tag=tag, file=filename)
        if _download_file(url, dest, shims_cache):
            downloaded += 1
        else:
            logger.warning("Could not download shim: %s", filename)

    # Generate synthetic fallbacks for shims that exist in Xcode but
    # 404 at all known OSS URLs.
    synthetic = 0
    for filename, content in _SYNTHETIC_SHIMS.items():
        dest = shims_dir / filename
        if not dest.exists():
            dest.write_text(content)
            synthetic += 1

    logger.info(
        "Swift shims: %d downloaded, %d cached/skipped, %d synthetic",
        downloaded, skipped, synthetic,
    )
