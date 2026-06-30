import sys
import os


def is_frozen():
    return getattr(sys, "frozen", False)


def bundled_path():
    if not is_frozen():
        return None
    exe_dir = os.path.dirname(sys.executable)
    return os.path.join(exe_dir, "bin")


def bundled_bin(name):
    bp = bundled_path()
    if bp is None:
        return None
    candidate = os.path.join(bp, name)
    if os.path.isfile(candidate):
        return candidate
    candidate_exe = os.path.join(bp, f"{name}.exe")
    if os.path.isfile(candidate_exe):
        return candidate_exe
    return None


def bundled_tessdata():
    bp = bundled_path()
    if bp is None:
        return None
    td = os.path.join(bp, "tessdata")
    if os.path.isdir(td):
        return td
    return None
