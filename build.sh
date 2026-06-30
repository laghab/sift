#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

echo "=== Building Sift CLI ==="
pyinstaller --onefile --name sift-cli sift/__main__.py

echo "=== Building Sift GUI ==="
pyinstaller --onefile --name sift-gui \
  --add-data "sift:sift" \
  --hidden-import sift.cli \
  --hidden-import sift.gui \
  --hidden-import sift.core \
  --hidden-import sift.installer \
  --hidden-import sift.progress \
  --hidden-import sift.banner \
  sift/__main__.py

echo "=== Done ==="
echo "Binaries in dist/:"
ls -lh dist/
