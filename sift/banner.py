import shutil
import os
import sys

BANNER = r"""
  ╔══════════════════════════════════════╗
  ║    ███████╗██╗███████╗████████╗      ║
  ║    ██╔════╝██║██╔════╝╚══██╔══╝      ║
  ║    ███████╗██║█████╗     ██║         ║
  ║    ╚════██║██║██╔══╝     ██║         ║
  ║    ███████║██║██║        ██║         ║
  ║    ╚══════╝╚═╝╚═╝        ╚═╝         ║
  ║       Digital Document Sifter        ║
  ╚══════════════════════════════════════╝
"""

SHORT_TAG = "Sift v{} — Digital Document Sifter"

COLORS = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "cyan": "\033[96m",
    "reset": "\033[0m",
    "bold": "\033[1m",
}


def supports_color():
    if not sys.stdout.isatty():
        return False
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("TERM") == "dumb":
        return False
    return True


def color(text, color_name):
    if supports_color() and color_name in COLORS:
        return f"{COLORS[color_name]}{text}{COLORS['reset']}"
    return text


def print_banner():
    term_width = shutil.get_terminal_size((80, 20)).columns
    for line in BANNER.strip("\n").split("\n"):
        print(color(line, "cyan"))


def print_header():
    print_banner()
    print()
