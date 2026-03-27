import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import subprocess
import sys
import os
import json
import threading

# ── Default values (mirrors your map_generator.py defaults) ──────────────────
DEFAULTS = {
    "primaryColor":   "lightblue",
    "secondaryColor": "gray",
    "textColor":      "black",
    "noDataColor":    "white",
    "fontSize":       20,
    "useGradient":    True,
    "gradientMin":    0.20,
    "gradientMax":    0.90,
    "mapWith":        40,
    "mapDepht":       20,
    "mapName":        "test",
    "dataPath":       "/workspaces/alumanimMapUsingGeopanda/data/Aluminium Can Recycling.csv",
    "latLongPath":    "/workspaces/alumanimMapUsingGeopanda/data/countries_latlon.csv",
    "europPath":      "/workspaces/alumanimMapUsingGeopanda/data/Aluminium Can Recycling Europe.csv",
}

GENERATOR_SCRIPT = os.path.join(os.path.dirname(__file__), "map_generator.py")

# ── Colour palette ────────────────────────────────────────────────────────────
BG       = "#0f1117"
PANEL    = "#1a1d27"
ACCENT   = "#3d8ef8"
ACCENT2  = "#62c6b0"
TEXT     = "#e8eaf0"
MUTED    = "#6b7280"
BORDER   = "#2a2d3a"
SUCCESS  = "#4ade80"
ERROR    = "#f87171"
ENTRY_BG = "#242736"

FONT_MONO  = ("Courier New", 10)
FONT_LABEL = ("Georgia", 10)
FONT_HEAD  = ("Georgia", 13, "bold")
FONT_TITLE = ("Georgia", 18, "bold")


class ColorEntry(tk.Frame):
    """A small colour swatch + text entry combo."""
    def __init__(self, parent, var, **kw):
        super().__init__(parent, bg=PANEL, **kw)
        self.var = var
        self.swatch = tk.Label(self, width=2, bg=var.get(), relief="flat", cursor="hand2")
        self.swatch.pack(side="left", padx=(0, 6))
        self.swatch.bind("<Button-1>", self._pick)
        entry = tk.Entry(self, textvariable=var, bg=ENTRY_BG, fg=TEXT,
                         insertbackground=TEXT, relief="flat", font=FONT_MONO,
                         width=14, bd=0)
        entry.pack(side="left")
        var.trace_add("write", lambda *_: self._update_swatch())

    def _update_swatch(self):
        try:
            self.swatch.config(bg=self.var.get())
        except Exception:
            pass

    def _pick(self, _=None):
        from tkinter.colorchooser import askcolor
        col = askcolor(color=self.var.get(), title="Pick colour")
        if col and col[1]:
            self.var.set(col[1])


class MapGeneratorGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Map Generator")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.minsize(1100, 700)

        # ── Variables ──────────────────────────────────────────────────────
        self.v_primaryColor   = tk.StringVar(value=DEFAULTS["primaryColor"])
        self.v_secondaryColor = tk.StringVar(value=DEFAULTS["secondaryColor"])
        self.v_textColor      = tk.StringVar(value=DEFAULTS["textColor"])
        self.v_noDataColor    = tk.StringVar(value=DEFAULTS["noDataColor"])
        self.v_fontSize       = tk.IntVar(value=DEFAULTS["fontSize"])
        self.v_useGradient    = tk.BooleanVar(value=DEFAULTS["useGradient"])
        self.v_gradientMin    = tk.DoubleVar(value=DEFAULTS["gradientMin"])
        self.v_gradientMax    = tk.DoubleVar(value=DEFAULTS["gradientMax"])
        self.v_mapWith        = tk.IntVar(value=DEFAULTS["mapWith"])
        self.v_mapDepht       = tk.IntVar(value=DEFAULTS["mapDepht"])
        self.v_mapName        = tk.StringVar(value=DEFAULTS["mapName"])
        self.v_dataPath       = tk.StringVar(value=DEFAULTS["dataPath"])
        self.v_latLongPath    = tk.StringVar(value=DEFAULTS["latLongPath"])
        self.v_europPath      = tk.StringVar(value=DEFAULTS["europPath"])

        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Top bar
        topbar = tk.Frame(self, bg=BG, pady=14)
        topbar.pack(fill="x", padx=24)
        tk.Label(topbar, text="◈ MAP GENERATOR", font=FONT_TITLE,
                 bg=BG, fg=ACCENT).pack(side="left")
        tk.Label(topbar, text="configure → generate → preview",
                 font=("Georgia", 10), bg=BG, fg=MUTED).pack(side="left", padx=16, pady=4)

        divider = tk.Frame(self, bg=BORDER, height=1)
        divider.pack(fill="x")

        # Main body
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=18, pady=12)

        # Left panel (controls)
        left = tk.Frame(body, bg=PANEL, bd=0, highlightthickness=1,
                        highlightbackground=BORDER)
        left.pack(side="left", fill="y", padx=(0, 12))
        left.pack_propagate(False)
        left.config(width=360)

        canvas = tk.Canvas(left, bg=PANEL, bd=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(left, orient="vertical", command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg=PANEL)
        self.scroll_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>",
            lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        self._build_controls(self.scroll_frame)

        # Right panel (preview)
        right = tk.Frame(body, bg=PANEL, bd=0, highlightthickness=1,
                         highlightbackground=BORDER)
        right.pack(side="left", fill="both", expand=True)

        prev_header = tk.Frame(right, bg=PANEL, pady=10)
        prev_header.pack(fill="x", padx=16)
        tk.Label(prev_header, text="PREVIEW", font=FONT_HEAD,
                 bg=PANEL, fg=ACCENT2).pack(side="left")

        self.img_label = tk.Label(right, bg=PANEL, text="No map generated yet.",
                                  fg=MUTED, font=("Georgia", 12))
        self.img_label.pack(fill="both", expand=True, padx=10, pady=10)
        self.img_label.bind("<Configure>", self._resize_preview)
        self._raw_image = None

        # Status bar
        self.status_var = tk.StringVar(value="Ready.")
        statusbar = tk.Frame(self, bg=BORDER, height=1)
        statusbar.pack(fill="x")
        sf = tk.Frame(self, bg=BG, pady=6)
        sf.pack(fill="x", padx=24)
        self.status_dot = tk.Label(sf, text="●", fg=MUTED, bg=BG, font=("Courier New", 11))
        self.status_dot.pack(side="left")
        tk.Label(sf, textvariable=self.status_var, bg=BG, fg=MUTED,
                 font=FONT_MONO).pack(side="left", padx=6)

    def _build_controls(self, parent):
        def section(label):
            f = tk.Frame(parent, bg=PANEL)
            f.pack(fill="x", padx=16, pady=(14, 2))
            tk.Label(f, text=label.upper(), font=("Courier New", 9, "bold"),
                     bg=PANEL, fg=ACCENT2).pack(side="left")
            tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=16, pady=(0, 8))

        def row(parent, label, widget_fn):
            f = tk.Frame(parent, bg=PANEL)
            f.pack(fill="x", padx=16, pady=4)
            tk.Label(f, text=label, width=16, anchor="w",
                     font=FONT_LABEL, bg=PANEL, fg=TEXT).pack(side="left")
            widget_fn(f)

        def entry(parent, var, width=20):
            e = tk.Entry(parent, textvariable=var, bg=ENTRY_BG, fg=TEXT,
                         insertbackground=TEXT, relief="flat", font=FONT_MONO,
                         width=width, bd=0)
            e.pack(side="left", ipady=4, padx=2)

        def spin(parent, var, frm, to, inc=1):
            s = tk.Spinbox(parent, textvariable=var, from_=frm, to=to,
                           increment=inc, bg=ENTRY_BG, fg=TEXT, buttonbackground=BORDER,
                           relief="flat", font=FONT_MONO, width=8,
                           insertbackground=TEXT, bd=0)
            s.pack(side="left", ipady=4, padx=2)

        def slider_row(parent, label, var, frm, to, res=0.01):
            f = tk.Frame(parent, bg=PANEL)
            f.pack(fill="x", padx=16, pady=4)
            tk.Label(f, text=label, width=16, anchor="w",
                     font=FONT_LABEL, bg=PANEL, fg=TEXT).pack(side="left")
            val_lbl = tk.Label(f, text=f"{var.get():.2f}", width=5,
                               font=FONT_MONO, bg=PANEL, fg=ACCENT)
            val_lbl.pack(side="right")
            sl = tk.Scale(f, variable=var, from_=frm, to=to, resolution=res,
                          orient="horizontal", bg=PANEL, fg=TEXT,
                          troughcolor=BORDER, activebackground=ACCENT,
                          highlightthickness=0, bd=0, showvalue=False,
                          command=lambda v: val_lbl.config(text=f"{float(v):.2f}"))
            sl.pack(side="left", fill="x", expand=True, padx=6)

        def file_row(parent, label, var):
            f = tk.Frame(parent, bg=PANEL)
            f.pack(fill="x", padx=16, pady=4)
            tk.Label(f, text=label, width=16, anchor="w",
                     font=FONT_LABEL, bg=PANEL, fg=TEXT).pack(side="left")
            e = tk.Entry(f, textvariable=var, bg=ENTRY_BG, fg=TEXT,
                         insertbackground=TEXT, relief="flat", font=FONT_MONO,
                         width=22, bd=0)
            e.pack(side="left", ipady=4, padx=2)
            btn = tk.Button(f, text="…", bg=BORDER, fg=TEXT, relief="flat",
                            font=FONT_MONO, padx=6,
                            command=lambda v=var: self._browse(v))
            btn.pack(side="left", padx=2)

        # ── Appearance ──────────────────────────────────────────────────
        section("Appearance")
        row(parent, "Primary colour", lambda p: ColorEntry(p, self.v_primaryColor).pack(side="left"))
        row(parent, "Secondary col.", lambda p: ColorEntry(p, self.v_secondaryColor).pack(side="left"))
        row(parent, "Text colour",    lambda p: ColorEntry(p, self.v_textColor).pack(side="left"))
        row(parent, "No-data colour", lambda p: ColorEntry(p, self.v_noDataColor).pack(side="left"))
        row(parent, "Font size",      lambda p: spin(p, self.v_fontSize, 6, 60))

        # ── Gradient ────────────────────────────────────────────────────
        section("Gradient")
        f = tk.Frame(parent, bg=PANEL)
        f.pack(fill="x", padx=16, pady=4)
        tk.Label(f, text="Use gradient", width=16, anchor="w",
                 font=FONT_LABEL, bg=PANEL, fg=TEXT).pack(side="left")
        tk.Checkbutton(f, variable=self.v_useGradient, bg=PANEL,
                       fg=ACCENT, selectcolor=ENTRY_BG, activebackground=PANEL,
                       relief="flat").pack(side="left")
        slider_row(parent, "Gradient min", self.v_gradientMin, 0.0, 1.0)
        slider_row(parent, "Gradient max", self.v_gradientMax, 0.0, 1.0)

        # ── Map size ────────────────────────────────────────────────────
        section("Map size")
        row(parent, "Width (in)",  lambda p: spin(p, self.v_mapWith,  5, 100))
        row(parent, "Height (in)", lambda p: spin(p, self.v_mapDepht, 5, 100))

        # ── Output ──────────────────────────────────────────────────────
        section("Output")
        row(parent, "Map name", lambda p: entry(p, self.v_mapName, 18))

        # ── Data paths ──────────────────────────────────────────────────
        section("Data paths")
        file_row(parent, "Data CSV",     self.v_dataPath)
        file_row(parent, "Lat/Lon CSV",  self.v_latLongPath)
        file_row(parent, "Europe CSV",   self.v_europPath)

        # ── Generate button ─────────────────────────────────────────────
        tk.Frame(parent, bg=PANEL, height=16).pack()
        btn = tk.Button(parent, text="▶  GENERATE MAP",
                        font=("Georgia", 12, "bold"),
                        bg=ACCENT, fg="white", activebackground="#2563eb",
                        relief="flat", padx=24, pady=10, cursor="hand2",
                        command=self._generate)
        btn.pack(fill="x", padx=16, pady=(0, 8))

        reset_btn = tk.Button(parent, text="↺  Reset defaults",
                              font=FONT_MONO, bg=BORDER, fg=MUTED,
                              activebackground=ENTRY_BG, relief="flat",
                              padx=10, pady=6, cursor="hand2",
                              command=self._reset)
        reset_btn.pack(fill="x", padx=16, pady=(0, 20))

    # ── Helpers ───────────────────────────────────────────────────────────
    def _browse(self, var):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All", "*.*")])
        if path:
            var.set(path)

    def _reset(self):
        for key, val in DEFAULTS.items():
            var = getattr(self, f"v_{key}", None)
            if var:
                var.set(val)

    def _set_status(self, msg, color=MUTED):
        self.status_var.set(msg)
        self.status_dot.config(fg=color)

    def _generate(self):
        self._set_status("Generating…", ACCENT)
        self.update_idletasks()
        threading.Thread(target=self._run_generator, daemon=True).start()

    def _run_generator(self):
        config = {
            "primaryColor":   self.v_primaryColor.get(),
            "secondaryColor": self.v_secondaryColor.get(),
            "textColor":      self.v_textColor.get(),
            "noDataColor":    self.v_noDataColor.get(),
            "fontSize":       self.v_fontSize.get(),
            "useGradient":    self.v_useGradient.get(),
            "gradientMin":    self.v_gradientMin.get(),
            "gradientMax":    self.v_gradientMax.get(),
            "dataPath":       self.v_dataPath.get(),
            "latLongPath":    self.v_latLongPath.get(),
            "europPath":      self.v_europPath.get(),
            "mapName":        self.v_mapName.get(),
            "mapWith":        self.v_mapWith.get(),
            "mapDepht":       self.v_mapDepht.get(),
        }

        config_json = json.dumps(config)
        try:
            result = subprocess.run(
                [sys.executable, GENERATOR_SCRIPT, config_json],
                capture_output=True, text=True, timeout=300
            )
            if result.returncode != 0:
                self.after(0, self._set_status,
                           f"Error: {result.stderr.strip()[:120]}", ERROR)
                return

            out_path = f"{config['mapName']}.png"
            if not os.path.exists(out_path):
                self.after(0, self._set_status, "Error: output PNG not found.", ERROR)
                return

            img = Image.open(out_path)
            self._raw_image = img
            self.after(0, self._display_image, img)
            self.after(0, self._set_status,
                       f"Saved → {out_path}  ({img.width}×{img.height}px)", SUCCESS)

        except subprocess.TimeoutExpired:
            self.after(0, self._set_status, "Timed out after 5 minutes.", ERROR)
        except Exception as e:
            self.after(0, self._set_status, f"Exception: {e}", ERROR)

    def _display_image(self, img):
        self._fit_image()

    def _fit_image(self):
        if self._raw_image is None:
            return
        w = self.img_label.winfo_width()
        h = self.img_label.winfo_height()
        if w < 10 or h < 10:
            return
        img = self._raw_image.copy()
        img.thumbnail((w - 20, h - 20), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        self.img_label.config(image=photo, text="")
        self.img_label._photo = photo  # keep reference

    def _resize_preview(self, event=None):
        self.after(100, self._fit_image)


if __name__ == "__main__":
    app = MapGeneratorGUI()
    app.mainloop()