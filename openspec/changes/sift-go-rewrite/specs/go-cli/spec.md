## ADDED Requirements

### Requirement: Go implementation preserves all Phase 1 features
The Go CLI SHALL implement all scanning, filtering, and output features delivered in Phase 1: `--copy`, `--dry-run`, `--search <term>`, `--json`, `--video`, `--threshold <n>`, `--lang <code>`, `--workers <n>`, and Unicode-aware word counting. Behavior SHALL match the Python implementation.

#### Scenario: Copy mode in Go matches Python behavior
- **WHEN** user runs `./sift --copy ~/photos`
- **THEN** files with text are copied to `~/photos/SIFT_docs/`
- **THEN** originals remain in place
- **THEN** output matches the Phase 1 format

#### Scenario: Search filter in Go matches Python behavior
- **WHEN** user runs `./sift --dry-run --search "invoice" ~/photos`
- **THEN** only files containing "invoice" in OCR text are reported
- **THEN** output matches Phase 1 format

#### Scenario: JSON output in Go matches Python schema
- **WHEN** user runs `./sift --json ~/photos`
- **THEN** the JSON object contains all fields from the Phase 1 schema
- **THEN** no terminal progress output is shown

### Requirement: Video mode with embedded ffmpeg
The Go binary SHALL support `--video` mode by shelling out to ffmpeg. The ffmpeg binary SHALL be bundled alongside (same directory as) the sift executable, or found on PATH.

#### Scenario: Video scan with bundled ffmpeg
- **WHEN** user runs `./sift --video ~/videos` and ffmpeg is next to the binary or on PATH
- **THEN** frames are extracted with ffmpeg
- **THEN** videos with text are moved to `SIFT_docs/`

### Requirement: Static binary with embedded tessdata
The Go binary SHALL statically link libtesseract and libleptonica via CGo. The `eng.traineddata` SHALL be embedded into the binary using `go:embed`. The binary SHALL NOT require `TESSDATA_PREFIX` to be set for English OCR.

#### Scenario: English OCR works without TESSDATA_PREFIX
- **WHEN** user runs `./sift ~/photos` without `TESSDATA_PREFIX` set
- **THEN** English OCR works using the embedded traineddata

#### Scenario: Custom tessdata directory overrides embedded
- **WHEN** user runs `TESSDATA_PREFIX=/path/to/tessdata ./sift --lang fra ~/photos`
- **THEN** the external `tessdata` directory is used instead of the embedded one

### Requirement: Graceful signal handling
The Go binary SHALL handle SIGINT and SIGTERM by finishing the current file, then printing a cancellation message and exiting with code 130.

#### Scenario: Ctrl+C cancels mid-scan
- **WHEN** user presses Ctrl+C during a scan
- **THEN** the current file being processed completes
- **THEN** no new files are started
- **THEN** a cancellation message is printed to stderr
- **THEN** the process exits with code 130
