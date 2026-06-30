#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

echo "=== Building Sift CLI (Linux/macOS) ==="
pyinstaller --onefile --name sift-cli sift/__main__.py

echo "=== Building Sift GUI (Linux/macOS) ==="
pyinstaller --onefile --name sift-gui \
  --add-data "sift:sift" \
  --hidden-import sift.cli \
  --hidden-import sift.gui \
  --hidden-import sift.core \
  --hidden-import sift.installer \
  --hidden-import sift.progress \
  --hidden-import sift.banner \
  sift/__main__.py

echo ""
echo "=== Windows cross-build (run on Windows) ==="
echo "To build for Windows, run on a Windows machine with Tesseract and FFmpeg"
echo "binaries placed in sift/bundle/win/ and use:"
echo ""
echo "  pyinstaller --onedir --name sift-cli ^"
echo "    --add-data \"sift;sift\" ^"
echo "    --add-data \"sift/bundle/win/bin;bin\" ^"
echo "    --hidden-import sift.cli ^"
echo "    --hidden-import sift.gui ^"
echo "    --hidden-import sift.core ^"
echo "    --hidden-import sift.installer ^"
echo "    --hidden-import sift.progress ^"
echo "    --hidden-import sift.banner ^"
echo "    sift/__main__.py"
echo ""
echo "  pyinstaller --onedir --name sift-gui ^"
echo "    --windowed ^"
echo "    --add-data \"sift;sift\" ^"
echo "    --add-data \"sift/bundle/win/bin;bin\" ^"
echo "    --hidden-import sift.cli ^"
echo "    --hidden-import sift.gui ^"
echo "    --hidden-import sift.core ^"
echo "    --hidden-import sift.installer ^"
echo "    --hidden-import sift.progress ^"
echo "    --hidden-import sift.banner ^"
echo "    sift/__main__.py"
echo ""
echo "Place tesseract.exe + DLLs + tessdata/ and ffmpeg.exe + ffprobe.exe"
echo "in sift/bundle/win/bin/ before building."
echo ""

echo "=== Done ==="
echo "Binaries in dist/:"
ls -lh dist/
