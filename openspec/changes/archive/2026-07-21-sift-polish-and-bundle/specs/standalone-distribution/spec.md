## ADDED Requirements

### Requirement: PyInstaller binary for Linux
The system SHALL produce a working standalone executable for Linux x86_64 via PyInstaller. The binary SHALL include the sift CLI. It SHALL NOT require Python, pip, or any system packages to run.

#### Scenario: Linux binary runs without Python
- **WHEN** a user downloads the Linux binary and runs `./sift --version`
- **THEN** the version is displayed
- **THEN** no Python-related errors occur

#### Scenario: Linux binary scans images
- **WHEN** a user runs the Linux binary on a directory with images
- **THEN** tesseract is found (either bundled or on PATH)
- **THEN** images with text are moved to SIFT_docs/

### Requirement: PyInstaller binary for macOS
The system SHALL produce a working standalone executable for macOS (both x86_64 and arm64) via PyInstaller. Same constraints as Linux binary.

#### Scenario: macOS binary runs without Python
- **WHEN** a user downloads the macOS binary and runs `./sift --version`
- **THEN** the version is displayed

### Requirement: Windows .exe installer
The system SHALL produce a working standalone executable for Windows x64 via PyInstaller. The binary SHALL bundle tesseract.exe, its DLLs, and eng.traineddata. FFmpeg SHALL be bundled for video support.

#### Scenario: Windows exe runs without Python
- **WHEN** a user downloads sift.exe and runs it
- **THEN** the CLI works without Python installed

### Requirement: Install script for Linux/macOS
The system SHALL provide an `install.sh` script that detects the OS and architecture, downloads the appropriate release binary from GitHub, and installs it to `~/.local/bin/`.

#### Scenario: Install script fetches and places binary
- **WHEN** a user runs `curl -fsSL https://github.com/laghab/sift/releases/.../install.sh | bash`
- **THEN** the correct binary for the platform is downloaded
- **THEN** it is placed in `~/.local/bin/sift`
- **THEN** `sift --version` works

### Requirement: pipx install path
The system SHALL support `pipx install .` from the source repo as an alternative install path. This SHALL install the CLI and GUI entry points.

#### Scenario: pipx install works
- **WHEN** a user runs `pipx install .` in the repo root
- **THEN** `sift` and `sift-gui` commands are available globally

### Requirement: Release workflow
The system SHALL document the release process for producing and publishing binaries. This SHALL include build commands, platform matrix, and upload instructions.

#### Scenario: Release documentation exists
- **WHEN** a maintainer follows the release docs
- **THEN** binaries for all three platforms are produced
- **THEN** assets are attached to a GitHub release
