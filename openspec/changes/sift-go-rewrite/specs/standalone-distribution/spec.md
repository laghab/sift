## MODIFIED Requirements

### Requirement: Go static binary for Linux
**BREAKING** — replaces "PyInstaller binary for Linux"

The system SHALL produce a statically linked Go executable for Linux x86_64 and arm64. The binary SHALL embed `eng.traineddata` and SHALL NOT require any system packages (including tesseract) to run.

#### Scenario: Linux binary runs on any distro
- **WHEN** a user downloads the Linux binary and runs `./sift --version`
- **THEN** the version is displayed
- **THEN** no missing library or Python errors occur

#### Scenario: Linux binary scans with embedded OCR
- **WHEN** a user runs the Linux binary on a directory with images
- **THEN** OCR works without tesseract installed on the system

### Requirement: Go static binary for macOS
**BREAKING** — replaces "PyInstaller binary for macOS"

The system SHALL produce a Go executable for macOS (x86_64 and arm64) compiled against the macOS SDK. Fully static linking is not possible on macOS (Apple SDK restrictions), but SHALL NOT require Python, tesseract, or any Homebrew packages.

#### Scenario: macOS binary runs without Homebrew
- **WHEN** a user downloads the macOS binary and runs `./sift --version`
- **THEN** the version is displayed
- **THEN** no Homebrew or Python dependency errors occur

### Requirement: Windows Go static binary
**BREAKING** — replaces "Windows .exe installer"

The system SHALL produce a Go executable for Windows x64. The binary SHALL embed `eng.traineddata` and SHALL NOT require Tesseract installation. FFmpeg SHALL NOT be bundled; video mode requires ffmpeg on PATH.

#### Scenario: Windows exe runs without Tesseract
- **WHEN** a user downloads sift.exe and runs it
- **THEN** the CLI works without Tesseract installed

## REMOVED Requirements

### Requirement: pipx install path
**Reason**: Go binary replaces Python distribution. There is no Python package to pipx-install.
**Migration**: Use the Go static binary from GitHub releases, or use `go install github.com/laghab/sift/cmd/sift@latest` if you have the Go toolchain installed.

## ADDED Requirements

### Requirement: go install path
The system SHALL support installation via `go install github.com/laghab/sift/cmd/sift@latest` for users who have the Go toolchain installed.

#### Scenario: go install works
- **WHEN** a user runs `go install github.com/laghab/sift/cmd/sift@latest`
- **THEN** the `sift` binary is installed to `$GOPATH/bin/sift`
- **THEN** `sift --version` works

### Requirement: Automated release via goreleaser
The system SHALL use `goreleaser` configured in `.goreleaser.yaml` to build and publish releases for all platforms. The release pipeline SHALL be triggered by pushing a git tag.

#### Scenario: Release tag triggers build
- **WHEN** a maintainer pushes a tag `v1.2.0`
- **THEN** GitHub Actions builds binaries for linux/amd64, linux/arm64, darwin/amd64, darwin/arm64, windows/amd64
- **THEN** release artifacts are attached to the GitHub release
