## Why

Sift has a working Go binary but no releases, no download badges, and no CI pipeline that actually runs. Anyone finding the repo has to `go build` from source or fight with the legacy Python install. This change ships v1.1.0 — tag it, build it, upload it, badge it. That's it.

## What Changes

- Tag v1.1.0 and push
- Fix `.goreleaser.yaml` so cross-compilation actually works (Linux/macOS/Windows, amd64/arm64)
- Create `.github/workflows/release.yml` that triggers on tags
- Remove broken PyInstaller build scripts
- Update `install.sh` and `install.ps1` to download goreleaser tarballs
- Add download badges to README
- Verify the tarball works on a clean machine
- `go install` path works (already does, just needs documenting)

No new features. No spec changes. Pure ship.

## Capabilities

<!-- No new capabilities or modified capabilities. This is purely operational. -->

## Impact

- `.goreleaser.yaml` — fix CGo cross-compilation flags
- `.github/workflows/release.yml` — new file
- `install.sh`, `install.ps1` — update download URLs
- `README.md` — add badges
- `build/*` — remove PyInstaller scripts
- No code changes to `cmd/` or `internal/`
