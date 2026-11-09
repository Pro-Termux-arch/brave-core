#!/usr/bin/env python3
# Copyright (c) 2026 The Brave Authors. All rights reserved.
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://mozilla.org/MPL/2.0/.

"""Statically inspect the custom APK. Never installs or executes browser code."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import sys
import zipfile

from build_partition_android import APPLICATION_ID


def capture(command):
    return subprocess.run(command, check=True, capture_output=True,
                          text=True).stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("apk", type=Path)
    parser.add_argument("--aapt", required=True, type=Path)
    parser.add_argument("--apksigner", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    apk = args.apk.resolve(strict=True)
    metadata = capture([str(args.aapt.resolve()), "dump", "badging", str(apk)])
    signing = capture([str(args.apksigner.resolve()), "verify", "--verbose",
                       "--print-certs", str(apk)])
    package = re.search(r"^package: name='([^']+)'", metadata, re.MULTILINE)
    if not package or package.group(1) != APPLICATION_ID:
        parser.error("APK does not have the custom application ID")

    libraries = []
    with zipfile.ZipFile(apk) as archive:
        names = set(archive.namelist())
        if not {"AndroidManifest.xml", "classes.dex"}.issubset(names):
            parser.error("APK is missing its manifest or primary dex")
        for info in archive.infolist():
            if not info.filename.startswith("lib/") or not info.filename.endswith(".so"):
                continue
            if not info.filename.startswith("lib/arm64-v8a/"):
                parser.error(f"unexpected non-ARM64 native library: {info.filename}")
            with archive.open(info) as library:
                header = library.read(64)
            if (len(header) < 64 or header[:6] != b"\x7fELF\x02\x01"
                    or struct.unpack_from("<H", header, 18)[0] != 183):
                parser.error(f"library is not little-endian AArch64 ELF64: {info.filename}")
            libraries.append({"path": info.filename, "uncompressed_size": info.file_size})
    if not libraries or not any("monochrome" in lib["path"] or "chrome" in lib["path"]
                                for lib in libraries):
        parser.error("expected native Chromium library is absent")

    def field(pattern):
        match = re.search(pattern, metadata, re.MULTILINE)
        return match.group(1) if match else None

    with apk.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    report = {
        "apk": str(apk), "size_bytes": apk.stat().st_size, "sha256": digest,
        "application_id": package.group(1),
        "version_name": field(r"^package: .*versionName='([^']+)'"),
        "minimum_sdk": field(r"^sdkVersion:'([^']+)'"),
        "target_sdk": field(r"^targetSdkVersion:'([^']+)'"),
        "native_libraries": libraries, "aapt_badging": metadata,
        "apksigner_verification": signing, "runtime_verified": False,
        "limitations": "APK structure and signing do not establish feature behavior or GPU activity.",
    }
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Static APK report: {args.output}; runtime remains unverified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
