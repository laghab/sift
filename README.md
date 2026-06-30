# Sift — Digital Document Sifter

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

Sift scans directories of images and videos for text content using Tesseract OCR. Files that contain text are moved into a `SIFT_docs/` subfolder; non-text files are left in place.

## Features

- Auto-scales workers to ~70% of available CPU cores
- OCR text detection via Tesseract (defaults to English)
- Text-bearing files moved into `SIFT_docs/` subfolder, preserving directory structure
- Non-matching files untouched
- Ephemeral dependency install with opt-in cleanup
- CLI and GUI (tkinter) interfaces

## What this actually does

Files are **moved, never deleted or copied**. A text-bearing image or video ends up in `SIFT_docs/` inside the same parent directory it was found in. Nothing Sift does is destructive or irreversible — you can always move files back manually.

## Limitations

- Tesseract OCR misses low-contrast, stylized, or handwritten text
- Sensitive to image rotation and resolution
- Language-pack dependent (English only by default)
- No preprocessing or denoising — noisy photos or photos-of-screens can produce false negatives
- Video scanning only samples frames at fixed intervals (1–5s depending on duration); brief on-screen text can be missed entirely

Sift gets you most of the way there, but it does not replace manually checking untouched files if completeness matters.

## Install

```bash
git clone https://github.com/anomalyco/sift.git
cd sift
```

System dependencies:

```bash
# Debian/Ubuntu — apt
sudo apt-get install tesseract-ocr tesseract-ocr-eng ffmpeg python3-tk
```

```bash
# macOS — Homebrew
brew install tesseract tesseract-lang ffmpeg
```

```bash
# Arch Linux — pacman
sudo pacman -S tesseract tesseract-data-eng ffmpeg
```

**Windows:** Install Tesseract from [UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) and FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html). Add both to your PATH.

```bash
pip install -e .
```

## Usage

```bash
# Scan images in a directory
sift ~/directory

# Scan videos instead
sift ~/directory --video

# Control parallelism
sift ~/directory --workers 4

# Launch the GUI
sift-gui
python -m sift --gui
```

## Dependency cleanup

After a scan, Sift interactively asks whether to remove packages it installed. Cleanup currently supports `apt`, `brew`, and `pacman`. Skip with `--no-cleanup`.

## License

MIT — see [LICENSE](LICENSE).
