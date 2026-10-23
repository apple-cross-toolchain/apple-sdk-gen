from __future__ import annotations

import gzip
import hashlib
import io
import logging
import os
import shutil
import stat
import struct
import xml.etree.ElementTree as ElementTree
import zlib
from pathlib import Path
from urllib.request import Request, urlopen

from ..config import PLATFORM_CONFIGS, tbd_target_name, tbd_targets_for_platform
from ..generators.tbd import tbd_document

logger = logging.getLogger(__name__)

PACKAGE_URL = "https://download.swift.org/swift-{0}-release/xcode/swift-{0}-RELEASE/swift-{0}-RELEASE-osx.pkg"
PACKAGE_SHA256 = {
    "6.4.0": "8fd03185b98fe27f54a54631c2449decf75d5b466ce8e34abbd414141063c6aa",
}
PLATFORM_DIRS = {key: cfg.sdk_prefix.lower() for key, cfg in PLATFORM_CONFIGS.items()}
SKIPPED_SUFFIXES = (
    ".abi.json",
    ".swiftmodule",
    ".package.swiftinterface",
    ".private.swiftinterface",
    ".swiftdoc",
    ".swiftsourceinfo",
)
TOOLCHAIN_ENTRIES = ("Cxx.swiftmodule", "CxxStdlib.swiftmodule")
TOOLCHAIN_SUFFIXES = (".a", ".h", ".modulemap", ".yaml")
TOOLCHAIN_PLACEHOLDERS = ("libLiveExecutionResultsLogger", "libPlaygrounds")
OBJC_PREFIXES = (("_OBJC_CLASS_$_", "objc-classes"), ("_OBJC_EHTYPE_$_", "objc-eh-types"), ("_OBJC_IVAR_$_", "objc-ivars"))
EXPORT_KIND_MASK = 0x03
EXPORT_THREAD_LOCAL = 0x01
EXPORT_WEAK = 0x04
FAT_MAGIC = 0xCAFEBABE
FAT_MAGIC_64 = 0xCAFEBABF
MH_MAGIC = 0xFEEDFACE
MH_MAGIC_64 = 0xFEEDFACF
MH_APP_EXTENSION_SAFE = 0x02000000
LC_SEGMENT = 0x1
LC_ID_DYLIB = 0xD
LC_SEGMENT_64 = 0x19
LC_DYLD_INFO = 0x22
LC_REEXPORT_DYLIB = 0x8000001F
LC_DYLD_INFO_ONLY = 0x80000022
LC_DYLD_EXPORTS_TRIE = 0x80000033
ARCHS = {
    (0x01000007, 3): "x86_64",
    (0x01000007, 8): "x86_64h",
    (0x0100000C, 0): "arm64",
    (0x0100000C, 1): "arm64",
    (0x0100000C, 2): "arm64e",
    (0x0200000C, 1): "arm64_32",
}


class PackageError(Exception):
    pass


class _Region(io.RawIOBase):
    def __init__(self, f, offset: int, length: int):
        self.f = f
        self.position = offset
        self.end = offset + length

    def readable(self) -> bool:
        return True

    def readinto(self, buffer) -> int:
        size = min(len(buffer), self.end - self.position)
        if size <= 0:
            return 0
        self.f.seek(self.position)
        data = self.f.read(size)
        buffer[: len(data)] = data
        self.position += len(data)
        return len(data)


class _Inflater(io.RawIOBase):
    def __init__(self, raw):
        self.raw = raw
        self.decompressor = zlib.decompressobj()
        self.pending = b""

    def readable(self) -> bool:
        return True

    def readinto(self, buffer) -> int:
        while not self.pending:
            chunk = self.raw.read(1 << 20)
            if not chunk:
                self.pending = self.decompressor.flush()
                break
            self.pending = self.decompressor.decompress(chunk)
        size = min(len(buffer), len(self.pending))
        buffer[:size] = self.pending[:size]
        self.pending = self.pending[size:]
        return size


def _xar_entries(f) -> dict[str, tuple[int, int, str]]:
    magic, header_size, _, toc_compressed, _, _ = struct.unpack(">4sHHQQI", f.read(28))
    if magic != b"xar!":
        raise PackageError("not a xar archive")
    f.seek(header_size)
    toc = ElementTree.fromstring(zlib.decompress(f.read(toc_compressed)))
    heap = header_size + toc_compressed
    entries: dict[str, tuple[int, int, str]] = {}

    def walk(element, prefix):
        for child in element.findall("file"):
            path = prefix + child.findtext("name")
            data = child.find("data")
            if data is not None:
                entries[path] = (
                    heap + int(data.findtext("offset")),
                    int(data.findtext("length")),
                    data.find("encoding").get("style"),
                )
            walk(child, path + "/")

    walk(toc.find("toc"), "")
    return entries


def _read_exact(stream, size: int) -> bytes:
    chunks = []
    while size:
        chunk = stream.read(min(size, 1 << 20))
        if not chunk:
            raise PackageError("truncated cpio archive")
        chunks.append(chunk)
        size -= len(chunk)
    return b"".join(chunks)


def _skip(stream, size: int) -> None:
    while size:
        chunk = stream.read(min(size, 1 << 20))
        if not chunk:
            raise PackageError("truncated cpio archive")
        size -= len(chunk)


def _cpio_entries(stream):
    while True:
        magic = _read_exact(stream, 6)
        if magic == b"070707":
            header = _read_exact(stream, 70)
            ino = (int(header[0:6], 8), int(header[6:12], 8))
            mode = int(header[12:18], 8)
            namesize = int(header[53:59], 8)
            filesize = int(header[59:70], 8)
            name = _read_exact(stream, namesize)[:-1].decode()
            data_pad = 0
        elif magic in (b"070701", b"070702"):
            header = _read_exact(stream, 104)
            fields = [int(header[i : i + 8], 16) for i in range(0, 104, 8)]
            ino = (fields[7], fields[8], fields[0])
            mode = fields[1]
            filesize = fields[6]
            namesize = fields[11]
            name = _read_exact(stream, namesize)[:-1].decode()
            _skip(stream, (4 - (110 + namesize) % 4) % 4)
            data_pad = (4 - filesize % 4) % 4
        else:
            raise PackageError("unsupported cpio format")
        if name == "TRAILER!!!":
            return
        yield name, mode, ino, filesize
        _skip(stream, data_pad)


def _wanted(path: str) -> bool:
    parts = path.split("/")
    if parts[-1].startswith("._") or path.endswith(SKIPPED_SUFFIXES) or len(parts) < 4 or parts[:2] != ["usr", "lib"]:
        return False
    if parts[2] == "swift":
        return parts[3] in ("clang", "shims") or parts[3] in PLATFORM_DIRS.values()
    if parts[2] == "clang" and len(parts) >= 6:
        if parts[4] == "include":
            return True
        return parts[4:6] == ["lib", "darwin"] and len(parts) == 7 and not path.endswith(".dylib")
    return False


def _extract_payload(package: Path, destination: Path) -> None:
    with open(package, "rb") as f:
        payloads = [entry for path, entry in _xar_entries(f).items() if path.endswith(".pkg/Payload")]
        if not payloads:
            raise PackageError(f"{package} has no package payload")
        for offset, length, encoding in payloads:
            raw = io.BufferedReader(_Region(f, offset, length), 1 << 20)
            if encoding == "application/x-gzip":
                raw = io.BufferedReader(_Inflater(raw), 1 << 20)
            elif encoding != "application/octet-stream":
                raise PackageError("unsupported payload encoding " + encoding)
            if raw.peek(2)[:2] != b"\x1f\x8b":
                raise PackageError("unsupported payload compression")
            _extract_cpio(gzip.GzipFile(fileobj=raw), destination)


def _extract_cpio(stream, destination: Path) -> None:
    links: dict[tuple, Path] = {}
    for name, mode, ino, size in _cpio_entries(stream):
        path = os.path.normpath(name)
        if not _wanted(path):
            _skip(stream, size)
            continue
        target = destination / path
        if stat.S_ISDIR(mode):
            target.mkdir(parents=True, exist_ok=True)
            _skip(stream, size)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if stat.S_ISLNK(mode):
            os.symlink(_read_exact(stream, size).decode(), target)
        elif stat.S_ISREG(mode):
            if size == 0 and ino in links:
                shutil.copyfile(links[ino], target)
            else:
                with open(target, "wb") as out:
                    remaining = size
                    while remaining:
                        chunk = stream.read(min(remaining, 1 << 20))
                        if not chunk:
                            raise PackageError("truncated cpio archive")
                        out.write(chunk)
                        remaining -= len(chunk)
                if size:
                    links[ino] = target
            os.chmod(target, (mode & 0o755) | 0o644)
        else:
            _skip(stream, size)


def _uleb128(data: bytes, offset: int) -> tuple[int, int]:
    value = shift = 0
    while True:
        byte = data[offset]
        offset += 1
        value |= (byte & 0x7F) << shift
        shift += 7
        if byte < 0x80:
            return value, offset


def _trie_symbols(trie: bytes) -> list[tuple[str, int]]:
    symbols = []
    pending = [(0, b"")] if trie else []
    while pending:
        node, prefix = pending.pop()
        size, offset = _uleb128(trie, node)
        if size:
            symbols.append((prefix.decode(), _uleb128(trie, offset)[0]))
        offset += size
        count = trie[offset]
        offset += 1
        for _ in range(count):
            end = trie.index(b"\0", offset)
            edge = trie[offset:end]
            child, offset = _uleb128(trie, end + 1)
            pending.append((child, prefix + edge))
    return symbols


def _export_groups(trie: bytes) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {
        "symbols": [],
        "objc-classes": [],
        "objc-eh-types": [],
        "objc-ivars": [],
        "weak-symbols": [],
        "thread-local-symbols": [],
    }
    for name, flags in _trie_symbols(trie):
        if name.startswith("_OBJC_METACLASS_$_"):
            continue
        for prefix, key in OBJC_PREFIXES:
            if name.startswith(prefix):
                groups[key].append(name[len(prefix) :])
                break
        else:
            if flags & EXPORT_WEAK:
                groups["weak-symbols"].append(name)
            elif flags & EXPORT_KIND_MASK == EXPORT_THREAD_LOCAL:
                groups["thread-local-symbols"].append(name)
            else:
                groups["symbols"].append(name)
    return {key: sorted(values) for key, values in groups.items()}


def _packed_version(value: int) -> str:
    return "{}.{}.{}".format(value >> 16, (value >> 8) & 0xFF, value & 0xFF)


def _macho_images(data: bytes) -> list[bytes]:
    magic = struct.unpack_from(">I", data)[0]
    if magic not in (FAT_MAGIC, FAT_MAGIC_64):
        return [data]
    images = []
    for index in range(struct.unpack_from(">I", data, 4)[0]):
        if magic == FAT_MAGIC_64:
            _, _, offset, size = struct.unpack_from(">iiQQ", data, 8 + index * 32)
        else:
            _, _, offset, size = struct.unpack_from(">iiII", data, 8 + index * 20)
        images.append(data[offset : offset + size])
    return images


def _read_dylib(path: Path) -> list[dict]:
    data = path.read_bytes()
    dylibs = []
    for image in _macho_images(data):
        magic, cputype, cpusubtype, _, ncmds, _, flags = struct.unpack_from("<IiIIIII", image)
        if magic not in (MH_MAGIC, MH_MAGIC_64):
            raise PackageError(f"{path} is not a Mach-O file")
        arch = ARCHS.get((cputype, cpusubtype & 0xFFFFFF))
        if not arch:
            continue
        dylib = {"arch": arch, "reexports": [], "safe": bool(flags & MH_APP_EXTENSION_SAFE), "swift_abi": 0, "trie": b""}
        offset = 32 if magic == MH_MAGIC_64 else 28
        for _ in range(ncmds):
            cmd, size = struct.unpack_from("<II", image, offset)
            if cmd in (LC_ID_DYLIB, LC_REEXPORT_DYLIB):
                name_offset, _, current, compatibility = struct.unpack_from("<IIII", image, offset + 8)
                name = image[offset + name_offset : offset + size].split(b"\0", 1)[0].decode()
                if cmd == LC_ID_DYLIB:
                    dylib["install_name"] = name
                    dylib["versions"] = (_packed_version(current), _packed_version(compatibility))
                else:
                    dylib["reexports"].append(name)
            elif cmd in (LC_DYLD_INFO, LC_DYLD_INFO_ONLY):
                start, length = struct.unpack_from("<II", image, offset + 40)
                dylib["trie"] = image[start : start + length]
            elif cmd == LC_DYLD_EXPORTS_TRIE:
                start, length = struct.unpack_from("<II", image, offset + 8)
                dylib["trie"] = image[start : start + length]
            elif cmd in (LC_SEGMENT, LC_SEGMENT_64):
                wide = cmd == LC_SEGMENT_64
                section = offset + (72 if wide else 56)
                for _ in range(struct.unpack_from("<I", image, offset + (64 if wide else 48))[0]):
                    if image[section : section + 16].rstrip(b"\0") == b"__objc_imageinfo":
                        start = struct.unpack_from("<I", image, section + (48 if wide else 40))[0]
                        dylib["swift_abi"] = (struct.unpack_from("<I", image, start + 4)[0] >> 8) & 0xFF
                    section += 80 if wide else 68
            offset += size
        dylibs.append(dylib)
    if not dylibs:
        raise PackageError(f"{path} has no slice for a known architecture")
    return dylibs


def _stubify(source: Path, destination: Path, platform_key: str) -> None:
    if destination.exists() or destination.is_symlink():
        destination.unlink()
    if source.is_symlink():
        os.symlink(os.readlink(source)[: -len(".dylib")] + ".tbd", destination)
        return
    dylibs = _read_dylib(source)
    targets = [tbd_target_name(platform_key, dylib["arch"]) for dylib in dylibs]
    exports: list[tuple[list[str], dict[str, list[str]]]] = []
    for target, dylib in zip(targets, dylibs):
        groups = _export_groups(dylib["trie"])
        for entry_targets, entry_groups in exports:
            if entry_groups == groups:
                entry_targets.append(target)
                break
        else:
            exports.append(([target], groups))
    first = dylibs[0]
    destination.write_text(tbd_document(
        targets,
        first["install_name"],
        exports=exports,
        current_version=first["versions"][0],
        compatibility_version=first["versions"][1],
        reexports=first["reexports"],
        flags=[] if first["safe"] else ["not_app_extension_safe"],
        swift_abi_version=first["swift_abi"],
    ))


def _runtime_module(name: str, entries: set[str]) -> bool:
    library = "Core" if name == "Swift" else name
    return f"libswift{library}.dylib" in entries


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _download(url: str, destination: Path) -> None:
    request = Request(url, headers={"User-Agent": "apple-sdk-gen/1.0"})
    with urlopen(request, timeout=120) as response, open(destination, "wb") as out:
        shutil.copyfileobj(response, out, 1 << 20)


def _replace(source: Path, destination: Path) -> None:
    if destination.is_symlink() or destination.is_file():
        destination.unlink()
    elif destination.is_dir():
        shutil.rmtree(destination)
    if source.is_dir() and not source.is_symlink():
        shutil.copytree(source, destination, symlinks=True)
    else:
        shutil.copy2(source, destination, follow_symlinks=False)


class SwiftRuntime:
    def __init__(self, root: Path):
        self.root = root

    @classmethod
    def from_package(cls, version: str, package: Path | None, sha256: str | None, work_dir: Path) -> SwiftRuntime:
        expected = sha256 or PACKAGE_SHA256.get(version)
        if package is None:
            package = work_dir / f"swift-{version}-RELEASE-osx.pkg"
            url = PACKAGE_URL.format(version)
            logger.info("Downloading %s", url)
            _download(url, package)
        if expected:
            digest = _sha256(package)
            if digest != expected:
                raise PackageError(f"{package} has sha256 {digest}, expected {expected}")
        else:
            logger.warning("No sha256 is known for Swift %s; %s is not verified", version, package)
        root = work_dir / "swift"
        _extract_payload(package, root)
        logger.info("Extracted the Swift %s Darwin runtime from %s", version, package)
        return cls(root)

    def install_toolchain(self, output_dir: Path, platform_keys: list[str]) -> None:
        toolchain = output_dir / "Xcode.app" / "Contents" / "Developer" / "Toolchains" / "XcodeDefault.xctoolchain"
        for directory in ("usr/bin", "usr/include", "usr/lib/swift"):
            (toolchain / directory).mkdir(parents=True, exist_ok=True)
        _replace(self.root / "usr" / "lib" / "clang", toolchain / "usr" / "lib" / "clang")
        clang_link = self.root / "usr" / "lib" / "swift" / "clang"
        if clang_link.is_symlink():
            _replace(clang_link, toolchain / "usr" / "lib" / "swift" / "clang")
        for platform_key in platform_keys:
            platform_dir = PLATFORM_DIRS[platform_key]
            source = self.root / "usr" / "lib" / "swift" / platform_dir
            if not source.is_dir():
                logger.warning("The Swift package has no %s runtime", platform_dir)
                continue
            destination = toolchain / "usr" / "lib" / "swift" / platform_dir
            destination.mkdir(parents=True, exist_ok=True)
            for entry in sorted(os.listdir(source)):
                if entry in TOOLCHAIN_ENTRIES or entry.endswith(TOOLCHAIN_SUFFIXES):
                    _replace(source / entry, destination / entry)
            targets = tbd_targets_for_platform(platform_key)
            for name in TOOLCHAIN_PLACEHOLDERS:
                (destination / f"{name}.tbd").write_text(tbd_document(targets, f"/usr/lib/swift/{name}.dylib"))
        logger.info("Installed the clang resource directory and Swift toolchain libraries")

    def install_sdk(self, sdk_root: Path, platform_key: str) -> None:
        platform_dir = PLATFORM_DIRS[platform_key]
        source = self.root / "usr" / "lib" / "swift" / platform_dir
        if not source.is_dir():
            logger.warning("The Swift package has no %s runtime", platform_dir)
            return
        sdk_swift = sdk_root / "usr" / "lib" / "swift"
        sdk_swift.mkdir(parents=True, exist_ok=True)
        entries = set(os.listdir(source))
        stubs = modules = 0
        for entry in sorted(entries):
            if entry.startswith("libswift") and entry.endswith(".dylib"):
                _stubify(source / entry, sdk_swift / (entry[: -len(".dylib")] + ".tbd"), platform_key)
                stubs += 1
            elif entry.endswith(".swiftmodule") and _runtime_module(entry[: -len(".swiftmodule")], entries):
                _replace(source / entry, sdk_swift / entry)
                modules += 1
        _replace(self.root / "usr" / "lib" / "swift" / "shims", sdk_swift / "shims")
        logger.info("Installed %d Swift runtime stubs and %d modules for %s", stubs, modules, platform_dir)
