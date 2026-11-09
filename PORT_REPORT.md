# Android desktop capabilities port — progress record

## Build outcome

IN PROGRESS: Brave Core clone is complete and ARM64 initialization is running. Chromium dependency sync, GN
generation, compilation, signing and APK packaging have not yet completed.
There is no APK or compiled-feature claim. This file must be updated as phases
complete; it is not a successful build report.

## Source pins

- Brave: 1.99.55, commit d5f73ccfbb8887db2367b182fa86df82c6b705cf.
- Chromium: 157.0.8103.39, commit 9a31f0acec1854d44e49a73fbf8017598151a583.
- Fork: https://github.com/Pro-Termux-arch/brave-core.
- Branch: feature/android-desktop-capabilities.
- Supported layout: project/src/brave, managed by Brave's pnpm initialization;
  brave-browser is releases/issues/documentation, not the Chromium checkout.

## Host and device

- Omarchy 4.5.0, Arch-derived, Linux x86_64; 4 logical CPUs.
- RAM: approximately 13 GiB; swap: approximately 27 GiB.
- Initial available disk: approximately 196 GiB on the 237 GiB root filesystem.
- Upstream Android instructions specify at least 100 GB free disk and 8 GB RAM;
  this is only a minimum, not a guarantee that Brave and build outputs will fit.
  Monitor free space throughout initialization and builds. Never delete unrelated
  files; pause downloads/build before filesystem exhaustion.
- Git 2.56.0, Python 3.14.8, system Java 17.0.21. System Node is 26.13.0;
  project-compatible Node 24.22.2 installed with mise without changing the default.
- Local Android SDK exists at /home/proadmin/Android/sdk, with platforms 36,
  36.1 and 37.0; NDKs 27.3.13750724 and 28.2.13676358. These are not substitutes
  for revision-pinned SDK/NDK/JDK/toolchain dependencies fetched by Chromium.
- ADB (read-only): Android 16, SDK 36, arm64-v8a, Exynos 2100, Mali EGL/Vulkan.
  ro.product.model reports SM-S947B; ro.product.vendor.model reports SM-G996B.
  Device features advertise GLES 3.2, Vulkan, freeform windows, and activities on
  secondary displays. Advertised capability is not proof of browser acceleration.

## Rendering and security constraints

Retain Chromium GPU process, Viz, Skia, Android surfaces, EGL/GLES and upstream
Vulkan selection/fallback. Retain Android MediaCodec hardware decoding where
supported. No custom driver, GPU library replacement, root dependency, forced
Vulkan, certificate bypass, sandbox bypass or unsafe command-line defaults.
Compiled backend reporting is pending a generated GN configuration; none can be
claimed compiled from source inspection alone. Driver activation and DeX
rendering remain runtime-unverified.

Brave Shields and other upstream protections must remain intact. Paid/API-backed
services may need builder-supplied credentials; never represent unset services as
verified protection. No dummy API keys or official signing identity are supplied.

## Containers, extensions, DeX

See docs/android-desktop/KIWI_INTEGRATION.md for concrete source comparisons and container security
requirements. Chromium's fixed-partition SiteInstance API is a candidate, not an
implemented container. Neither profile-keyed extension authorization nor UI tab
labels establish a container boundary. No new browser feature has been integrated
or compiled yet. No custom DeX UI has been implemented yet.

The custom build entry point requests application ID
`io.github.protermuxarch.partitionbrowser`. Stable/default Android launcher
resources now use `Partition Browser` / `Partition Browser - Development`.
These changes have not been compiled or packaged yet. Other channel resources
have not been rebranded; use only the supplied custom build entry point.

## Intended official build workflow

From src/brave with the project-compatible Node on PATH:

```sh
pnpm run init --target_os=android --target_arch=arm64
python3 script/build_partition_android.py --jobs 2
```

Initialization was started; build is pending. The build helper uses upstream
pnpm/GN/Ninja, Static configuration, no official-build identity, zero debug symbol
levels, no secondary ABI, two local jobs, and an explicit custom manifest package.
It monitors a 25 GiB free-space reserve and terminates only its own process group
if reached, preserving intermediates. It does not change GPU/security flags.
Use `--prepare-only` for GN preparation without compilation. Direct unmodified
pnpm build commands do not supply the custom application ID and are not the
delivery build configuration.

`script/inspect_partition_apk.py` checks a built APK using explicit aapt and
apksigner paths. It verifies the package ID, APK structure, native ELF AArch64
headers and signature, then records metadata, SHA256 and tool output. It has not
yet been run against an APK. Python syntax compilation and `git diff --check`
were performed; these are not browser compilation or runtime tests.

## Current feature matrix

| Requested feature group | Status |
| --- | --- |
| Complete native Brave ARM64 APK | Not implemented |
| Preserved Brave privacy/security in custom APK | Not implemented |
| GPU process, Viz, Skia, surfaces, EGL/GLES, Vulkan fallback, MediaCodec | Not implemented (no custom APK compiled) |
| Container cookies, sessions, LocalStorage, IndexedDB, cache, service workers, network state | Not implemented |
| Container create/rename/delete/color/icon/default/domain rules | Not implemented |
| Container tab open/reopen/selector/indicator/persistence/session restore | Not implemented |
| MV3 loading/registration/content scripts/background workers/storage/DNR | Not implemented |
| Extension permissions/popups/manager/enable/disable/uninstall/local install | Not implemented |
| Container-aware extension authorization | Not implemented |
| Phone-mode integration | Not implemented |
| DeX tab strip/toolbar/extension actions/indicators/desktop-site preference | Not implemented |
| Mouse hover/right click/keyboard shortcuts/resizing/multi-window/state restore | Not implemented |
| Performance/memory/lifecycle improvements | Not implemented |

## Logs and artifacts

- Logs: /home/proadmin/Projects/brave-desktop-android/logs/.
- Initial clone attempt timed out after 120 seconds; a new attempt was started
  without a timeout at the same path after the failed clone left no checkout.
  Preserve the currently active attempt; do not start another Chromium checkout.
- APK path, size, application ID, packaged version, min/target SDK, signing
  fingerprint, implementation commit: unavailable until built/committed.
- No application installation, launch, runtime testing, device configuration
  changes, firmware changes or root actions were performed.
