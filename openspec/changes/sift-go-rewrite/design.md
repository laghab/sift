## Context

The Python prototype (Phase 1) proved the feature set works but left distribution friction unresolved. The Go rewrite eliminates all runtime dependencies by producing a single static binary with embedded OCR data.

Phase 1 delivered: image/video OCR, --copy, --dry-run, --search, --json, --threshold, --lang, Unicode support, thread pool parallelism. Phase 2 reimplements all of this in Go with zero external dependencies at runtime.

## Goals / Non-Goals

**Goals:**
- Single static binary per platform (Linux x86_64, macOS x86_64+arm64, Windows x64)
- All Phase 1 features preserved
- OCR without requiring tesseract installation (embedded tessdata + static linking or pure-Go OCR)
- Video frame extraction without ffmpeg (embedded ffmpeg or pure-Go video lib)
- Cross-compiled from a single CI pipeline (GitHub Actions)
- Graceful signal handling (SIGINT/SIGTERM)
- JSON output, dry-run, copy mode all work identically to Phase 1

**Non-Goals:**
- GUI in the initial Go release
- Windows GUI (.exe with GUI) — CLI only for now
- Replacing the Python codebase (kept for reference and legacy users)
- Performance optimization beyond matching Python's throughput
- Non-Latin OCR language packs beyond eng (users can add their own tessdata)

## Decisions

| Decision | Choice | Rationale |
|---|---|---|
| **OCR engine** | CGo static linking with `gosseract/v2` | Most reliable OCR. Pure-Go alternatives (e.g., `gosseract` alternatives) are immature or low accuracy. CGo pain is a one-time build cost. |
| **Tessdata embedding** | `go:embed` compiled tessdata (fastest, smallest, or custom) | `eng.traineddata` is ~2MB compressed. Embedding avoids needing to find it at runtime. |
| **Video frame extraction** | `ffmpeg` subprocess for now, bundled within binary via `go:embed` | Pure-Go video libs (`gen2brain/av`) require CGo for codec support too. Subprocess adds complexity but works reliably. Long-term: evaluate pure-Go approach. |
| **CLI framework** | `spf13/cobra` | Standard Go CLI library. Handles help text, flags, subcommands cleanly. |
| **Project structure** | `cmd/sift/main.go` + `internal/` packages | Standard Go layout. Avoids premature modularization. |
| **Parallel processing** | `sync.WaitGroup` + bounded goroutine pool | Go's concurrency primitives are cleaner than Python ThreadPoolExecutor. |
| **Progress output** | ANSI escape codes (same as Phase 1), suppressed in `--json` mode | Proven approach from Phase 1. |
| **Cross-compilation** | `goreleaser` + GitHub Actions | Industry standard for Go release automation. Produces platform-specific tarballs. |
| **Static linking** | CGo enabled, `-extldflags "-static"` for Linux; macOS uses system SDK | Required for tesseract C library static linking. macOS can't fully static link (Apple SDK restrictions). |

### Go project tree

```
sift/
├── cmd/
│   └── sift/
│       └── main.go              # Entry point, CLI setup
├── internal/
│   ├── ocr/
│   │   ├── tesseract.go         # CGo bridge to gosseract
│   │   └── count.go             # Unicode word counting
│   ├── scanner/
│   │   ├── image.go             # Image scan logic
│   │   └── video.go             # Video scan logic (ffmpeg subprocess)
│   ├── output/
│   │   ├── json.go              # JSON result builder
│   │   ├── summary.go           # Terminal summary
│   │   └── progress.go          # Progress bar rendering
│   ├── fileop/
│   │   └── ops.go               # move/copy/preview file operations
│   └── config/
│       └── config.go            # CLI flag parsing, mode detection
├── embed/
│   └── tessdata/
│       └── eng.traineddata      # Embedded via go:embed
├── go.mod
├── go.sum
├── .goreleaser.yaml             # Release automation
└── Makefile                     # Build shortcuts
```

### Data flow

```
CLI flags (cobra)
    │
    ▼
config.Parse()  →  mode, search_term, threshold, lang, workers
    │
    ▼
scanner.ScanImages() / scanner.ScanVideos()
    │
    ├──► walk directory, collect files
    ├──► spawn goroutine pool (bounded by workers)
    │       │
    │       ├──► ocr.Text() → gosseract
    │       ├──► count.Words() → Unicode-aware count
    │       ├──► check search_term
    │       ├──► check threshold
    │       └──► fileop.Do() → move/copy/preview
    │
    ├──► collect results (matched_paths, skipped_paths)
    └──► accumulate counters
    │
    ▼
output.JSON() or output.Summary()
```

## Risks / Trade-offs

- **[Risk]** CGo cross-compilation is fragile. Building tesseract + leptonica as static libs for 3 platforms × 2 architectures requires carefully maintained build scripts. → Mitigation: Use Docker build containers per platform. Document the exact toolchain versions.
- **[Risk]** `eng.traineddata` is ~2MB embedded, pushing binary size to ~15-30MB. → Acceptable: one-time download, comparable to or smaller than Phase 1's PyInstaller output.
- **[Trade-off]** Video mode requires ffmpeg binary bundled alongside sift or found on PATH. Pure-Go video decoding exists but adds complexity. → Phase 2 bundles ffmpeg; Phase 3 can evaluate pure-Go.
- **[Risk]** Non-English OCR requires additional `traineddata` files not embedded by default. → Users must download and place them manually (or use `--lang` with a pre-downloaded tessdata directory via env var `TESSDATA_PREFIX`).
- **[Trade-off]** No GUI in initial Go release. Power users who want the GUI stick with the Python version. → Documented clearly in README; GUI can be added later with Fyne or a web-based approach.
- **[Open Question]** Should video frame extraction use embedded ffmpeg binary or switch to a pure Go library like `gen2brain/av`? → Start with embedded ffmpeg for feature parity; benchmark accuracy/speed before switching.
