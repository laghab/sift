import subprocess
import shutil
import sys
import os
import platform


def run(cmd, capture=True):
    try:
        r = subprocess.run(cmd, capture_output=capture, text=True, timeout=120)
        return r.returncode == 0, r.stdout.strip() if capture else ""
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False, ""


def which(name):
    return shutil.which(name) is not None


def check_tesseract():
    if which("tesseract"):
        ok, out = run(["tesseract", "--list-langs"])
        has_eng = "eng" in out if out else False
        return True, has_eng
    return False, False


def check_ffmpeg():
    return which("ffmpeg") and which("ffprobe")


def _windows_manual_instructions():
    print("  Windows detected. Install manually:")
    print("    Tesseract: https://github.com/UB-Mannheim/tesseract/wiki")
    print("    FFmpeg:    https://ffmpeg.org/download.html")
    print("  Add both to your PATH after installation.")


def _warn_sudo():
    if not sys.stdout.isatty():
        print("  (sudo may prompt for password — run from a terminal if it hangs)")


def install_tesseract():
    print("  Installing Tesseract OCR...")
    if platform.system() == "Windows":
        _windows_manual_instructions()
        return False
    if which("apt-get"):
        _warn_sudo()
        ok, _ = run(["sudo", "apt-get", "install", "-y", "tesseract-ocr", "tesseract-ocr-eng"])
        return ok
    elif which("brew"):
        ok, _ = run(["brew", "install", "tesseract"])
        if ok:
            run(["brew", "install", "tesseract-lang"])
        return ok
    elif which("pacman"):
        _warn_sudo()
        ok, _ = run(["sudo", "pacman", "-S", "--noconfirm", "tesseract", "tesseract-data-eng"])
        return ok
    else:
        print("  Could not detect package manager. Install tesseract manually.")
        return False


def install_ffmpeg():
    print("  Installing FFmpeg...")
    if platform.system() == "Windows":
        _windows_manual_instructions()
        return False
    if which("apt-get"):
        _warn_sudo()
        ok, _ = run(["sudo", "apt-get", "install", "-y", "ffmpeg"])
        return ok
    elif which("brew"):
        ok, _ = run(["brew", "install", "ffmpeg"])
        return ok
    elif which("pacman"):
        _warn_sudo()
        ok, _ = run(["sudo", "pacman", "-S", "--noconfirm", "ffmpeg"])
        return ok
    else:
        print("  Could not detect package manager. Install ffmpeg manually.")
        return False


def ensure_deps(need_video=False):
    if platform.system() == "Windows":
        print("  Windows detected — Sift requires system binaries.")
        _windows_manual_instructions()
        raise RuntimeError("Install Tesseract manually on Windows (see instructions above)")

    installed_by_us = []
    had_tesseract, has_eng = check_tesseract()

    if not had_tesseract:
        print("  Tesseract OCR not found.")
        if install_tesseract():
            installed_by_us.append("tesseract")
            print("  Tesseract installed.")
        else:
            print("  Failed to install Tesseract.")
            raise RuntimeError("Failed to install Tesseract OCR. Install it manually: sudo apt-get install tesseract-ocr tesseract-ocr-eng")
    elif not has_eng:
        print("  Installing English language pack for Tesseract...")
        if which("apt-get"):
            _warn_sudo()
            run(["sudo", "apt-get", "install", "-y", "tesseract-ocr-eng"])
        installed_by_us.append("tesseract-eng")
        print("  English language pack installed.")

    if need_video:
        if not check_ffmpeg():
            print("  FFmpeg not found.")
            if install_ffmpeg():
                installed_by_us.append("ffmpeg")
                print("  FFmpeg installed.")
            else:
                print("  Failed to install FFmpeg.")
                raise RuntimeError("Failed to install FFmpeg. Install it manually: sudo apt-get install ffmpeg")

    return installed_by_us


def _apt_package_name(pkg):
    mapping = {
        "tesseract": "tesseract-ocr",
        "tesseract-eng": "tesseract-ocr-eng",
    }
    return mapping.get(pkg, pkg)


def cleanup(installed_by_us):
    if not installed_by_us:
        return
    print()
    print(f"  Sift installed {len(installed_by_us)} package(s). Clean up?")
    for pkg in installed_by_us:
        ans = input(f"  Remove {pkg}? [y/N]: ").strip().lower()
        if ans != "y":
            continue
        if which("apt-get"):
            name = _apt_package_name(pkg)
            _warn_sudo()
            run(["sudo", "apt-get", "remove", "-y", name])
            print(f"  Removed {pkg}.")
        elif which("brew"):
            run(["brew", "uninstall", pkg])
            print(f"  Removed {pkg} (brew).")
        elif which("pacman"):
            _warn_sudo()
            run(["sudo", "pacman", "-R", "--noconfirm", pkg])
            print(f"  Removed {pkg} (pacman).")
        else:
            print("  Skipping removal (unsupported package manager).")
