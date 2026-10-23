#!/usr/bin/env python3
import json
import os
import re
import subprocess
import sys

import yaml

PLATFORMS = [
    "MacOSX",
    "iPhoneOS",
    "iPhoneSimulator",
    "AppleTVOS",
    "AppleTVSimulator",
    "WatchOS",
    "WatchSimulator",
    "XROS",
    "XRSimulator",
]
FILES = ["libSystem.B.tbd", "libobjc.A.tbd", "libc++.1.tbd", "libc++abi.tbd"]
EXPORT_KEYS = ["symbols", "objc-classes", "objc-eh-types", "objc-ivars", "weak-symbols", "thread-local-symbols"]
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "apple_sdk_gen", "supplements", "data", "darwin_libs.json")


def load_documents(path):
    with open(path) as f:
        text = re.sub(r"^--- !tapi-tbd", "---", f.read(), flags=re.M)
    return [doc for doc in yaml.safe_load_all(text) if doc]


def main():
    if len(sys.argv) > 2:
        sys.exit("usage: tools/extract-darwin-libs.py [developer dir]")
    developer_dir = sys.argv[1] if len(sys.argv) == 2 else subprocess.check_output(["xcode-select", "-p"], text=True).strip()
    libraries = {}
    for platform in PLATFORMS:
        lib_dir = os.path.join(developer_dir, "Platforms", platform + ".platform", "Developer", "SDKs", platform + ".sdk", "usr", "lib")
        for name in FILES:
            path = os.path.join(lib_dir, name)
            if not os.path.exists(path):
                print("missing " + path, file=sys.stderr)
                continue
            for doc in load_documents(path):
                if doc.get("tbd-version") != 4:
                    sys.exit(path + " is not a TBD v4 file")
                entry = libraries.setdefault(doc["install-name"], {
                    "current-version": str(doc.get("current-version", "")),
                    "compatibility-version": str(doc.get("compatibility-version", "")),
                    "flags": set(),
                    "reexported-libraries": set(),
                    **{key: set() for key in EXPORT_KEYS},
                })
                for group in doc.get("flags", []):
                    entry["flags"].update(group.get("flags", []) if isinstance(group, dict) else [group])
                for group in doc.get("reexported-libraries", []):
                    entry["reexported-libraries"].update(group.get("libraries", []))
                for section in ("exports", "reexports"):
                    for group in doc.get(section, []):
                        for key in EXPORT_KEYS:
                            entry[key].update(group.get(key, []))
    result = {}
    for install_name in sorted(libraries):
        entry = libraries[install_name]
        record = {}
        for key in ("current-version", "compatibility-version"):
            if entry[key]:
                record[key] = entry[key]
        for key in ("flags", "reexported-libraries", *EXPORT_KEYS):
            if entry[key]:
                record[key] = sorted(entry[key])
        result[install_name] = record
    with open(OUTPUT, "w") as f:
        json.dump(result, f, indent=1, sort_keys=True)
        f.write("\n")
    print("{} libraries, {} exports".format(len(result), sum(len(record.get(key, [])) for record in result.values() for key in EXPORT_KEYS)))


if __name__ == "__main__":
    main()
