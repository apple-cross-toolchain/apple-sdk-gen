#!/usr/bin/env python3
"""Extract versioned Darwin linker metadata for local comparisons."""

import argparse
import json
import re
from pathlib import Path

import yaml

from apple_sdk_gen.config import PLATFORM_CONFIGS
from apple_sdk_gen.supplements.darwin_libs import LIBRARIES

TBD_FIELDS = (
    "install-name", "targets", "current-version", "compatibility-version",
    "flags", "reexported-libraries", "exports", "reexports", "swift-abi-version",
)


def load_documents(path: Path) -> list[dict]:
    text = re.sub(r"^--- !tapi-tbd", "---", path.read_text(), flags=re.M)
    records = []
    for document in yaml.safe_load_all(text):
        if document.get("tbd-version") != 4:
            raise ValueError(f"{path} is not a TBD v4 file")
        record = {field: document[field] for field in TBD_FIELDS if field in document}
        for field in ("current-version", "compatibility-version"):
            if field in record:
                record[field] = str(record[field])
        records.append(record)
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sdk", type=Path, help="path to an installed or generated SDK")
    parser.add_argument("--platform", required=True, choices=PLATFORM_CONFIGS)
    parser.add_argument("--output", type=Path, required=True, help="JSON output path")
    args = parser.parse_args()
    try:
        settings = json.loads((args.sdk / "SDKSettings.json").read_text())
        version = settings["Version"]
        platform = PLATFORM_CONFIGS[args.platform]
        if settings["CanonicalName"] != f"{platform.sdk_prefix.lower()}{version}":
            raise ValueError(f"{args.sdk} does not describe a {args.platform} SDK")
        libraries = {
            name: load_documents(args.sdk / "usr" / "lib" / f"{name}.tbd")
            for name in LIBRARIES
        }
        metadata = {"sdk_version": version, "platforms": {args.platform: libraries}}
        args.output.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    except (KeyError, OSError, ValueError, yaml.YAMLError) as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
