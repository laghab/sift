import sys
import time
import threading
import shutil


class ProgressTracker:
    def __init__(self, callback=None):
        self.total = 0
        self.current = 0
        self.moved = 0
        self.label = "items"
        self.status_text = ""
        self.start_time = None
        self.lock = threading.Lock()
        self.callback = callback

    def set_total(self, total, label="items"):
        self.total = total
        self.label = label
        self.current = 0
        self.start_time = time.time()

    def update(self, n=1, status_text=""):
        with self.lock:
            self.current += n
            if status_text:
                self.status_text = status_text
        if self.callback:
            self.callback(self)

    def get_progress(self):
        with self.lock:
            elapsed = time.time() - self.start_time if self.start_time else 0
            pct = (self.current / self.total * 100) if self.total > 0 else 0
            rate = self.current / elapsed if elapsed > 0 else 0
            eta = (self.total - self.current) / rate if rate > 0 else 0
            return {
                "current": self.current,
                "total": self.total,
                "pct": pct,
                "elapsed": elapsed,
                "eta": eta,
                "rate": rate,
                "label": self.label,
                "status_text": self.status_text,
            }


class CLIProgress:
    BAR_WIDTH = 30

    def render(self, progress):
        info = progress.get_progress()
        cols = shutil.get_terminal_size((80, 20)).columns

        pct = info["pct"]
        filled = int(self.BAR_WIDTH * pct / 100)
        bar = "█" * filled + "╸" * (self.BAR_WIDTH - filled)

        elapsed_str = time.strftime("%M:%S", time.gmtime(info["elapsed"]))

        line = f"  {bar}  {pct:5.1f}%  [{info['current']}/{info['total']} {info['label']}]  ⏱ {elapsed_str}"
        if info["status_text"]:
            suffix = f"  {info['status_text']}"
            if len(line) + len(suffix) < cols:
                line += suffix

        sys.stdout.write("\r" + line.ljust(cols))
        sys.stdout.flush()
