## Purpose

Allow users to search for specific text content within files, rather than matching all files with any text. Supports combination with threshold and video mode.

## Requirements

### Requirement: Search by text content
The system SHALL support a `--search <term>` flag that only matches files whose OCR text contains the given search term. Matching SHALL be case-insensitive.

#### Scenario: Search matches files containing the term
- **WHEN** user runs `sift --search "invoice" ~/photos`
- **THEN** only files whose OCR text contains "invoice" (case-insensitive) are moved to `SIFT_docs/`

#### Scenario: Search with no matches
- **WHEN** user runs `sift --search "nonexistent" ~/photos`
- **THEN** no files are moved
- **THEN** the summary reports 0 files matched

### Requirement: Search combined with threshold
The system SHALL support `--search` combined with `--threshold`. A file MUST meet both criteria (contains search term AND exceeds minimum word count) to be matched.

#### Scenario: Search and threshold both required
- **WHEN** user runs `sift --search "hello" --threshold 10 ~/photos`
- **THEN** a file with "hello" but only 3 total words is NOT matched
- **THEN** a file with "hello" and 15 total words IS matched

### Requirement: Search in video mode
The `--search` flag SHALL work in video mode (`--video`). The search term SHALL be checked against the aggregated OCR text from all sampled frames.

#### Scenario: Search finds term in video frames
- **WHEN** user runs `sift --video --search "error" ~/videos`
- **THEN** videos containing "error" in any sampled frame are moved to `SIFT_docs/`
