## 1. Bug Fixes

- [x] 1.1 Fix `count_meaningful_words` to support Unicode letters (non-Latin scripts). Replace `re.sub(r"[^a-zA-Z]", "", word)` with a Unicode-aware check (e.g., `unicodedata` category or `regex` Unicode letter match).
- [x] 1.2 Fix `skipped` double-count race in `scan_videos`. Remove the `skipped += 1` from inside the thread worker (`core.py:216`). Return `False` from the worker and let the main loop handle counting.
- [x] 1.3 Add `threshold` parameter to `scan_images` and pass it from CLI. Replace hardcoded `>= 2` with `>= threshold`.
- [x] 1.4 Fix GUI thread-safety: move `messagebox.showinfo` and `messagebox.askyesno` calls from `_scan_worker` background thread to main thread via `self.root.after()`.
- [x] 1.5 Add missing image formats to `IMG_EXTENSIONS`: `.webp`, `.bmp`, `.tiff`, `.tif`, `.heic`, `.gif`.
- [x] 1.6 Fix `_unique_dest` overflow: change `range(2, 1000)` to an unbounded `itertools.count(2)` or add a `break` after finding a gap.

## 2. New CLI Features

- [x] 2.1 Add `--copy` flag to CLI. Pass a `mode` parameter through to `scan_images`/`scan_videos`. When `mode="copy"`, use `shutil.copy2` instead of `shutil.move`.
- [x] 2.2 Add `--dry-run` flag. When active, OCR and report results without performing any file operations. Accumulate matched file paths for display/JSON.
- [x] 2.3 Add `--search <term>` flag. Pass `search_term` to worker functions. After OCR, check `search_term.lower() in ocr_text.lower()` before qualifying.
- [x] 2.4 Add `--json` flag. Accumulate `files_matched` and `files_skipped` arrays during scan. At completion, print JSON object to stdout instead of the normal summary. Suppress progress bar when `--json` is active.
- [x] 2.5 Make `--threshold` flag apply to image mode. Update `scan_images` signature to accept `threshold` parameter. Pass it from CLI and `gui.py`.

## 3. CLI Polish

- [x] 3.1 Show `--help` with examples when no arguments given (current behavior, keep).
- [x] 3.2 Add `--dry-run` and `--copy` to help text.
- [x] 3.3 Show mode (move/copy/preview) in the scan header and summary.

## 4. GUI Polish

- [x] 4.1 Add copy mode toggle checkbox to GUI options panel.
- [x] 4.2 Add search text entry to GUI options panel.
- [x] 4.3 GUI passes mode and search_term to scan functions.
- [x] 4.4 GUI shows mode in status text.

## 5. Distribution & Packaging

- [x] 5.1 Create `build/` scripts for each platform that download the correct tesseract + ffmpeg binaries, place them in `sift/bundle/<platform>/`, then run PyInstaller.
- [x] 5.2 Fix `_bundled.py` to work correctly on Linux/macOS frozen builds (currently hardcoded to `exe_dir/bin` pattern — verify tessdata and bin paths match PyInstaller extraction layout).
- [x] 5.3 Verify Linux PyInstaller build works end-to-end: run `build-linux.sh`, test the resulting binary on a real directory.
- [x] 5.4 macOS build: platform-specific (requires macOS). Documented in build/build-macos.sh.
- [x] 5.5 Create `install.sh` script: detects OS/arch, fetches release tarball from GitHub, extracts to `~/.local/bin/`.
- [x] 5.6 Create `install.ps1` script: same for Windows PowerShell.
- [x] 5.7 Add release workflow docs: build commands per platform, how to create a GitHub release with assets.

## 6. Real-Data Testing

- [x] 6.1 Test on a directory with mixed images (screenshots with text, photos without text, various formats). Verify correct files move to `SIFT_docs/`.
- [x] 6.2 Test `--copy` mode: verify originals remain in place after run.
- [x] 6.3 Test `--dry-run` mode: verify no files are moved.
- [x] 6.4 Test `--search` with known terms: verify only matching files are selected.
- [x] 6.5 Test `--json` mode: verify output is valid JSON with correct counts.
- [x] 6.6 Test `--threshold` on images: verify files below threshold are skipped.
- [ ] 6.7 Test `--video` mode on a directory with mixed videos.
- [x] 6.8 Test non-Latin language: create a test image with Arabic/Russian/Chinese text, run with `--lang ara/rus/chi_sim`, verify OCR and counting works.
- [x] 6.9 Test edge cases: empty directory, no-matches directory, corrupt image files, path with spaces.
- [ ] 6.10 Test KeyboardInterrupt handling: start scan, press Ctrl+C, verify clean exit.

## 7. Documentation & README

- [x] 7.1 Rewrite README install section: one primary path (pipx), mention binary downloads, mark GUI as separate path with tkinter note.
- [ ] 7.2 Add binary download badges/links in README.
- [x] 7.3 Document new CLI flags (`--copy`, `--dry-run`, `--search`, `--json`, `--threshold` for images).
- [x] 7.4 Update `build.sh` to reflect the new per-platform build scripts.
- [x] 7.5 Clean up `.gitignore` to include new build artifacts if any.
