import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
import os
import sys
import time

from . import __version__
from .core import scan_images, scan_videos, get_worker_count
from .progress import ProgressTracker
from .installer import ensure_deps, cleanup


class SiftGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"Sift v{__version__} — Digital Document Sifter")
        self.root.geometry("650x550")
        self.root.minsize(600, 400)

        try:
            self.root.iconbitmap(default="")
        except Exception:
            pass

        self.running = False
        self.need_video = False
        self.stop_event = threading.Event()
        self.lang = "eng"
        self.progress = ProgressTracker()
        self._build_ui()

    def _build_ui(self):
        header = tk.Frame(self.root, bg="#1a1a2e", height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        title = tk.Label(
            header,
            text="SIFT",
            font=("Courier", 28, "bold"),
            fg="#00d4ff",
            bg="#1a1a2e",
        )
        title.pack(pady=(10, 0))

        subtitle = tk.Label(
            header,
            text="Digital Document Sifter",
            font=("Courier", 11),
            fg="#888",
            bg="#1a1a2e",
        )
        subtitle.pack()

        main = tk.Frame(self.root, padx=20, pady=15)
        main.pack(fill=tk.BOTH, expand=True)

        dir_frame = tk.LabelFrame(main, text="Directory", padx=10, pady=10)
        dir_frame.pack(fill=tk.X, pady=(0, 10))

        self.dir_var = tk.StringVar()
        dir_entry = tk.Entry(dir_frame, textvariable=self.dir_var, font=("", 10))
        dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        browse_btn = tk.Button(dir_frame, text="Browse", command=self._browse, width=10)
        browse_btn.pack(side=tk.RIGHT)

        opts_frame = tk.LabelFrame(main, text="Options", padx=10, pady=10)
        opts_frame.pack(fill=tk.X, pady=(0, 10))

        self.video_var = tk.BooleanVar(value=False)
        video_cb = tk.Checkbutton(
            opts_frame, text="Scan videos instead of images (needs ffmpeg)",
            variable=self.video_var
        )
        video_cb.pack(anchor=tk.W)

        lang_frame = tk.Frame(opts_frame)
        lang_frame.pack(anchor=tk.W, pady=(5, 0))
        tk.Label(lang_frame, text="OCR Language:").pack(side=tk.LEFT)
        self.lang_var = tk.StringVar(value="eng")
        lang_entry = tk.Entry(lang_frame, textvariable=self.lang_var, width=10)
        lang_entry.pack(side=tk.LEFT, padx=(5, 0))

        workers_frame = tk.Frame(opts_frame)
        workers_frame.pack(anchor=tk.W, pady=(5, 0))
        tk.Label(workers_frame, text="Workers:").pack(side=tk.LEFT)
        self.workers_var = tk.StringVar(value=str(get_worker_count()))
        workers_spin = tk.Spinbox(
            workers_frame, from_=1, to=64,
            textvariable=self.workers_var, width=5
        )
        workers_spin.pack(side=tk.LEFT, padx=(5, 0))

        progress_frame = tk.LabelFrame(main, text="Progress", padx=10, pady=10)
        progress_frame.pack(fill=tk.BOTH, expand=True)

        self.progress_bar = ttk.Progressbar(progress_frame, mode="determinate")
        self.progress_bar.pack(fill=tk.X, pady=(0, 8))

        self.status_text = tk.StringVar(value="Ready")
        status_label = tk.Label(
            progress_frame, textvariable=self.status_text,
            font=("", 9), anchor=tk.W, justify=tk.LEFT
        )
        status_label.pack(fill=tk.X)

        self.log_text = tk.Text(progress_frame, height=6, font=("Courier", 8), state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        scrollbar = tk.Scrollbar(self.log_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)

        btn_frame = tk.Frame(main)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        self.start_btn = tk.Button(
            btn_frame, text="▶ Start Scan", command=self._start_scan,
            bg="#28a745", fg="white", font=("", 10, "bold"), padx=15
        )
        self.start_btn.pack(side=tk.LEFT)

        self.stop_btn = tk.Button(
            btn_frame, text="■ Stop", command=self._stop_scan,
            bg="#dc3545", fg="white", font=("", 10, "bold"), padx=15,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=(10, 0))

    def _browse(self):
        d = filedialog.askdirectory(title="Select directory to scan")
        if d:
            self.dir_var.set(d)

    def _log(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()

    def _on_progress(self, pt):
        info = pt.get_progress()
        self.progress_bar["value"] = info["pct"]
        self.status_text.set(
            f"Scanned: {info['current']}/{info['total']} {info['label']}  "
            f"({info['pct']:.1f}%)  "
            f"Rate: {info['rate']:.1f}/s  "
            f"ETA: {time.strftime('%M:%S', time.gmtime(info['eta']))}\n"
            f"{info['status_text']}"
        )

    def _scan_worker(self, directory, lang, workers, video):
        try:
            installed = ensure_deps(need_video=video)
            mode = "videos" if video else "images"
            self._log(f"Scanning {mode} in: {directory}")
            self._log(f"Workers: {workers}")
            self._log("Starting scan...")

            self.progress.callback = self._on_progress
            if video:
                moved, skipped, total = scan_videos(
                    directory, lang, workers, self.progress, stop_event=self.stop_event
                )
            else:
                moved, skipped, total = scan_images(
                    directory, lang, workers, self.progress, stop_event=self.stop_event
                )

            if self.stop_event.is_set():
                self._log("Scan cancelled by user.")
            else:
                self._log(f"{mode.capitalize()}: {moved} with text moved, {skipped} skipped (of {total})")
                self._log("")
                self._log("✓ Scan complete!")
                messagebox.showinfo("Sift Complete", f"Scan finished!\n\n{mode.capitalize()}: {moved} text {mode} moved")

                for pkg in installed:
                    if messagebox.askyesno("Cleanup", f"Remove installed dependency '{pkg}'?"):
                        cleanup([pkg])

        except Exception as e:
            self._log(f"ERROR: {e}")
            messagebox.showerror("Error", str(e))
        finally:
            self.running = False
            self.stop_event.clear()
            self.root.after(0, self._set_idle)

    def _set_idle(self):
        self.start_btn.config(state=tk.NORMAL, text="▶ Start Scan")
        self.stop_btn.config(state=tk.DISABLED)
        self.progress_bar["value"] = 0
        if not self.status_text.get().startswith("✓"):
            self.status_text.set("Ready")

    def _set_running(self):
        self.start_btn.config(state=tk.DISABLED, text="Scanning...")
        self.stop_btn.config(state=tk.NORMAL)

    def _start_scan(self):
        directory = self.dir_var.get().strip()
        if not directory:
            messagebox.showwarning("No Directory", "Please select a directory to scan.")
            return
        if not os.path.isdir(directory):
            messagebox.showerror("Invalid Directory", f"'{directory}' is not a valid directory.")
            return

        self.running = True
        self.stop_event.clear()
        self.need_video = self.video_var.get()
        self.lang = self.lang_var.get().strip() or "eng"
        self.workers = int(self.workers_var.get().strip() or get_worker_count())
        self._set_running()
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)

        thread = threading.Thread(
            target=self._scan_worker,
            args=(directory, self.lang, self.workers, self.need_video),
            daemon=True
        )
        thread.start()

    def _stop_scan(self):
        self.stop_event.set()
        self._log("Stopping... (will finish current file)")
        self.start_btn.config(state=tk.DISABLED, text="Stopping...")

    def run(self):
        self.root.mainloop()


def gui_main():
    try:
        app = SiftGUI()
        app.run()
    except ImportError as e:
        from .banner import color
        print(f"  {color('Error:', 'red')} Could not launch GUI: {e}")
        print("  Install tkinter: sudo apt-get install python3-tk")
        sys.exit(1)
