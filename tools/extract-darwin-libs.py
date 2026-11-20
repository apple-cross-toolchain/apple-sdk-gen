#!/usr/bin/env python3
import argparse
import json
import os
import re
import subprocess
import sys

import yaml

from apple_sdk_gen.config import PLATFORM_CONFIGS
from apple_sdk_gen.supplements.darwin_libs import LIBRARIES

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "apple_sdk_gen", "supplements", "data", "darwin_libs.json")
TBD_FIELDS = (
    "install-name", "targets", "current-version", "compatibility-version",
    "flags", "reexported-libraries", "exports", "reexports",
)


def load_documents(path):
    with open(path) as f:
        text = re.sub(r"^--- !tapi-tbd", "---", f.read(), flags=re.M)
    return [doc for doc in yaml.safe_load_all(text) if doc]


def extract_libraries(developer_dir):
    result = {}
    for platform_key, platform in PLATFORM_CONFIGS.items():
        lib_dir = os.path.join(developer_dir, "Platforms", platform.platform_dir, "Developer",
                               "SDKs", f"{platform.sdk_prefix}.sdk", "usr", "lib")
        libraries = {}
        for name in LIBRARIES:
            path = os.path.join(lib_dir, f"{name}.tbd")
            if not os.path.exists(path):
                print("missing " + path, file=sys.stderr)
                continue
            documents = []
            for doc in load_documents(path):
                if doc.get("tbd-version") != 4:
                    sys.exit(path + " is not a TBD v4 file")
                record = {field: doc[field] for field in TBD_FIELDS if field in doc}
                for field in ("current-version", "compatibility-version"):
                    if field in record:
                        record[field] = str(record[field])
                documents.append(record)
            libraries[name] = documents
        if libraries:
            result[platform_key] = libraries
    return result


def main():
    parser = argparse.ArgumentParser(description="Extract target-specific Darwin library metadata from Xcode.")
    parser.add_argument("developer_dir", nargs="?", help="Xcode's Contents/Developer directory")
    parser.add_argument("--output", default=OUTPUT, help="write the metadata to this JSON path")
    args = parser.parse_args()
    developer_dir = args.developer_dir or subprocess.check_output(["xcode-select", "-p"], text=True).strip()
    result = extract_libraries(developer_dir)
    with open(args.output, "w") as f:
        json.dump(result, f, indent=1, sort_keys=True)
        f.write("\n")
    print(f"Darwin library metadata for {len(result)} SDKs written to {args.output}")


if __name__ == "__main__":
    main()
