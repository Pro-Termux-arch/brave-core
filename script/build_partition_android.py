#!/usr/bin/env python3
# Copyright (c) 2026 The Brave Authors. All rights reserved.
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://mozilla.org/MPL/2.0/.

"""Build the custom ARM64 APK without installing, launching, or testing it."""

import argparse
import datetime
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys


APPLICATION_ID = "io.github.protermuxarch.partitionbrowser"
GIB = 1024 ** 3


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", type=int, default=2)
    parser.add_argument("--reserve-gib", type=int, default=25)
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    if args.jobs < 1 or args.reserve_gib < 10:
        parser.error("jobs must be positive; disk reserve must be at least 10 GiB")

    brave = Path(__file__).resolve().parents[1]
    src = brave.parent
    logs = src.parent / "logs"
    logs.mkdir(exist_ok=True)
    if not (src / ".gn").is_file():
        parser.error("Chromium checkout is missing; finish official ARM64 init first")
    if shutil.disk_usage(src).free < args.reserve_gib * GIB:
        parser.error("insufficient disk reserve; preserve checkout and add capacity")

    command = [
        "pnpm", "run", "build", "Static",
        "--target_os=android", "--target_arch=arm64",
        "--target_android_output_format=apk", "--use_remoteexec=false",
        "-C", "partition_android_arm64",
        "--ninja", f"j:{args.jobs}",
        "--gn", f"chrome_public_manifest_package:{APPLICATION_ID}",
        "--gn", "is_official_build:false",
        "--gn", "symbol_level:0",
        "--gn", "blink_symbol_level:0",
        "--gn", "v8_symbol_level:0",
        "--gn", "enable_android_secondary_abi:false",
    ]
    if args.prepare_only:
        command.append("--prepare_only")

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_path = logs / f"build-{stamp}.log"
    record = {"command": command, "cwd": str(brave),
              "application_id_requested": APPLICATION_ID,
              "runtime_verified": False}
    print(f"Build log: {log_path}", flush=True)
    with log_path.open("w") as log:
        log.write(json.dumps(record) + "\n")
        log.flush()
        process = subprocess.Popen(command, cwd=brave, stdout=log,
                                   stderr=subprocess.STDOUT,
                                   start_new_session=True)
        disk_stopped = False
        try:
            while True:
                try:
                    status = process.wait(timeout=10)
                    break
                except subprocess.TimeoutExpired:
                    if shutil.disk_usage(src).free < args.reserve_gib * GIB:
                        disk_stopped = True
                        log.write("Disk reserve reached; stopping build, retaining intermediates.\n")
                        log.flush()
                        os.killpg(process.pid, signal.SIGTERM)
                        try:
                            process.wait(timeout=30)
                        except subprocess.TimeoutExpired:
                            os.killpg(process.pid, signal.SIGKILL)
                            process.wait()
                        status = 75
                        break
        except KeyboardInterrupt:
            os.killpg(process.pid, signal.SIGTERM)
            process.wait()
            status = 130
    record.update(exit_code=status, disk_reserve_stop=disk_stopped,
                  build_log=str(log_path))
    (logs / f"build-{stamp}.json").write_text(json.dumps(record, indent=2) + "\n")
    print(f"Build exit code: {status}; no runtime verification performed.")
    return status if status >= 0 else 1


if __name__ == "__main__":
    sys.exit(main())
