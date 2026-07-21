## Why

Phase 1 proved the concept and added all the features users need, but installation is still painful: Python + pip + venv + tesseract + ffmpeg + tkinter. Even the PyInstaller binary needs tesseract on PATH to function. The goal is a single static binary you download and run — nothing else. Rewriting in Go makes this trivial: cross-compile once, ship everywhere.

## What Changes

- **Complete rewrite** of all Sift functionality from Python to Go. The Python code stays in `sift/` as reference but is no longer the primary distribution.
- **Static binary**: One executable per platform, statically linked, no libc dependencies (musl-based build for Linux).
- **Embedded OCR**: Use `gosseract` (CGo bindings to libtesseract) statically linked, with `eng.traineddata` baked into the binary via `go:embed`.
- **Embedded FFmpeg**: For video mode, either embed ffmpeg binaries or use a pure-Go video frame extraction library (`gen2brain/av`).
- **All Phase 1 features preserved**: `--copy`, `--dry-run`, `--search`, `--json`, `--video`, `--threshold`, `--lang`, `--workers`, Unicode OCR.
- **No GUI in initial Go release**. GUI can be revisited later (Fyne, webview, or a separate project). For now, CLI-only.
- **Carry forward incomplete Phase 1 tasks**: video testing, signal handling, release badges.

## Capabilities

### New Capabilities
- `go-cli`: Go-based implementation of the sift CLI with all features from Phase 1, compiled to a static binary.

### Modified Capabilities
- `standalone-distribution`: Distribution model changes from PyInstaller to Go static binary. Requirements now specify `go:embed` for traineddata, cross-compilation for all platforms, and GitHub Actions CI for automated releases.

## Impact

- **New codebase**: `cmd/sift/main.go` + `internal/` package tree in Go
- **Python code**: `sift/` directory remains but is deprecated for end users (still reference for Phase 3 if needed)
- **Build system**: `go build` replaces PyInstaller. GitHub Actions for cross-platform releases.
- **Distribution**: Releases become truly single-file. No more PyInstaller complexity.
- **Dependencies**: Zero runtime dependencies. Go toolchain + CGo tesseract headers for build time.
- **GUI**: Removed from initial Go release. `sift --gui` will error with a message pointing to the Python version for now.
