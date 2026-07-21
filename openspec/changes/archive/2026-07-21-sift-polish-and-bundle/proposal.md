## Why

Sift works in principle, but installation is a 7-step slog (Python + venv + pip + tesseract + ffmpeg + tkinter), it has never been systematically tested, and several real bugs exist in the core logic (thread safety, non-Latin OCR, hardcoded thresholds). Without a polished, distributable package and a solid test pass, the tool isn't trustworthy enough to give to others.

This phase focuses on: (1) fixing known bugs, (2) testing on real data, (3) adding missing features users need, and (4) producing installable artifacts (PyInstaller standalone binary, pipx package) that eliminate the dependency friction for end users. Phase 2 will be a Go rewrite for true zero-dependency distribution.

## What Changes

- **Bug fixes**: Fix thread-safety race condition in `core.py` scan_videos (`skipped` double-counting), fix `count_meaningful_words` to support non-Latin scripts, fix hardcoded image threshold (respect `--threshold`), fix GUI calling tkinter dialogs from background thread, add missing image formats (webp, bmp, tiff, heic), fix `_unique_dest` overflow at 999+ collisions.
- **New CLI flags**: `--copy` (copy instead of move), `--dry-run` (report-only), `--json` (structured output to stdout), `--search <term>` (only move files containing specific text).
- **Feature**: Add image threshold support (`--threshold` works for images too, not just video).
- **Testing**: Systematic test pass on real data (phone backups, screenshot collections, video files).
- **Distribution**: Fix PyInstaller build to produce working standalone binaries for Linux/macOS. Verify Windows cross-build path works. Ship `install.sh`/`install.ps1` scripts that download prebuilt binary.
- **Readme**: Rewrite install section to be a single-path guide. Add download links for prebuilt binaries.
- **Docs**: No changes to existing specs (there are none yet). README.md update.

## Capabilities

### New Capabilities

- `copy-mode`: Support for non-destructive operation (copy instead of move, dry-run preview).
- `search-filter`: Search for specific text terms, not just presence of any text.
- `json-output`: Structured machine-readable output for scripting and piping.
- `standalone-distribution`: PyInstaller bundles with baked tesseract+ffmpeg for one-file download.

### Modified Capabilities

<!-- No existing specs to modify -->

## Impact

- **Core logic** (`core.py`): threading changes, OCR pipeline changes, new flags flow through
- **CLI** (`cli.py`): new arguments, new output modes
- **GUI** (`gui.py`): thread-safety fix
- **Packaging** (`build.sh`, `pyproject.toml`): PyInstaller fixes, install scripts
- **Dependencies**: No new pip deps. Tesseract/ffmpeg still required for source installs; bundled in binary releases.
- **Backwards compatibility**: `--copy` and `--dry-run` are additive. `--threshold` for images changes default behavior slightly (was hardcoded 2, now defaults to 2 but configurable). Non-Latin OCR fix changes behavior for non-English users (previously broken, now works).
