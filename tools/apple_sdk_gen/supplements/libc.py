"""Download and install C standard library / POSIX / runtime headers from Apple OSS.

These headers populate ``<sdk>/usr/include/`` so that code using
``#include <stdio.h>``, ``#include <pthread.h>``, ``#import <objc/runtime.h>``,
``#include <dispatch/dispatch.h>`` etc. can compile against the generated SDK.

Six GitHub repositories are used:

- **apple-oss-distributions/Libc** – stdio, stdlib, string, math, …
- **apple-oss-distributions/xnu** – sys/, mach/, machine/, os/ (partial), …
- **apple-oss-distributions/libpthread** – pthread.h, sched.h
- **apple-oss-distributions/objc4** – objc/objc.h, objc/runtime.h, …
- **apple-oss-distributions/libdispatch** – dispatch/, os/object.h, …
- **apple-oss-distributions/libplatform** – os/lock.h, os/once.h, …

Matching TBD stubs are generated for libSystem.B, libobjc.A, and libdispatch.
"""

from __future__ import annotations

import logging
import zipfile
from pathlib import Path
from urllib.request import urlopen, Request

logger = logging.getLogger(__name__)

# Maps SDK version → dict of repo name → git tag.
# Tags are approximate — the exact correspondence between Apple's SDK
# versions and open-source drops is not always 1:1, but the headers
# are stable enough across minor releases.
VERSION_TAGS: dict[str, dict[str, str]] = {
    "15.0": {
        "Libc": "Libc-1534.81.1",
        "xnu": "xnu-10002.1.13",
        "libpthread": "libpthread-485.60.2",
        "objc4": "objc4-906.2",
        "libdispatch": "libdispatch-1462.0.4",
        "libplatform": "libplatform-306.0.1",
    },
    "15.2": {
        "Libc": "Libc-1534.81.1",
        "xnu": "xnu-10002.41.9",
        "libpthread": "libpthread-485.60.2",
        "objc4": "objc4-906.2",
        "libdispatch": "libdispatch-1462.80.1",
        "libplatform": "libplatform-306.0.1",
    },
    "16.0": {
        "Libc": "Libc-1583.40.7",
        "xnu": "xnu-10063.61.3",
        "libpthread": "libpthread-519.40.4",
        "objc4": "objc4-912.7",
        "libdispatch": "libdispatch-1477.100.9",
        "libplatform": "libplatform-316.100.10",
    },
    "17.0": {
        "Libc": "Libc-1583.100.4",
        "xnu": "xnu-10063.121.3",
        "libpthread": "libpthread-519.100.3",
        "objc4": "objc4-928.3",
        "libdispatch": "libdispatch-1504.60.7",
        "libplatform": "libplatform-340.60.2",
    },
    "18.0": {
        "Libc": "Libc-1583.100.4",
        "xnu": "xnu-11215.1.10",
        "libpthread": "libpthread-519.100.3",
        "objc4": "objc4-940.4",
        "libdispatch": "libdispatch-1521.100.8",
        "libplatform": "libplatform-349.140.6",
    },
    "18.2": {
        "Libc": "Libc-1583.100.4",
        "xnu": "xnu-11215.61.5",
        "libpthread": "libpthread-519.100.3",
        "objc4": "objc4-951.1",
        "libdispatch": "libdispatch-1542.0.4",
        "libplatform": "libplatform-359.60.3",
    },
}

_GITHUB_ZIP = "https://github.com/apple-oss-distributions/{repo}/archive/refs/tags/{tag}.zip"


# ── Extraction rules ────────────────────────────────────────────────
# Each entry is (src_prefix, dst_prefix) where src_prefix is relative
# to the archive root and dst_prefix is the destination under
# <sdk>/usr/include/.

_LIBC_HEADERS = [
    ("include/", ""),
]

_XNU_HEADERS = [
    # BSD sys/ headers
    ("bsd/sys/", "sys/"),
    ("bsd/machine/", "machine/"),
    ("bsd/arm/", "arm/"),
    ("bsd/i386/", "i386/"),
    ("bsd/net/", "net/"),
    ("bsd/netinet/", "netinet/"),
    ("bsd/netinet6/", "netinet6/"),
    # EXTERNAL_HEADERS — mach/, architecture/ etc.
    ("EXTERNAL_HEADERS/", ""),
    # osfmk mach headers
    ("osfmk/mach/", "mach/"),
    ("bsd/sys/_types/", "sys/_types/"),
    ("bsd/i386/_types.h", "i386/_types.h"),
    ("bsd/arm/_types.h", "arm/_types.h"),
    # os/ headers from libkern
    ("libkern/os/", "os/"),
]

_LIBPTHREAD_HEADERS = [
    ("include/pthread/", "pthread/"),
    ("include/pthread.h", "pthread.h"),
    ("include/sched.h", "sched.h"),
]

_OBJC4_HEADERS = [
    # Public ObjC runtime headers — installed into usr/include/objc/
    ("runtime/objc.h", "objc/objc.h"),
    ("runtime/runtime.h", "objc/runtime.h"),
    ("runtime/message.h", "objc/message.h"),
    ("runtime/objc-api.h", "objc/objc-api.h"),
    ("runtime/objc-auto.h", "objc/objc-auto.h"),
    ("runtime/objc-exception.h", "objc/objc-exception.h"),
    ("runtime/objc-sync.h", "objc/objc-sync.h"),
    ("runtime/NSObjCRuntime.h", "objc/NSObjCRuntime.h"),
    ("runtime/NSObject.h", "objc/NSObject.h"),
]

_LIBDISPATCH_HEADERS = [
    # dispatch/ public headers
    ("dispatch/", "dispatch/"),
    # os/ headers provided by libdispatch (object.h, clock.h, workgroup.h, etc.)
    ("os/", "os/"),
]

_LIBPLATFORM_HEADERS = [
    # os/ headers (lock.h, once.h, etc.)
    ("include/os/", "os/"),
]


def install_libc_headers(
    sdk_root: Path,
    sdk_version: str,
    tbd_targets: list[str],
    cache_dir: Path,
) -> None:
    """Download Apple OSS headers and install them into the SDK."""
    tags = VERSION_TAGS.get(sdk_version)
    if tags is None:
        # Fall back to latest known
        tags = list(VERSION_TAGS.values())[-1]
        logger.warning(
            "No exact tags for SDK %s, falling back to latest known",
            sdk_version,
        )

    usr_include = sdk_root / "usr" / "include"
    usr_include.mkdir(parents=True, exist_ok=True)

    # Download and extract each repo
    _extract_repo("Libc", tags["Libc"], _LIBC_HEADERS, usr_include, cache_dir)
    _extract_repo("xnu", tags["xnu"], _XNU_HEADERS, usr_include, cache_dir)
    _extract_repo("libpthread", tags["libpthread"], _LIBPTHREAD_HEADERS, usr_include, cache_dir)
    _extract_repo("objc4", tags["objc4"], _OBJC4_HEADERS, usr_include, cache_dir)
    _extract_repo("libdispatch", tags["libdispatch"], _LIBDISPATCH_HEADERS, usr_include, cache_dir)
    _extract_repo("libplatform", tags["libplatform"], _LIBPLATFORM_HEADERS, usr_include, cache_dir)

    # Generate TBD stubs for system libraries
    _generate_tbd_stubs(sdk_root, tbd_targets)

    logger.info("Installed system headers into %s", usr_include)


def _download_zip(repo: str, tag: str, cache_dir: Path) -> Path:
    """Download a GitHub archive zip, caching to disk."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    cached = cache_dir / f"{repo}-{tag}.zip"
    if cached.exists():
        logger.debug("Using cached %s", cached)
        return cached

    url = _GITHUB_ZIP.format(repo=repo, tag=tag)
    logger.info("Downloading %s ...", url)

    req = Request(url, headers={"User-Agent": "apple-sdk-gen/1.0"})
    with urlopen(req, timeout=120) as resp:
        data = resp.read()

    cached.write_bytes(data)
    return cached


def _extract_repo(
    repo: str,
    tag: str,
    rules: list[tuple[str, str]],
    usr_include: Path,
    cache_dir: Path,
) -> None:
    """Extract header files from a GitHub archive zip into usr/include."""
    zip_path = _download_zip(repo, tag, cache_dir)

    with zipfile.ZipFile(zip_path) as zf:
        # The archive root is "{repo}-{tag}/"
        prefix = f"{repo}-{tag}/"
        members = zf.namelist()

        for src_rule, dst_rule in rules:
            full_src = prefix + src_rule

            # Single-file rule (e.g. "runtime/objc.h" → "objc/objc.h")
            if not src_rule.endswith("/") and full_src in members:
                dst = usr_include / dst_rule
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(zf.read(full_src))
                continue

            # Directory rule — extract matching .h files
            for member in members:
                if not member.startswith(full_src):
                    continue
                if member.endswith("/"):
                    continue
                if not member.endswith(".h"):
                    continue

                rel = member[len(full_src):]
                dst = usr_include / dst_rule / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(zf.read(member))

    logger.debug("Extracted headers from %s-%s", repo, tag)


def _generate_tbd_stubs(sdk_root: Path, tbd_targets: list[str]) -> None:
    """Generate TBD stubs for system libraries."""
    usr_lib = sdk_root / "usr" / "lib"
    usr_lib.mkdir(parents=True, exist_ok=True)

    targets_str = ", ".join(tbd_targets)

    # ── libSystem.B ──────────────────────────────────────────────────
    (usr_lib / "libSystem.B.tbd").write_text(f"""\
--- !tapi-tbd
tbd-version:     4
targets:         [{targets_str}]
install-name:    '/usr/lib/libSystem.B.dylib'
current-version: 1345.100.2
exports:
  - targets:     [{targets_str}]
    re-exports:
      - '/usr/lib/system/libsystem_c.dylib'
      - '/usr/lib/system/libsystem_kernel.dylib'
      - '/usr/lib/system/libsystem_malloc.dylib'
      - '/usr/lib/system/libsystem_pthread.dylib'
      - '/usr/lib/system/libsystem_platform.dylib'
      - '/usr/lib/system/libsystem_info.dylib'
      - '/usr/lib/system/libdyld.dylib'
      - '/usr/lib/system/libsystem_blocks.dylib'
      - '/usr/lib/system/libsystem_darwin.dylib'
      - '/usr/lib/system/libsystem_m.dylib'
      - '/usr/lib/system/libsystem_trace.dylib'
      - '/usr/lib/system/libxpc.dylib'
      - '/usr/lib/system/libdispatch.dylib'
      - '/usr/lib/system/libcorecrypto.dylib'
      - '/usr/lib/system/libcommonCrypto.dylib'
      - '/usr/lib/system/libsystem_asl.dylib'
      - '/usr/lib/system/libsystem_notify.dylib'
      - '/usr/lib/system/libsystem_sandbox.dylib'
      - '/usr/lib/system/libcompiler_rt.dylib'
      - '/usr/lib/system/libcopyfile.dylib'
      - '/usr/lib/system/libremovefile.dylib'
      - '/usr/lib/system/libmacho.dylib'
...
""")

    # ── libc (re-exports libSystem) ──────────────────────────────────
    (usr_lib / "libc.tbd").write_text(f"""\
--- !tapi-tbd
tbd-version:     4
targets:         [{targets_str}]
install-name:    '/usr/lib/libc.dylib'
current-version: 1345.100.2
exports:
  - targets:     [{targets_str}]
    re-exports:
      - '/usr/lib/libSystem.B.dylib'
...
""")

    # ── libobjc.A ────────────────────────────────────────────────────
    (usr_lib / "libobjc.A.tbd").write_text(f"""\
--- !tapi-tbd
tbd-version:     4
targets:         [{targets_str}]
install-name:    '/usr/lib/libobjc.A.dylib'
current-version: 228.0.0
exports:
  - targets:     [{targets_str}]
    symbols:
      - _objc_msgSend
      - _objc_msgSendSuper
      - _objc_msgSendSuper2
      - _objc_msgSend_stret
      - _objc_msgSendSuper_stret
      - _objc_alloc
      - _objc_alloc_init
      - _objc_allocWithZone
      - _objc_autoreleasePoolPush
      - _objc_autoreleasePoolPop
      - _objc_autorelease
      - _objc_autoreleaseReturnValue
      - _objc_retainAutoreleasedReturnValue
      - _objc_unsafeClaimAutoreleasedReturnValue
      - _objc_retain
      - _objc_release
      - _objc_storeStrong
      - _objc_storeWeak
      - _objc_loadWeakRetained
      - _objc_destroyWeak
      - _objc_initWeak
      - _objc_moveWeak
      - _objc_copyWeak
      - _objc_retainBlock
      - _objc_getAssociatedObject
      - _objc_setAssociatedObject
      - _objc_removeAssociatedObjects
      - _objc_getClass
      - _objc_getMetaClass
      - _objc_lookUpClass
      - _objc_getProtocol
      - _objc_getRequiredClass
      - _objc_enumerationMutation
      - _objc_setEnumerationMutationHandler
      - _objc_constructInstance
      - _objc_destructInstance
      - _objc_registerClassPair
      - _objc_allocateClassPair
      - _objc_disposeClassPair
      - _objc_duplicateClass
      - _objc_setProperty
      - _objc_getProperty
      - _objc_copyStruct
      - _objc_opt_self
      - _objc_opt_class
      - _objc_opt_isKindOfClass
      - _objc_opt_respondsToSelector
      - _objc_opt_new
      - _objc_exception_throw
      - _objc_exception_rethrow
      - _objc_begin_catch
      - _objc_end_catch
      - _objc_terminate
      - _objc_sync_enter
      - _objc_sync_exit
      - _object_getClass
      - _object_setClass
      - _object_getClassName
      - _object_getIndexedIvars
      - _object_getIvar
      - _object_setIvar
      - _class_getName
      - _class_getSuperclass
      - _class_isMetaClass
      - _class_getInstanceSize
      - _class_getInstanceVariable
      - _class_getClassVariable
      - _class_getInstanceMethod
      - _class_getClassMethod
      - _class_getMethodImplementation
      - _class_respondsToSelector
      - _class_conformsToProtocol
      - _class_copyMethodList
      - _class_copyPropertyList
      - _class_copyIvarList
      - _class_copyProtocolList
      - _class_addMethod
      - _class_replaceMethod
      - _class_addIvar
      - _class_addProtocol
      - _class_addProperty
      - _class_getProperty
      - _class_createInstance
      - _method_getName
      - _method_getImplementation
      - _method_setImplementation
      - _method_exchangeImplementations
      - _method_getTypeEncoding
      - _method_getNumberOfArguments
      - _method_copyReturnType
      - _method_copyArgumentType
      - _method_getDescription
      - _ivar_getName
      - _ivar_getTypeEncoding
      - _ivar_getOffset
      - _property_getName
      - _property_getAttributes
      - _property_copyAttributeList
      - _property_copyAttributeValue
      - _protocol_getName
      - _protocol_conformsToProtocol
      - _protocol_getMethodDescription
      - _protocol_copyMethodDescriptionList
      - _protocol_copyPropertyList
      - _protocol_copyProtocolList
      - _sel_getName
      - _sel_registerName
      - _sel_isEqual
      - _NSSelectorFromString
      - _NSStringFromSelector
      - _NSClassFromString
      - _NSStringFromClass
      - _NSLog
      - _NSLogv
    objc-classes:
      - _NSObject
      - _NSProxy
      - _NSAutoreleasePool
      - _Protocol
...
""")

    # ── libobjc (re-exports libobjc.A) ───────────────────────────────
    (usr_lib / "libobjc.tbd").write_text(f"""\
--- !tapi-tbd
tbd-version:     4
targets:         [{targets_str}]
install-name:    '/usr/lib/libobjc.dylib'
current-version: 228.0.0
exports:
  - targets:     [{targets_str}]
    re-exports:
      - '/usr/lib/libobjc.A.dylib'
...
""")

    # ── libdispatch ──────────────────────────────────────────────────
    (usr_lib / "libdispatch.tbd").write_text(f"""\
--- !tapi-tbd
tbd-version:     4
targets:         [{targets_str}]
install-name:    '/usr/lib/system/libdispatch.dylib'
current-version: 1325.100.2
exports:
  - targets:     [{targets_str}]
    symbols:
      - _dispatch_async
      - _dispatch_async_f
      - _dispatch_sync
      - _dispatch_sync_f
      - _dispatch_after
      - _dispatch_after_f
      - _dispatch_apply
      - _dispatch_apply_f
      - _dispatch_barrier_async
      - _dispatch_barrier_async_f
      - _dispatch_barrier_sync
      - _dispatch_barrier_sync_f
      - _dispatch_group_create
      - _dispatch_group_async
      - _dispatch_group_async_f
      - _dispatch_group_enter
      - _dispatch_group_leave
      - _dispatch_group_notify
      - _dispatch_group_notify_f
      - _dispatch_group_wait
      - _dispatch_semaphore_create
      - _dispatch_semaphore_wait
      - _dispatch_semaphore_signal
      - _dispatch_once
      - _dispatch_once_f
      - _dispatch_queue_create
      - _dispatch_queue_create_with_target
      - _dispatch_queue_get_label
      - _dispatch_get_main_queue
      - _dispatch_get_global_queue
      - _dispatch_main
      - _dispatch_time
      - _dispatch_walltime
      - _dispatch_source_create
      - _dispatch_source_set_event_handler
      - _dispatch_source_set_event_handler_f
      - _dispatch_source_set_cancel_handler
      - _dispatch_source_set_cancel_handler_f
      - _dispatch_source_cancel
      - _dispatch_source_get_data
      - _dispatch_source_get_handle
      - _dispatch_source_get_mask
      - _dispatch_source_merge_data
      - _dispatch_source_set_timer
      - _dispatch_data_create
      - _dispatch_data_get_size
      - _dispatch_data_create_map
      - _dispatch_data_apply
      - _dispatch_data_create_subrange
      - _dispatch_data_create_concat
      - _dispatch_data_copy_region
      - _dispatch_io_create
      - _dispatch_io_read
      - _dispatch_io_write
      - _dispatch_io_close
      - _dispatch_io_set_high_water
      - _dispatch_io_set_low_water
      - _dispatch_io_set_interval
      - _dispatch_read
      - _dispatch_write
      - _dispatch_retain
      - _dispatch_release
      - _dispatch_set_target_queue
      - _dispatch_set_finalizer_f
      - _dispatch_suspend
      - _dispatch_resume
      - _dispatch_activate
      - _dispatch_assert_queue
      - _dispatch_assert_queue_barrier
      - _dispatch_assert_queue_not
      - _dispatch_block_create
      - _dispatch_block_create_with_qos_class
      - _dispatch_block_perform
      - _dispatch_block_wait
      - _dispatch_block_notify
      - _dispatch_block_cancel
      - _dispatch_block_testcancel
      - _dispatch_workloop_create
      - _dispatch_workloop_create_inactive
      - _dispatch_workloop_set_autorelease_frequency
      - _dispatch_queue_attr_make_with_qos_class
      - _dispatch_queue_attr_make_initially_inactive
      - _dispatch_queue_attr_make_with_autorelease_frequency
    symbols:
      - _dispatch_data_empty
      - __dispatch_main_q
      - __dispatch_source_type_data_add
      - __dispatch_source_type_data_or
      - __dispatch_source_type_data_replace
      - __dispatch_source_type_mach_recv
      - __dispatch_source_type_mach_send
      - __dispatch_source_type_memorypressure
      - __dispatch_source_type_proc
      - __dispatch_source_type_read
      - __dispatch_source_type_signal
      - __dispatch_source_type_timer
      - __dispatch_source_type_vnode
      - __dispatch_source_type_write
...
""")

    logger.debug("Generated system library TBD stubs")
