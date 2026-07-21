## Context

Sift is a 850-line Python tool with CLI, GUI, and video-scan modes. Core architecture is sound: thread pool for parallel OCR, subprocess calls to tesseract, file moves to `SIFT_docs/`. Current state:

- **Threading**: `scan_videos` has a racy `skipped` counter mutated inside thread pool workers. `scan_images` is correct (counters incremented in main thread via `future.result()`).
- **OCR**: `count_meaningful_words` strips non-ASCII letters, making non-Latin languages unusable. Image threshold hardcoded to 2, video respects `--threshold`.
- **Distribution**: `_bundled.py` infra exists but only Windows build path is documented. Linux/macOS PyInstaller builds are untested. No install scripts.
- **File formats**: Only `.jpg`, `.jpeg`, `.png` scanned. Common formats (webp, bmp, tiff, heic) omitted.
- **GUI**: Tkinter calls (`messagebox`) from background thread — unsafe.

## Goals / Non-Goals

**Goals:**
- Fix all known bugs (thread race, non-Latin OCR, hardcoded threshold, GUI thread safety, format gaps, `_unique_dest` overflow)
- Add `--copy`, `--dry-run`, `--json`, `--search <term>` flags
- Make `--threshold` apply to images as well
- Run a systematic test pass on real data
- Produce working PyInstaller binaries for Linux/macOS
- Ship `install.sh` / `install.ps1` download scripts
- Rewrite README install section: single path, minimal friction

**Non-Goals:**
- Go rewrite (Phase 2, separate change)
- Adding a full test suite framework (manual real-data testing for now)
- Replacing OCR engine (still tesseract)
- Adding a web or mobile UI

## Decisions

| Decision | Choice | Rationale |
|---|---|---|
| **Counter mutation model** | Use `threading.Lock` for `skipped` in `scan_videos`; keep main-thread-only counters in `scan_images` as-is | Minimal change. Alternative: return (moved, skipped) from each worker and aggregate — cleaner but touches every function |
| **Non-Latin OCR** | Extend `count_meaningful_words` to keep Unicode letters (use `\p{L}` via `regex` or a Unicode-aware check) | Minimal change. Alternative: switch to language-agnostic word boundary detection (`\w+` in Unicode mode) |
| **`--copy` / `--dry-run`** | New `mode` parameter in `process()` callback: `"move"`, `"copy"`, `"preview"`. Progress tracks both moved and identified | Cleaner than boolean flags that interact |
| **Image formats** | Add `.webp`, `.bmp`, `.tiff`, `.tif`, `.heic`, `.gif` to `IMG_EXTENSIONS` | Zero-cost change, broadens compatibility |
| **`--json` output** | Accumulate results list in-memory, dump JSON at end. Schema: `{moved: [...], skipped: [...], stats: {total, moved, skipped, elapsed}}` | Simple, no streaming complexity. Files too large for memory can be handled later |
| **`--search <term>`** | Pass `search_term` through to `process()`, check `search_term in text.lower()` after OCR | Fast filter, works with existing OCR pipeline |
| **PyInstaller bundling** | Ship separate `build-linux.sh`, `build-macos.sh`, `build-windows.ps1`. Each downloads platform-specific tesseract+ffmpeg into `sift/bundle/<platform>/bin/` before building | Avoids bloating the repo with binaries. Download scripts are documented and auditable |
| **Install scripts** | `install.sh` detects OS/arch, fetches the right release tarball from GitHub, extracts to `~/.local/bin/` | Pattern used by `rustup`, `k3s`, etc. Familiar to users |

## Risks / Trade-offs

- **[Risk]** PyInstaller builds may fail on different glibc versions. → Mitigation: build on oldest supported glibc (Ubuntu 20.04) or use `--static` flags where possible.
- **[Risk]** Bundling tesseract+ffmpeg increases binary size to ~30-50MB. → Mitigation: this is a one-time download; users who prefer minimal can still use `pipx install`.
- **[Trade-off]** `--copy` mode with search term matching is slower (must OCR every file before deciding). This is inherent to the problem.
- **[Trade-off]** Dropping `python3-tk` from default install path for binary users (GUI not available in PyInstaller bundle unless we resolve tkinter bundling). → Mitigation: document that GUI users should use `pipx install` or the source path.
- **[Risk]** Non-Latin OCR fix may have false positives for short strings in non-Latin scripts. → Mitigation: threshold still applies; 3+ character minimum in meaningful word check.
