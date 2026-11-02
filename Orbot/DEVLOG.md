# Orbot Development Log

## 2026-10-28 — Microsoft Store preparation plan

This is a plan for preparing **Orbot** for Microsoft Store distribution. It does
not claim that Orbot currently complies with Store requirements or has been
submitted. Orbot's Tauri configuration currently has `bundle.active: false`.

The scope is Orbot's own repository. Dock Station remains Orbot's required
launch and activation environment. VIV and Prime Mail keep their separate
repositories, services, and data authority; this plan does not package or
change them.

### Preparation work

1. Choose and document the Store distribution format after checking that it
   preserves Dock-owned startup, initial docking, and the existing runtime
   boundaries. Tauri's current Windows Store guide describes a Store listing
   that links to an offline MSI or EXE installer; it does not produce an MSIX
   package directly.
2. Define how the Orbot release obtains its required runtime components,
   professional foundation, and existing AIMS credential without relying on a
   developer checkout, repository-relative `.venv`, or writable package folder.
   Keep the existing shared llama.cpp service and user-owned AIMS records as
   external authorities unless a separate owner-approved deployment decision
   says otherwise.
3. Confirm microphone permission behavior and write the Store privacy and
   capability disclosures for local microphone capture, model inference, and
   persistent memory. Do not add a browser speech engine or Windows speech
   fallback.
4. Set final package metadata, publisher identity, versioning, offline WebView2
   installer behavior, and a Store-compatible installation/update/uninstall
   path that preserves user data.
5. Build a release package and validate it with the current Windows App
   Certification Kit, followed by clean-machine lifecycle, microphone, update,
   and uninstall checks. Provide accurate certification notes and Store listing
   materials for owner review.

The required relationship between the Store-distributed Orbot and the
Dock-owned launch environment remains an implementation dependency to resolve
before submission. No packaging configuration, Store account, product listing,
or certification result is created by this planning entry.
