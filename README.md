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

Sift finds the images and videos in a folder that actually contain text, and pulls them out so you don't have to scroll past 10,000 photos to find them.

## What it's for

- **Old phone backups.** Years of WhatsApp/Telegram media dumped into one folder — screenshots of addresses, OTPs, boarding passes, and ID scans buried among memes and photos. Point Sift at the folder and it surfaces the ones with text.
- **Downloads folder archaeology.** Random screenshots you saved "for later" — whiteboard photos, error messages, code snippets, receipts — mixed in with everything else. Sift separates them out.
- **Screen recordings and video clips.** Tutorials, lecture recordings, bug-report clips — find the ones with on-screen text without re-watching every file.
- **General declutter.** Anywhere photos and "documents disguised as photos" have piled up together.

Run it, walk away, come back to a `SIFT_docs/` subfolder with the text-bearing files sorted out. Everything else stays exactly where it was.

## How it works (briefly)

Sift OCRs every image (and, in video mode, sampled frames of every video) with Tesseract. Anything with detectable text gets moved into `SIFT_docs/` in the same folder it was found in — moved, never deleted or copied, so it's fully reversible. It auto-scales to use ~70% of your CPU cores so it doesn't lock up your machine while it runs, and it'll install Tesseract/FFmpeg if you don't have them, offering to remove them again when it's done.

## Limitations

OCR isn't perfect — read this before relying on it for anything important:

- Misses low-contrast, stylized, or handwritten text
- Sensitive to image rotation and resolution
- English only by default (language-pack dependent)
- No image preprocessing, so noisy photos or photos-of-screens can produce false negatives
- Video mode only samples frames every 1–5 seconds — brief on-screen text can be missed entirely

Sift gets you most of the way there. It doesn't replace manually skimming the untouched files if completeness actually matters.

## Install

```bash
git clone https://github.com/laghab/sift.git
cd sift
pip install -e .
```

System dependencies (Tesseract is required; FFmpeg only if you'll use `--video`):

```bash
# Debian/Ubuntu
sudo apt-get install tesseract-ocr tesseract-ocr-eng ffmpeg python3-tk

# macOS
brew install tesseract tesseract-lang ffmpeg

# Arch
sudo pacman -S tesseract tesseract-data-eng ffmpeg
```

Windows: install [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki) and [FFmpeg](https://ffmpeg.org/download.html) manually and add both to your PATH.

## Usage

```bash
sift ~/directory              # scan images
sift ~/directory --video      # scan videos instead
sift ~/directory --workers 4  # override auto-detected worker count
sift-gui                      # launch the GUI
```

Dependencies Sift installs on its own are offered for removal interactively at the end of a run (apt, brew, and pacman supported). Skip the prompt with `--no-cleanup`.

## License

MIT — see [LICENSE](https://github.com/laghab/sift/blob/main/LICENSE).
