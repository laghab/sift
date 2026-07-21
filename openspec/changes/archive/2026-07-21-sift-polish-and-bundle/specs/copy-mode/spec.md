## ADDED Requirements

### Requirement: Non-destructive copy mode
The system SHALL support a `--copy` flag that copies matching files to `SIFT_docs/` instead of moving them. The original files SHALL remain in place.

#### Scenario: Copy mode moves files to SIFT_docs without removing originals
- **WHEN** user runs `sift --copy ~/photos`
- **THEN** files with detected text are copied into `~/photos/SIFT_docs/`
- **THEN** original files remain in place

### Requirement: Dry-run preview mode
The system SHALL support a `--dry-run` flag that identifies which files would be moved/copied without performing any file operations. It SHALL print or output the list of matched files.

#### Scenario: Dry-run reports files that would be moved
- **WHEN** user runs `sift --dry-run ~/photos`
- **THEN** no files are moved or copied
- **THEN** the console shows which files contain detectable text

#### Scenario: Dry-run with --json outputs machine-readable results
- **WHEN** user runs `sift --dry-run --json ~/photos`
- **THEN** output is valid JSON with a list of matched and unmatched files
- **THEN** no files are moved or copied

### Requirement: Mode flags are mutually compatible
The system SHALL allow `--copy` and `--dry-run` to be combined. When combined, the system SHALL operate in dry-run mode regardless of the copy flag.

#### Scenario: Dry-run overrides copy
- **WHEN** user runs `sift --copy --dry-run ~/photos`
- **THEN** no files are moved or copied
- **THEN** results are reported as if copy mode was active
