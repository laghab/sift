# Sift — Digital Document Sifter

[![Go Report Card](https://goreportcard.com/badge/github.com/laghab/sift)](https://goreportcard.com/report/github.com/laghab/sift)
[![GitHub release](https://img.shields.io/github/v/release/laghab/sift)](https://github.com/laghab/sift/releases/latest)
[![Go version](https://img.shields.io/github/go-mod/go-version/laghab/sift)](https://go.dev/)
[![License](https://img.shields.io/github/license/laghab/sift)](LICENSE)

```
  ╔══════════════════════════════════════╗
  ║    ███████╗██╗███████╗████████╗      ║
  ║    ██╔════╝██║██╔════╝╚══██╔══╝      ║
  ║    ███████╗██║█████╗     ██║         ║
  ║    ╚════██║██║██╔══╝     ██║         ║
  ║    ███████║██║██║        ██║         ║
  ║    ╚══════╝╚═╝╚═╝        ╚═╝         ║
  ║       Digital Document Sifter        ║
  ╚══════════════════════════════════════╝
```

Sift finds the images and videos in a folder that actually contain text, and pulls them out so you don't have to scroll past 10,000 photos to find them.

## What it's for

- **Old phone backups.** Years of WhatsApp/Telegram media dumped into one folder — screenshots of addresses, OTPs, boarding passes, and ID scans buried among memes and photos. Point Sift at the folder and it surfaces the ones with text.
- **Downloads folder archaeology.** Random screenshots you saved "for later" — whiteboard photos, error messages, code snippets, receipts — mixed in with everything else. Sift separates them out.
- **Screen recordings and video clips.** Tutorials, lecture recordings, bug-report clips — find the ones with on-screen text without re-watching every file.
- **General declutter.** Anywhere photos and "documents disguised as photos" have piled up together.

Run it, walk away, come back to a `SIFT_docs/` subfolder with the text-bearing files sorted out. Everything else stays exactly where it was.

## How it works (briefly)

Sift OCRs every image (and, in video mode, sampled frames of every video) with Tesseract. Anything with detectable text gets moved into `SIFT_docs/` in the same folder it was found in. It auto-scales to use ~70% of your CPU cores so it doesn't lock up your machine while it runs. Video mode requires ffmpeg on PATH.

## Limitations

OCR isn't perfect — read this before relying on it for anything important:

- Misses low-contrast, stylized, or handwritten text
- Sensitive to image rotation and resolution
- English only by default (language-pack dependent)
- No image preprocessing, so noisy photos or photos-of-screens can produce false negatives
- Video mode only samples frames every 1–5 seconds — brief on-screen text can be missed entirely

Sift gets you most of the way there. It doesn't replace manually skimming the untouched files if completeness actually matters.

## Install

### Binary download (recommended — no dependencies)

Download the latest binary for your platform from the [releases page](https://github.com/laghab/sift/releases):

```bash
# Linux/macOS
curl -fsSL https://github.com/laghab/sift/releases/latest/download/sift_linux_amd64.tar.gz | tar xz
./sift ~/photos

# Windows
# Download sift_windows_amd64.tar.gz from releases, extract, run sift.exe
```

Or via install script:

```bash
curl -fsSL https://github.com/laghab/sift/releases/latest/download/install.sh | bash
```

### Go toolchain

```bash
go install github.com/laghab/sift/cmd/sift@latest
```

### Legacy Python version (GUI only)

The Go rewrite is CLI-only. For the Tkinter GUI, use the Python version:

```bash
git clone https://github.com/laghab/sift.git
cd sift
pip install -e .
sift-gui
```

## Usage

```bash
sift ~/photos                      # scan images (default: move text files)
sift ~/photos --copy               # copy instead of move
sift ~/photos --dry-run            # preview what would be moved
sift ~/photos --search invoice     # only match files containing "invoice"
sift ~/photos --json               # machine-readable JSON output
sift ~/photos --video              # scan videos instead (needs ffmpeg on PATH)
sift ~/photos --threshold 10       # require 10+ meaningful words
sift ~/photos --workers 4          # override CPU count
```

All flags can be combined. For example:

```bash
sift ~/WhatsAppBackup --copy --search "address" --json
```

## License

MIT — see [LICENSE](https://github.com/laghab/sift/blob/main/LICENSE).
