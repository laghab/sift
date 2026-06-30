import argparse
import sys
import os
import time

from . import __version__
from .banner import print_header, color
from .core import scan_images, scan_videos, get_worker_count
from .progress import ProgressTracker, CLIProgress
from .installer import ensure_deps, cleanup


def format_summary(moved, skipped, total, elapsed, label="images"):
    pct = (moved / total * 100) if total > 0 else 0
    elapsed_str = time.strftime("%M:%S", time.gmtime(elapsed))
    summary = [
        "",
        color("  ─────────────────────────────────────", "cyan"),
        color(f"  SIFT COMPLETE", "green"),
        color("  ─────────────────────────────────────", "cyan"),
        f"  {label.capitalize()} scanned:  {total}",
        f"  Text found → moved: {color(str(moved), 'green')} ({pct:.1f}%)",
        f"  No text (left):    {skipped}",
        f"  Time taken:        {elapsed_str}",
        color("  ─────────────────────────────────────", "cyan"),
        "",
    ]
    return "\n".join(summary)


def run_cli(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog="sift",
        description="Sift — Digital Document Sifter. Finds images/videos containing text using OCR.",
    )
    parser.add_argument(
        "directory", nargs="?", default=".",
        help="Directory to scan (default: current directory)"
    )
    parser.add_argument(
        "--video", "-v", action="store_true",
        help="Scan videos instead of images (requires ffmpeg)"
    )
    parser.add_argument(
        "--workers", "-w", type=int, default=None,
        help=f"Number of parallel workers (default: 70%% of CPU = {get_worker_count()})"
    )
    parser.add_argument(
        "--lang", "-l", default="eng",
        help="Tesseract language (default: eng)"
    )
    parser.add_argument(
        "--threshold", "-t", type=int, default=5,
        help="Minimum meaningful words to consider as document (default: 5)"
    )
    parser.add_argument(
        "--no-cleanup", action="store_true",
        help="Skip prompt to remove installed dependencies"
    )
    parser.add_argument(
        "--version", action="version", version=f"Sift v{__version__}"
    )

    parsed = parser.parse_args(args)

    if parsed.directory == "." and len(sys.argv) == 1:
        parser.print_help()
        print()
        print("  Example: sift ~/WhatsAppBackup")
        print("           sift ~/WhatsAppBackup --video")
        print()
        sys.exit(0)

    target = os.path.abspath(parsed.directory)
    if not os.path.isdir(target):
        print(f"  Error: '{target}' is not a valid directory.")
        sys.exit(1)

    print_header()
    print(f"  Target:  {color(target, 'yellow')}")
    workers = parsed.workers or get_worker_count()
    print(f"  Workers: {workers} ({color(str(workers), 'green')} parallel)")
    print(f"  Mode:    {'Video' if parsed.video else 'Image'} scan")
    if parsed.video:
        print(f"  Threshold: {parsed.threshold}+ words")
    print()

    try:
        installed = ensure_deps(need_video=parsed.video)
    except RuntimeError as e:
        print(f"  {color('Error:', 'red')} {e}")
        sys.exit(1)
    print()

    progress = ProgressTracker()
    cli_progress = CLIProgress()

    def on_update(pt):
        cli_progress.render(pt)

    progress.callback = on_update

    t0 = time.time()
    try:
        if parsed.video:
            moved, skipped, total = scan_videos(target, parsed.lang, workers, progress, parsed.threshold)
        else:
            moved, skipped, total = scan_images(target, parsed.lang, workers, progress)
    except KeyboardInterrupt:
        print()
        print(color("  Interrupted by user.", "yellow"))
        sys.exit(130)
    elapsed = time.time() - t0
    print(format_summary(moved, skipped, total, elapsed, "videos" if parsed.video else "images"))

    print()

    if not parsed.no_cleanup:
        cleanup(installed)
