## Context

Go rewrite is done. Binary works. But there's no release pipeline, no tags, and no way for anyone to download a prebuilt binary. The goreleaser config exists but hasn't been tested with CGo cross-compilation.

## Goals / Non-Goals

**Goals:**
- Tag and publish v1.1.0
- CI produces working binaries for linux/amd64, linux/arm64, darwin/amd64, darwin/arm64, windows/amd64
- README badges link to release downloads
- `install.sh` / `install.ps1` actually download working binaries
- Remove broken PyInstaller build scripts

**Non-Goals:**
- No code changes to sift itself
- No new features
- No pure-Go OCR migration
- No GUI

## Decisions

| Decision | Choice | Rationale |
|---|---|---|
| **CGo cross-compile** | Use goreleaser's Docker build container feature with `tesseract-ocr-dev` + `libleptonica-dev` | CGo cross-compilation is fragile. Docker containers make it reproducible. Default goreleaser builders don't have tesseract headers. |
| **Release tag format** | `v1.1.0` — semver | Matches existing convention. 1.1.0 because 1.0.0 was the Python version. |
| **Badge style** | shields.io dynamic badge: GitHub release | Standard practice. No custom hosting needed. |

## Risks / Trade-offs

- **[Risk]** CGo cross-compilation will fail on first try (it always does). → First release will need 2-3 CI iterations. Use `goreleaser --snapshot` to debug before tagging.
- **[Risk]** macOS arm64 build requires Apple's SDK. goreleaser can't cross-compile from Linux for macOS with CGo. → Need a macOS runner or build on macOS and upload manually for the darwin build.
- **[Mitigation]** For v1.1.0, ship Linux + Windows from CI. Build macOS manually and attach to release.
