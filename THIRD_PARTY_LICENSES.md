# Third-Party Licenses

Sift itself is MIT-licensed (see [LICENSE](./LICENSE)). When distributed as a
standalone Windows executable, it bundles the following third-party binaries.
Each is used as an unmodified, separate process (no static or dynamic linking
from Sift's own code), and each carries its own license terms.

---

## Tesseract OCR

- **License:** Apache License 2.0
- **Source:** https://github.com/tesseract-ocr/tesseract
- **License text:** https://www.apache.org/licenses/LICENSE-2.0

Tesseract is bundled in the Windows release as `bin/tesseract.exe`, supporting
DLLs, and `bin/tessdata/eng.traineddata`. No modifications have been made.

---

## FFmpeg

- **License:** LGPL 2.1+
- **Source:** https://ffmpeg.org
- **License text:** https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html

The LGPL "essentials" build is bundled in the Windows release as
`bin/ffmpeg.exe` and `bin/ffprobe.exe`. No modifications have been made.

The LGPL build does not include GPL-licensed codecs (e.g. libx264). Because
FFmpeg is invoked as a separate process rather than statically linked into
Sift, there is no source-disclosure obligation for Sift itself beyond
providing this notice.
