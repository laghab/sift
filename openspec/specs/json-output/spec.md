## Purpose

Provide machine-readable JSON output for scripting, piping, and integration with other tools. Suppress terminal-specific output when JSON mode is active.

## Requirements

### Requirement: JSON output mode
The system SHALL support a `--json` flag that outputs scan results as a JSON object to stdout. Normal console output (progress bar, summary) SHALL be suppressed when `--json` is active.

#### Scenario: JSON output with results
- **WHEN** user runs `sift --json ~/photos`
- **THEN** stdout contains a single JSON object
- **THEN** terminal progress bar and colored summary are not shown

### Requirement: JSON output schema
The JSON output SHALL contain the following fields:
- `scanned`: total files scanned (integer)
- `matched`: files matched and moved/copied (integer)
- `skipped`: files skipped (integer)
- `elapsed_seconds`: wall-clock time in seconds (float)
- `mode`: "image" or "video" (string)
- `action`: "move", "copy", or "preview" (string)
- `files_matched`: array of file paths that were matched (array of strings)
- `files_skipped`: array of file paths that were skipped (array of strings)

#### Scenario: JSON output when dry-run
- **WHEN** user runs `sift --dry-run --json ~/photos`
- **THEN** `action` field is `"preview"`
- **THEN** `files_matched` lists files that would be processed
- **THEN** no files are actually moved or copied

### Requirement: JSON to stdout only
The JSON output SHALL go to stdout. Logging, warnings, and errors SHALL still go to stderr so that JSON piped to other tools is clean.

#### Scenario: Errors go to stderr
- **WHEN** user runs `sift --json ~/nonexistent 2>/dev/null`
- **THEN** JSON is still valid (no error text pollutes stdout)
