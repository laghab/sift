import os
import re
import subprocess
import tempfile
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .banner import color
from .progress import ProgressTracker


IMG_EXTENSIONS = (".jpg", ".jpeg", ".png")
VID_EXTENSIONS = (".mp4", ".mkv", ".mov", ".avi", ".3gp", ".webm")
DOC_DIR_NAME = "SIFT_docs"


def count_meaningful_words(text):
    count = 0
    for word in text.split():
        clean = re.sub(r"[^a-zA-Z]", "", word)
        if len(clean) >= 3:
            count += 1
    return count


def ocr_image(img_path, lang="eng"):
    try:
        r = subprocess.run(
            ["tesseract", str(img_path), "stdout", "--psm", "3", "-l", lang],
            capture_output=True, text=True, timeout=60, env={**os.environ, "OMP_THREAD_LIMIT": "1"}
        )
        return r.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return ""


def ocr_image_word_count(img_path, lang="eng"):
    text = ocr_image(img_path, lang)
    return count_meaningful_words(text)


def get_worker_count():
    try:
        cores = os.cpu_count() or 4
        workers = max(1, int(cores * 0.7))
        return workers
    except Exception:
        return 2


def _unique_dest(doc_dir, stem, suffix):
    dest = doc_dir / f"{stem}{suffix}"
    if not dest.exists():
        return dest
    for i in range(2, 1000):
        dest = doc_dir / f"{stem}_sifted{i}{suffix}"
        if not dest.exists():
            return dest
    return dest


def scan_images(directory, lang="eng", workers=None, progress=None, stop_event=None):
    if workers is None:
        workers = get_worker_count()

    directory = Path(directory).resolve()
    images = []
    for ext in IMG_EXTENSIONS:
        images.extend(directory.rglob(f"*{ext}"))
        images.extend(directory.rglob(f"*{ext.upper()}"))

    images = [p for p in images if DOC_DIR_NAME not in p.parts]
    total = len(images)

    if progress:
        progress.set_total(total, "images")

    moved = 0
    skipped = 0
    stopped = False

    def process(img_path):
        nonlocal moved, skipped, stopped
        if stop_event and stop_event.is_set():
            stopped = True
            return False
        if progress:
            progress.update(1, f"Scanning: {img_path.name}")
        if ocr_image_word_count(img_path, lang) >= 2:
            parent = img_path.parent
            rel = parent.relative_to(directory)
            doc_dir = directory / DOC_DIR_NAME / rel if str(rel) != "." else directory / DOC_DIR_NAME
            doc_dir.mkdir(parents=True, exist_ok=True)
            dest = _unique_dest(doc_dir, img_path.stem, img_path.suffix)
            shutil.move(str(img_path), str(dest))
            return True
        return False

    pool = ThreadPoolExecutor(max_workers=workers)
    futures = {pool.submit(process, img): img for img in images}
    try:
        for future in as_completed(futures):
            if stop_event and stop_event.is_set():
                for f in futures:
                    f.cancel()
                break
            if future.result():
                moved += 1
            else:
                skipped += 1
    except KeyboardInterrupt:
        for f in futures:
            f.cancel()
        raise
    finally:
        pool.shutdown(wait=False)

    return moved, skipped, total


def scan_videos(directory, lang="eng", workers=None, progress=None, min_words=5, stop_event=None):
    if workers is None:
        workers = get_worker_count()

    directory = Path(directory).resolve()
    videos = []
    for ext in VID_EXTENSIONS:
        videos.extend(directory.rglob(f"*{ext}"))
        videos.extend(directory.rglob(f"*{ext.upper()}"))

    videos = [p for p in videos if DOC_DIR_NAME not in p.parts]
    total = len(videos)

    if progress:
        progress.set_total(total, "videos")

    moved = 0
    skipped = 0
    stopped = False

    def get_duration(video_path):
        try:
            r = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "csv=p=0", str(video_path)],
                capture_output=True, text=True, timeout=30
            )
            return float(r.stdout.strip())
        except Exception:
            return 0

    def extract_frames(video_path, duration):
        if stop_event and stop_event.is_set():
            return [], None
        if duration < 15:
            interval = 1
        elif duration < 60:
            interval = 2
        else:
            interval = 5
        tmpdir = tempfile.mkdtemp(prefix="sift_video_")
        try:
            subprocess.run(
                ["ffmpeg", "-i", str(video_path), "-vf", f"fps=1/{interval}",
                 "-q:v", "5", f"{tmpdir}/frame%03d.jpg", "-y"],
                capture_output=True, timeout=120, env={**os.environ, "OMP_THREAD_LIMIT": "1"}
            )
            frames = sorted(Path(tmpdir).glob("*.jpg"))
            return frames, tmpdir
        except Exception:
            shutil.rmtree(tmpdir, ignore_errors=True)
            return [], None

    def process(video_path):
        nonlocal moved, skipped, stopped
        if stop_event and stop_event.is_set():
            stopped = True
            return False
        if progress:
            progress.update(1, f"Scanning: {video_path.name}")
        duration = get_duration(video_path)
        frames, tmpdir = extract_frames(video_path, duration)
        if not frames:
            skipped += 1
            return False
        try:
            total_words = 0
            for frame in frames:
                total_words += ocr_image_word_count(frame, lang)
                if total_words >= min_words:
                    parent = video_path.parent
                    rel = parent.relative_to(directory)
                    doc_dir = directory / DOC_DIR_NAME / rel if str(rel) != "." else directory / DOC_DIR_NAME
                    doc_dir.mkdir(parents=True, exist_ok=True)
                    dest = _unique_dest(doc_dir, video_path.stem, video_path.suffix)
                    shutil.move(str(video_path), str(dest))
                    return True
            return False
        finally:
            if tmpdir:
                shutil.rmtree(tmpdir, ignore_errors=True)

    pool = ThreadPoolExecutor(max_workers=workers)
    futures = {pool.submit(process, vid): vid for vid in videos}
    try:
        for future in as_completed(futures):
            if stop_event and stop_event.is_set():
                for f in futures:
                    f.cancel()
                break
            if future.result():
                moved += 1
            else:
                skipped += 1
    except KeyboardInterrupt:
        for f in futures:
            f.cancel()
        raise
    finally:
        pool.shutdown(wait=False)

    return moved, skipped, total
