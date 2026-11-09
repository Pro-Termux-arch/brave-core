# Kiwi integration decision — source inspection, not runtime verification

## Revision anchors

- Primary: Brave Core v1.99.55; Chromium 157.0.8103.39
  (`9a31f0acec1854d44e49a73fbf8017598151a583`).
- kiwibrowser/chromium_extension_patches:
  `70090be3d44b848983af2d92bf8b5e635d67e24b`, GPL-3.0.
- kiwibrowser/src.next:
  `7be7edd1532148f22103cb4c5a1964d96297836f`; CHROMIUM_VERSION
  specifies 105.0.5195.24; repository root licence is BSD-3-Clause.
  Individual files and third-party notices still require review before reuse.

## Actual source comparison

The R80 patch bundle modifies the old Android tab models, app-menu JNI,
extension hosts, GN dependencies, and many platform guards. Its README reports
debug builds and extension sideloading as unsupported. It is not a patch set
for Chromium 157 and must not be applied wholesale.

Kiwi src.next chrome/browser/extensions/extension_install_prompt.cc implements
an Android confirmation using AppModalDialogManager. However,
AutoConfirmPromptIfEnabled() at lines 738–749 contains an unconditional
`if (true)` that posts an ACCEPTED result. This fallback must not be reused.
This is a source observation, not a claim that every Kiwi install skips a prompt.

Chromium 157 extensions/buildflags/buildflags.gni separates ENABLE_EXTENSIONS,
ENABLE_EXTENSIONS_CORE and ENABLE_DESKTOP_ANDROID_EXTENSIONS. The desktop Android
flag defaults to is_desktop_android; normal mobile Android does not enable it.
Setting flags alone is not an integration.

Chromium 157 chrome/browser/ui/android/extensions/BUILD.gn already contains:

- extension_action_popup_contents.{cc,h}, backed by Chromium WebContents;
- extension_actions_bridge and extension_action_delegate_android;
- extension_install_dialog_view_android and its Java dialog bridge;
- extension_developer_private_bridge and extension_util_bridge;
- extensions_toolbar_android and extensions_menu_delegate_android;
- JNI bindings and conditional Java sources under enable_extensions_core.

Decision: use Chromium 157's current engine, JNI and Android UI as the foundation.
Use Kiwi's app-menu/action arrangement as a design reference only unless a
specific missing component justifies a small, independently reviewed adaptation.
No Kiwi code has been incorporated as of this inspection. Do not claim Kiwi
extension integration or MV3 support from this document.

## Container boundary requirements

Chromium 157 SiteInstance::CreateForFixedStoragePartition accepts a non-default
StoragePartitionConfig preserved across navigations. The partition config,
not SiteInstance identity by itself, supplies the storage boundary. A separate
SiteInstance with the default partition does not isolate cookies or storage.

Before exposing containers, native tab creation, restoration, renderer-created
windows, redirects, back/forward navigation and WebContents replacement must
retain the partition identity. UI metadata alone is insufficient. Data deletion
must close/quiesce affected tabs and workers before storage removal; unknown or
deleted identities must fail closed, never silently use the default partition.

Partitions do not automatically isolate Profile-keyed permission grants, history,
passwords, downloads, extension services, clipboard, or network anonymity.
An extension system shared by a Profile is not container-aware. Do not enable
extension access to container tabs until API tab/frame lookup, content-script
matching, activeTab grants, cookie access, service-worker events and request
observation have explicit, reviewed container authorization boundaries.

## Evidence

Read-only source snapshots are in logs/kiwi-reference and logs/upstream. They are
inspection material, not source overlays. No browser, instrumentation, UI tests,
or benchmarks were run; no APK was installed on the attached phone.
