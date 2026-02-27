"""Generate Clang module maps for system headers in usr/include/.

Without these, ``@import Darwin`` and ``import Darwin`` in Swift fail.
Module maps are generated conditionally — only headers that actually exist
in the SDK get submodule entries.
"""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# ── POSIX / BSD headers that belong in the Darwin umbrella ──────────
_POSIX_HEADERS = [
    "aio.h", "arpa/inet.h", "assert.h", "complex.h", "cpio.h", "ctype.h",
    "dirent.h", "dlfcn.h", "errno.h", "fcntl.h", "fenv.h", "float.h",
    "fnmatch.h", "ftw.h", "glob.h", "grp.h", "iconv.h", "ifaddrs.h",
    "inttypes.h", "iso646.h", "langinfo.h", "libgen.h", "limits.h",
    "locale.h", "math.h", "monetary.h", "net/if.h", "netdb.h",
    "netinet/in.h", "netinet/tcp.h", "nl_types.h", "poll.h", "pthread.h",
    "pwd.h", "regex.h", "sched.h", "search.h", "semaphore.h", "setjmp.h",
    "signal.h", "spawn.h", "stdalign.h", "stdarg.h", "stdbool.h",
    "stddef.h", "stdint.h", "stdio.h", "stdlib.h", "string.h",
    "strings.h", "sys/ioctl.h", "sys/ipc.h", "sys/mman.h", "sys/msg.h",
    "sys/param.h", "sys/resource.h", "sys/select.h", "sys/sem.h",
    "sys/shm.h", "sys/signal.h", "sys/socket.h", "sys/stat.h",
    "sys/statvfs.h", "sys/sysctl.h", "sys/syslog.h", "sys/time.h",
    "sys/times.h", "sys/types.h", "sys/uio.h", "sys/un.h", "sys/utsname.h",
    "sys/wait.h", "syslog.h", "tar.h", "termios.h", "time.h", "ucontext.h",
    "unistd.h", "utime.h", "utmpx.h", "wchar.h", "wctype.h", "wordexp.h",
    "xlocale.h",
]

# Additional C stdlib / Apple-specific headers
_C_HEADERS = [
    "alloca.h", "bank/bank_types.h", "Block.h", "checkint.h",
    "CommonCrypto/CommonCrypto.h", "copyfile.h", "err.h", "fts.h",
    "getopt.h", "libkern/OSAtomic.h", "libkern/OSByteOrder.h",
    "mach/mach.h", "mach/mach_time.h", "mach-o/dyld.h", "mach-o/getsect.h",
    "mach-o/loader.h", "mach-o/nlist.h", "malloc/malloc.h", "membership.h",
    "nameser.h", "ndbm.h", "notify.h", "os/log.h", "os/signpost.h",
    "os/activity.h", "readpassphrase.h", "removefile.h", "resolv.h",
    "sandbox.h", "sys/acl.h", "sys/attr.h", "sys/clonefile.h",
    "sys/event.h", "sys/fcntl.h", "sys/file.h", "sys/kern_control.h",
    "sys/mount.h", "sys/proc_info.h", "sys/ptrace.h", "sys/queue.h",
    "sys/quota.h", "sys/random.h", "sys/syscall.h", "sys/syslimits.h",
    "sys/xattr.h", "sysexits.h", "TargetConditionals.h", "uuid/uuid.h",
    "vis.h",
]


def _header_module_name(header: str) -> str:
    """Derive a Clang submodule name from a header path.

    ``sys/types.h`` → ``sys_types``, ``stdio.h`` → ``stdio``.
    """
    return header.removesuffix(".h").replace("/", "_").replace("-", "_").replace(".", "_")


def _generate_darwin_modulemap(usr_include: Path) -> str:
    """Build the top-level Darwin module.modulemap."""
    lines = [
        'module Darwin [system] [extern_c] {',
    ]

    # POSIX submodules
    for hdr in _POSIX_HEADERS:
        if (usr_include / hdr).exists():
            name = _header_module_name(hdr)
            lines.append(f'  module {name} {{')
            lines.append(f'    header "{hdr}"')
            lines.append(f'    export *')
            lines.append(f'  }}')

    # C / Apple-specific submodules
    for hdr in _C_HEADERS:
        if (usr_include / hdr).exists():
            name = _header_module_name(hdr)
            lines.append(f'  module {name} {{')
            lines.append(f'    header "{hdr}"')
            lines.append(f'    export *')
            lines.append(f'  }}')

    # Catch-all for sys/cdefs.h, _types.h etc. that aren't explicitly listed
    lines.append('')
    lines.append('  // Machine / internal type headers')
    for sub in ("sys/_types.h", "sys/cdefs.h", "machine/types.h",
                "machine/endian.h", "arm/_types.h", "i386/_types.h",
                "secure/_common.h", "secure/_stdio.h", "secure/_string.h"):
        if (usr_include / sub).exists():
            name = _header_module_name(sub)
            lines.append(f'  module {name} {{')
            lines.append(f'    header "{sub}"')
            lines.append(f'    export *')
            lines.append(f'  }}')

    # Link directives for common system libraries
    lines.append('')
    lines.append('  link "System"')

    lines.append('}')
    lines.append('')

    # SQLite3 module (separate from Darwin)
    if (usr_include / "sqlite3.h").exists():
        lines.append('module SQLite3 [system] {')
        lines.append('  header "sqlite3.h"')
        lines.append('  link "sqlite3"')
        lines.append('  export *')
        lines.append('}')
        lines.append('')

    # libxml2 module
    libxml2_dir = usr_include / "libxml2"
    if libxml2_dir.is_dir():
        lines.append('module libxml2 [system] {')
        lines.append('  umbrella "libxml2"')
        lines.append('  link "xml2"')
        lines.append('  export *')
        lines.append('}')
        lines.append('')

    # zlib module
    if (usr_include / "zlib.h").exists():
        lines.append('module zlib [system] {')
        lines.append('  header "zlib.h"')
        lines.append('  link "z"')
        lines.append('  export *')
        lines.append('}')
        lines.append('')

    return "\n".join(lines)


def _generate_dispatch_modulemap(usr_include: Path) -> str | None:
    """Generate usr/include/dispatch/module.modulemap."""
    dispatch_dir = usr_include / "dispatch"
    if not dispatch_dir.is_dir():
        return None

    headers = sorted(p.name for p in dispatch_dir.glob("*.h"))
    if not headers:
        return None

    lines = [
        'module Dispatch [system] {',
    ]
    for h in headers:
        if h == "module.modulemap":
            continue
        lines.append(f'  header "{h}"')
    lines.append('  link "dispatch"')
    lines.append('  export *')
    lines.append('}')
    lines.append('')
    return "\n".join(lines)


def _generate_objc_modulemap(usr_include: Path) -> str | None:
    """Generate usr/include/objc/module.modulemap."""
    objc_dir = usr_include / "objc"
    if not objc_dir.is_dir():
        return None

    headers = sorted(p.name for p in objc_dir.glob("*.h"))
    if not headers:
        return None

    lines = [
        'module ObjectiveC [system] {',
    ]
    for h in headers:
        lines.append(f'  header "{h}"')
    lines.append('  link "objc"')
    lines.append('  export *')
    lines.append('}')
    lines.append('')
    return "\n".join(lines)


def _generate_os_modulemap(usr_include: Path) -> str | None:
    """Generate usr/include/os/module.modulemap."""
    os_dir = usr_include / "os"
    if not os_dir.is_dir():
        return None

    headers = sorted(p.name for p in os_dir.glob("*.h"))
    if not headers:
        return None

    lines = [
        'module os [system] {',
    ]
    for h in headers:
        lines.append(f'  header "{h}"')
    lines.append('  export *')
    lines.append('}')
    lines.append('')
    return "\n".join(lines)


def _generate_conditional_modulemap(
    usr_include: Path,
    dirname: str,
    module_name: str,
) -> str | None:
    """Generate a modulemap for an optional subdirectory."""
    target_dir = usr_include / dirname
    if not target_dir.is_dir():
        return None

    headers = sorted(p.name for p in target_dir.glob("*.h"))
    if not headers:
        return None

    lines = [
        f'module {module_name} [system] {{',
    ]
    for h in headers:
        lines.append(f'  header "{h}"')
    lines.append('  export *')
    lines.append('}')
    lines.append('')
    return "\n".join(lines)


def install_system_modulemaps(sdk_root: Path) -> None:
    """Generate Clang module maps for system headers already present in the SDK."""
    usr_include = sdk_root / "usr" / "include"
    if not usr_include.is_dir():
        logger.warning("No usr/include directory; skipping modulemaps")
        return

    generated = 0

    # 1. Main Darwin modulemap
    darwin_mm = _generate_darwin_modulemap(usr_include)
    (usr_include / "module.modulemap").write_text(darwin_mm)
    generated += 1

    # 2. dispatch/module.modulemap
    dispatch_mm = _generate_dispatch_modulemap(usr_include)
    if dispatch_mm:
        (usr_include / "dispatch" / "module.modulemap").write_text(dispatch_mm)
        generated += 1

    # 3. objc/module.modulemap
    objc_mm = _generate_objc_modulemap(usr_include)
    if objc_mm:
        (usr_include / "objc" / "module.modulemap").write_text(objc_mm)
        generated += 1

    # 4. os/module.modulemap
    os_mm = _generate_os_modulemap(usr_include)
    if os_mm:
        (usr_include / "os" / "module.modulemap").write_text(os_mm)
        generated += 1

    # 5. Conditional modulemaps for optional directories
    _OPTIONAL_MODULES = [
        ("CommonCrypto", "CommonCrypto"),
        ("simd", "simd"),
        ("Spatial", "Spatial"),
        ("xpc", "xpc"),
    ]
    for dirname, module_name in _OPTIONAL_MODULES:
        mm = _generate_conditional_modulemap(usr_include, dirname, module_name)
        if mm:
            (usr_include / dirname / "module.modulemap").write_text(mm)
            generated += 1

    logger.info("Generated %d system module maps", generated)
