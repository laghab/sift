## 1. Go Project Setup

- [x] 1.1 Initialize Go module (`go mod init github.com/laghab/sift`), create `cmd/sift/main.go` directory structure
- [x] 1.2 Add dependencies: `cobra` for CLI, `gosseract/v2` for OCR
- [x] 1.3 Set up CGo build environment: verify tesseract + leptonica dev headers/libs available for static linking
- [x] 1.4 Create `Makefile` with targets: `build`, `build-static`, `clean`, `test`, `lint`
- [x] 1.5 Create `internal/config/config.go`: parse CLI flags via cobra, derive mode/search_term/threshold/workers/lang

## 2. Core: OCR Engine

- [x] 2.1 Create `internal/ocr/tesseract.go`: CGo bridge to gosseract/v2, configure language, PSM mode, timeout
- [x] 2.2 Create `internal/ocr/count.go`: Unicode-aware word counting (port of Phase 1's unicodedata approach — use `unicode.IsLetter` in Go)
- [x] 2.3 Embed `eng.traineddata` via `//go:embed` in `embed/tessdata/`
- [x] 2.4 Support fallback: if `TESSDATA_PREFIX` env var is set, use external tessdata dir; otherwise use embedded
- [x] 2.5 Test OCR on sample images (same test images from Phase 1)

## 3. Core: File Operations

- [x] 3.1 Create `internal/fileop/ops.go`: `Do(src, dest, mode)` function supporting "move", "copy", "preview"
- [x] 3.2 Implement `_unique_dest` equivalent: append incrementing suffix on name collision
- [x] 3.3 Implement `SIFT_docs/` directory logic with subdirectory preservation
- [x] 3.4 Support `--dry-run` (mode="preview") that performs no file I/O

## 4. Core: Image Scanner

- [x] 4.1 Create `internal/scanner/image.go`: walk directory, collect files by extension (same supported formats as Phase 1)
- [x] 4.2 Implement goroutine pool with bounded worker count (channel-based semaphore)
- [x] 4.3 Per-worker: OCR → count words → check search term → check threshold → file op
- [x] 4.4 Collect results: matched_paths, skipped_paths, counters
- [x] 4.5 Support `stop` channel for cancellation

## 5. Core: Video Scanner

- [x] 5.1 Create `internal/scanner/video.go`: list video files, detect duration via ffprobe or pure-Go probe
- [x] 5.2 Implement ffmpeg subprocess for frame extraction (same interval logic as Phase 1: 1s/2s/5s based on duration)
- [x] 5.3 Ensure ffmpeg is found: check binary directory first, then PATH
- [x] 5.4 OCR sampled frames, aggregate word count, check threshold + search term
- [x] 5.5 Clean up temp frame directories after processing

## 6. Output: Terminal and JSON

- [x] 6.1 Create `internal/output/progress.go`: ANSI progress bar (same style as Phase 1)
- [x] 6.2 Create `internal/output/summary.go`: final summary table with colors
- [x] 6.3 Create `internal/output/json.go`: build JSON object with all required fields
- [x] 6.4 Suppress progress and summary when `--json` is active
- [x] 6.5 Write JSON to stdout, errors to stderr

## 7. CLI Wiring

- [x] 7.1 Wire all components in `cmd/sift/main.go`: parse flags → run scanner → print output
- [x] 7.2 Implement graceful signal handling (SIGINT/SIGTERM → cancel via stop channel → exit 130)
- [x] 7.3 Handle `--version` flag
- [x] 7.4 Handle empty/no-args case: print help with examples
- [x] 7.5 Handle invalid directory, missing deps (ffmpeg for video mode), OCR errors gracefully

## 8. Distribution & Release

- [x] 8.1 Create `.goreleaser.yaml` with builds for linux/amd64, linux/arm64, darwin/amd64, darwin/arm64, windows/amd64
- [x] 8.2 Configure CGo cross-compilation in goreleaser (Docker build containers with tesseract static libs)
- [x] 8.3 Create GitHub Actions workflow `.github/workflows/release.yml`
- [ ] 8.4 Test end-to-end release dry-run: `goreleaser release --snapshot --clean`
- [ ] 8.5 Verify Linux binary on a clean machine (no Go, no Python, no tesseract)
- [x] 8.6 Remove PyInstaller build scripts (no longer needed for primary distribution)
- [x] 8.7 Update `install.sh` and `install.ps1` to download Go binary from releases

## 9. Testing & Verification

- [x] 9.1 Test on same Phase 1 test images: verify identical results for --dry-run, --json, --copy, --search, --threshold
- [ ] 9.2 Test video mode with ffmpeg present and absent (graceful error)
- [x] 9.3 Test Unicode non-Latin OCR with Arabic test image
- [x] 9.4 Test edge cases: empty dir, no-match, path with spaces
- [ ] 9.5 Test signal handling: Ctrl+C during scan, verify clean exit
- [ ] 9.6 Test on a real phone backup directory (mixed images with/without text)

## 10. Documentation & Cleanup

- [x] 10.1 Update README: one-line install (`go install` or binary download), remove Python install instructions
- [ ] 10.2 Add binary download badges to README
- [x] 10.3 Remove or archive PyInstaller build scripts (build/*.sh, build/*.ps1)
- [x] 10.4 Mark Python version as legacy in README, point to Go binary for new users
- [x] 10.5 Update `RELEASE.md` to reflect goreleaser-based release process

## 10. Documentation & Cleanup

- [ ] 10.1 Update README: one-line install (`go install` or binary download), remove Python install instructions
- [ ] 10.2 Add binary download badges to README
- [ ] 10.3 Remove or archive PyInstaller build scripts (build/*.sh, build/*.ps1)
- [ ] 10.4 Mark Python version as legacy in README, point to Go binary for new users
- [ ] 10.5 Update `RELEASE.md` to reflect goreleaser-based release process
