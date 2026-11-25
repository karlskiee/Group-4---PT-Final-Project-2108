import tkinter as tk
from tkinter import ttk, messagebox


# ==============================================================================
# 1. PAGE REPLACEMENT ENGINE
# ==============================================================================

def simulate_page_replacement(pages, num_frames, algo):
    """Unified simulation engine for FIFO, LRU, and Optimal algorithms."""
    frames = []
    steps = []
    fifo_idx = 0
    last_used = {}

    for i, page in enumerate(pages):
        replaced = "-"

        if page in frames:
            status = "HIT"
        else:
            status = "FAULT"
            if len(frames) < num_frames:
                frames.append(page)
            else:
                if algo == "FIFO":
                    victim_idx = fifo_idx
                    fifo_idx = (fifo_idx + 1) % num_frames
                elif algo == "LRU":
                    victim_page = min(frames, key=lambda p: last_used[p])
                    victim_idx = frames.index(victim_page)
                else:  # Optimal
                    future = pages[i + 1:]
                    victim_idx = max(
                        range(num_frames),
                        key=lambda idx: future.index(frames[idx]) if frames[idx] in future else float("inf")
                    )

                replaced = str(frames[victim_idx])
                frames[victim_idx] = page

        last_used[page] = i
        steps.append({
            "step": i + 1,
            "page": page,
            "frames": frames.copy(),
            "status": status,
            "replaced": replaced
        })

    return steps


# ==============================================================================
# 2. GRAPHICAL USER INTERFACE
# ==============================================================================

class PageReplacementApp:
    BG_MAIN = "#0F172A"
    BG_CARD = "#1E293B"
    BG_INPUT = "#334155"
    FG_TEXT = "#F8FAFC"
    FG_MUTED = "#94A3B8"
    ACCENT = "#38BDF8"
    HIT_COLOR = "#22C55E"
    FAULT_COLOR = "#EF4444"

    def __init__(self, root):
        self.root = root
        self.root.title("OS Page Replacement Simulator")
        self.root.geometry("1120x740")
        self.root.minsize(960, 650)
        self.root.configure(bg=self.BG_MAIN)

        self._configure_styles()
        self._build_header()
        self._build_input_and_metrics()
        self._build_visual_grid()
        self._build_step_table()

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background=self.BG_CARD,
            foreground=self.FG_TEXT,
            fieldbackground=self.BG_CARD,
            rowheight=26,
            borderwidth=0,
            font=("Segoe UI", 10)
        )
        style.configure(
            "Treeview.Heading",
            background=self.BG_INPUT,
            foreground=self.FG_TEXT,
            font=("Segoe UI", 10, "bold"),
            borderwidth=0
        )
        style.map("Treeview", background=[("selected", "#0284C7")])

    def _make_btn(self, parent, text, cmd, bg, fg=FG_TEXT, font_size=9, padx=12, pady=6):
        return tk.Button(
            parent, text=text, command=cmd, bg=bg, fg=fg,
            font=("Segoe UI", font_size, "bold"), relief="flat",
            padx=padx, pady=pady, cursor="hand2"
        )

    # ==========================================================================
    # HEADER & GUIDE WINDOW
    # ==========================================================================

    def _build_header(self):
        header = tk.Frame(self.root, bg=self.BG_CARD, padx=20, pady=14)
        header.pack(fill="x", padx=16, pady=(16, 10))

        title_box = tk.Frame(header, bg=self.BG_CARD)
        title_box.pack(side="left")

        tk.Label(
            title_box, text="OS Page Replacement Simulator",
            font=("Segoe UI", 16, "bold"), bg=self.BG_CARD, fg=self.ACCENT
        ).pack(anchor="w")

        tk.Label(
            title_box, text="Compare FIFO, Least Recently Used (LRU), and Optimal Page Replacement",
            font=("Segoe UI", 9), bg=self.BG_CARD, fg=self.FG_MUTED
        ).pack(anchor="w")

        controls = tk.Frame(header, bg=self.BG_CARD)
        controls.pack(side="right")

        buttons = [
            ("Load Sample", self.load_sample, self.BG_INPUT, self.FG_TEXT, 9, 12, (0, 8)),
            ("Clear", self.clear_all, self.FAULT_COLOR, self.FG_TEXT, 9, 12, (0, 8)),
            ("Run Simulation", self.run_simulation, self.HIT_COLOR, "#052E16", 10, 16, 0),
            ("Guide", self._show_guide, self.ACCENT, "#082F49", 10, 16, (8, 0)),
        ]
        for text, cmd, bg, fg, fsize, px, pad_x in buttons:
            self._make_btn(controls, text, cmd, bg, fg, fsize, px).pack(side="left", padx=pad_x)

    def _show_guide(self):
        guide = tk.Toplevel(self.root)
        guide.title("Page Replacement Simulator - Guide")
        guide.geometry("760x680")
        guide.minsize(650, 500)
        guide.configure(bg=self.BG_MAIN)
        guide.transient(self.root)

        # Fixed Header
        header = tk.Frame(guide, bg=self.BG_CARD, padx=18, pady=14)
        header.pack(fill="x", padx=16, pady=(16, 10))

        tk.Label(
            header, text="How to Use the Simulator",
            font=("Segoe UI", 16, "bold"), bg=self.BG_CARD, fg=self.ACCENT
        ).pack(anchor="w")
        tk.Label(
            header, text="A quick visual guide to the input boxes and simulation results.",
            font=("Segoe UI", 9), bg=self.BG_CARD, fg=self.FG_MUTED
        ).pack(anchor="w", pady=(3, 0))

        # Scrollable Area (Canvas + Vertical Scrollbar)
        scroll_container = tk.Frame(guide, bg=self.BG_MAIN)
        scroll_container.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        canvas = tk.Canvas(scroll_container, bg=self.BG_MAIN, highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        content = tk.Frame(canvas, bg=self.BG_MAIN)
        canvas_window = canvas.create_window((0, 0), window=content, anchor="nw")

        content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width - 8))

        def _on_mousewheel(event):
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
            else:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        guide.bind("<MouseWheel>", _on_mousewheel)
        guide.bind("<Button-4>", _on_mousewheel)
        guide.bind("<Button-5>", _on_mousewheel)

        def make_card(title, description, footnote=None):
            card = tk.Frame(content, bg=self.BG_CARD, padx=16, pady=12)
            card.pack(fill="x", pady=(0, 10))

            tk.Label(
                card, text=title, font=("Segoe UI", 11, "bold"),
                bg=self.BG_CARD, fg=self.FG_TEXT
            ).pack(anchor="w")
            tk.Label(
                card, text=description, font=("Segoe UI", 9),
                bg=self.BG_CARD, fg=self.FG_MUTED, justify="left", wraplength=660
            ).pack(anchor="w", pady=(4, 8))

            body = tk.Frame(card, bg=self.BG_CARD)
            body.pack(anchor="w", fill="x")

            if footnote:
                tk.Label(
                    card, text=footnote, font=("Segoe UI", 9),
                    bg=self.BG_CARD, fg=self.FG_TEXT, justify="left", wraplength=660
                ).pack(anchor="w", pady=(8, 0))
            return body

        # 1. Reference String
        body1 = make_card(
            "1. Page Reference String",
            "This box is the order in which the computer requests pages. "
            "The simulator reads the numbers from left to right, one at a time. "
            "Separate whole numbers with spaces or commas.",
            "Meaning: First request page 7, then page 0, then page 1, then page 2, and so on."
        )
        ex1 = tk.Frame(body1, bg=self.BG_INPUT, padx=10, pady=10)
        ex1.pack(fill="x")
        tk.Label(ex1, text="Example input:", font=("Segoe UI", 9, "bold"), bg=self.BG_INPUT, fg=self.FG_MUTED).pack(anchor="w")
        tk.Label(ex1, text="7   0   1   2   0   3", font=("Consolas", 15, "bold"), bg=self.BG_INPUT, fg=self.ACCENT).pack(anchor="w", pady=(3, 0))

        # 2. Frames
        body2 = make_card(
            "2. Frames",
            "Frames are the available spaces in physical memory where pages can be stored. "
            "The number you enter controls how many pages can stay in memory at the same time (1 to 10).",
            "With 3 frames, memory can hold up to 3 different pages. When full, the selected algorithm decides which page to replace."
        )
        ex2 = tk.Frame(body2, bg=self.BG_INPUT, padx=10, pady=10)
        ex2.pack(fill="x")
        tk.Label(ex2, text="Example: enter 3 frames", font=("Segoe UI", 9, "bold"), bg=self.BG_INPUT, fg=self.FG_MUTED).pack(anchor="w", pady=(0, 7))
        slots = tk.Frame(ex2, bg=self.BG_INPUT)
        slots.pack(anchor="w")

        for i in range(1, 4):
            slot = tk.Frame(slots, bg=self.BG_CARD, padx=18, pady=10, highlightbackground=self.ACCENT, highlightthickness=1)
            slot.pack(side="left", padx=(0, 8))
            tk.Label(slot, text=f"Frame {i}", font=("Segoe UI", 9, "bold"), bg=self.BG_CARD, fg=self.FG_MUTED).pack()
            tk.Label(slot, text="—", font=("Consolas", 16, "bold"), bg=self.BG_CARD, fg=self.FG_TEXT).pack(pady=(3, 0))

        # 3. Algorithm
        body3 = make_card(
            "3. Algorithm",
            "FIFO removes the oldest page; LRU removes the page unused for the longest time; "
            "Optimal removes the page whose next use is farthest in the future."
        )
        algo_row = tk.Frame(body3, bg=self.BG_INPUT, padx=10, pady=8)
        algo_row.pack(anchor="w")
        tk.Label(algo_row, text="Algorithm", font=("Segoe UI", 9), bg=self.BG_INPUT, fg=self.FG_MUTED).pack(side="left", padx=(0, 12))
        tk.Label(algo_row, text="FIFO  ▼", font=("Segoe UI", 10, "bold"), bg=self.BG_INPUT, fg=self.FG_TEXT).pack(side="left")

        # 4. Run Simulation
        body4 = make_card(
            "4. Run the Simulation",
            "Click Run Simulation to process the reference string. The visualization and execution log show every page request.",
            "HIT = requested page is already in a frame. FAULT = page is not in memory and must be loaded. A dash (—) indicates an empty frame."
        )
        for label, color, fg in (("HIT", self.HIT_COLOR, "#052E16"), ("FAULT", self.FAULT_COLOR, "#FFFFFF")):
            badge = tk.Frame(body4, bg=color, padx=12, pady=5)
            badge.pack(side="left", padx=(0, 8))
            tk.Label(badge, text=label, font=("Segoe UI", 9, "bold"), bg=color, fg=fg).pack()

        # Fixed Footer Button
        self._make_btn(guide, "Close Guide", guide.destroy, self.BG_INPUT, pady=7).pack(pady=(0, 14))

    # ==========================================================================
    # INPUT CONFIGURATION & METRIC CARDS
    # ==========================================================================

    def _build_input_and_metrics(self):
        top_section = tk.Frame(self.root, bg=self.BG_MAIN)
        top_section.pack(fill="x", padx=16, pady=6)

        input_card = tk.Frame(top_section, bg=self.BG_CARD, padx=16, pady=14)
        input_card.pack(fill="x", pady=(0, 10))

        # Reference String
        ref_box = tk.Frame(input_card, bg=self.BG_CARD)
        ref_box.pack(side="left", fill="x", expand=True, padx=(0, 14))
        tk.Label(
            ref_box, text="Page Reference String (space or comma separated whole numbers, e.g. 7 0 1 2 0 3)",
            font=("Segoe UI", 9), bg=self.BG_CARD, fg=self.FG_MUTED
        ).pack(anchor="w")
        self.ref_entry = tk.Entry(
            ref_box, font=("Segoe UI", 11), bg=self.BG_INPUT,
            fg=self.FG_TEXT, insertbackground=self.FG_TEXT, relief="flat"
        )
        self.ref_entry.pack(fill="x", ipady=5, pady=(3, 0))

        # Frames
        frame_box = tk.Frame(input_card, bg=self.BG_CARD)
        frame_box.pack(side="left", padx=(0, 14))
        tk.Label(frame_box, text="Frames (1 - 10)", font=("Segoe UI", 9), bg=self.BG_CARD, fg=self.FG_MUTED).pack(anchor="w")
        self.frames_entry = tk.Entry(
            frame_box, width=10, font=("Segoe UI", 11), bg=self.BG_INPUT,
            fg=self.FG_TEXT, insertbackground=self.FG_TEXT, relief="flat"
        )
        self.frames_entry.insert(0, "3")
        self.frames_entry.pack(ipady=5, pady=(3, 0))

        # Algorithm
        algo_box = tk.Frame(input_card, bg=self.BG_CARD)
        algo_box.pack(side="left")
        tk.Label(algo_box, text="Algorithm", font=("Segoe UI", 9), bg=self.BG_CARD, fg=self.FG_MUTED).pack(anchor="w")
        self.algo_var = tk.StringVar(value="FIFO")
        ttk.Combobox(
            algo_box, textvariable=self.algo_var, state="readonly",
            width=16, font=("Segoe UI", 10), values=["FIFO", "LRU", "Optimal"]
        ).pack(ipady=3, pady=(3, 0))

        # Metric Cards
        metrics_row = tk.Frame(top_section, bg=self.BG_MAIN)
        metrics_row.pack(fill="x")

        metrics_cfg = [
            ("lbl_total", "Total References", "0", self.ACCENT),
            ("lbl_faults", "Page Faults", "0", self.FAULT_COLOR),
            ("lbl_hits", "Page Hits", "0", self.HIT_COLOR),
            ("lbl_hit_ratio", "Hit Ratio", "0.00%", self.HIT_COLOR),
            ("lbl_fault_ratio", "Fault Ratio", "0.00%", self.FAULT_COLOR),
        ]
        for attr, title, initial, color in metrics_cfg:
            card = tk.Frame(metrics_row, bg=self.BG_CARD, padx=14, pady=10)
            card.pack(side="left", fill="x", expand=True, padx=(0, 8))
            tk.Label(card, text=title, font=("Segoe UI", 9), bg=self.BG_CARD, fg=self.FG_MUTED).pack(anchor="w")
            val_lbl = tk.Label(card, text=initial, font=("Segoe UI", 15, "bold"), bg=self.BG_CARD, fg=color)
            val_lbl.pack(anchor="w")
            setattr(self, attr, val_lbl)

    # ==========================================================================
    # MEMORY FRAME VISUALIZATION & STEP TABLE
    # ==========================================================================

    def _build_visual_grid(self):
        grid_card = tk.Frame(self.root, bg=self.BG_CARD, padx=16, pady=12)
        grid_card.pack(fill="x", padx=16, pady=6)

        tk.Label(
            grid_card, text="Memory Frame Visualization",
            font=("Segoe UI", 11, "bold"), bg=self.BG_CARD, fg=self.FG_TEXT
        ).pack(anchor="w", pady=(0, 6))

        canvas_wrap = tk.Frame(grid_card, bg=self.BG_CARD)
        canvas_wrap.pack(fill="x")

        self.grid_canvas = tk.Canvas(canvas_wrap, height=180, bg=self.BG_MAIN, highlightthickness=0)
        h_scroll = ttk.Scrollbar(canvas_wrap, orient="horizontal", command=self.grid_canvas.xview)
        v_scroll = ttk.Scrollbar(canvas_wrap, orient="vertical", command=self.grid_canvas.yview)
        self.grid_canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)

        self.grid_canvas.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        canvas_wrap.columnconfigure(0, weight=1)

    def _build_step_table(self):
        table_card = tk.Frame(self.root, bg=self.BG_CARD, padx=16, pady=12)
        table_card.pack(fill="both", expand=True, padx=16, pady=(6, 16))

        tk.Label(
            table_card, text="Step-by-Step Execution Log",
            font=("Segoe UI", 11, "bold"), bg=self.BG_CARD, fg=self.FG_TEXT
        ).pack(anchor="w", pady=(0, 6))

        headers = {
            "step": "Step",
            "page": "Page Requested",
            "frames": "Frames in Memory",
            "status": "Status",
            "replaced": "Replaced Page"
        }
        self.tree = ttk.Treeview(table_card, columns=list(headers.keys()), show="headings", height=7)

        for col, text in headers.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, anchor="center", width=240 if col == "frames" else 110)

        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # ==========================================================================
    # ACTIONS & VALIDATION
    # ==========================================================================

    def _validate_inputs(self):
        raw_ref = self.ref_entry.get().strip()
        if not raw_ref:
            messagebox.showerror("Invalid Input", "Please enter a page reference string.")
            return None, None

        tokens = raw_ref.replace(",", " ").split()
        if not all(t.isdigit() for t in tokens):
            messagebox.showerror(
                "Invalid Input",
                "Reference string must contain only whole numbers (0 or greater, no negatives or decimals)."
            )
            return None, None

        raw_frames = self.frames_entry.get().strip()
        if not raw_frames.isdigit() or not (1 <= int(raw_frames) <= 10):
            messagebox.showerror("Invalid Input", "Number of frames must be a whole number between 1 and 10.")
            return None, None

        return [int(t) for t in tokens], int(raw_frames)

    def load_sample(self):
        self.ref_entry.delete(0, "end")
        self.ref_entry.insert(0, "7 0 1 2 0 3 0 4 2 3 0 3 2")
        self.frames_entry.delete(0, "end")
        self.frames_entry.insert(0, "3")

    def clear_all(self):
        self.ref_entry.delete(0, "end")
        self.frames_entry.delete(0, "end")
        self.frames_entry.insert(0, "3")
        self.grid_canvas.delete("all")
        self.tree.delete(*self.tree.get_children())

        for lbl, val in (
            (self.lbl_total, "0"), (self.lbl_faults, "0"), (self.lbl_hits, "0"),
            (self.lbl_hit_ratio, "0.00%"), (self.lbl_fault_ratio, "0.00%")
        ):
            lbl.config(text=val)

    def run_simulation(self):
        pages, num_frames = self._validate_inputs()
        if pages is None:
            return

        steps = simulate_page_replacement(pages, num_frames, self.algo_var.get())
        self._update_metrics(steps)
        self._draw_visual_grid(steps, num_frames)
        self._populate_table(steps, num_frames)

    def _update_metrics(self, steps):
        total = len(steps)
        faults = sum(1 for s in steps if s["status"] == "FAULT")
        hits = total - faults

        self.lbl_total.config(text=str(total))
        self.lbl_faults.config(text=str(faults))
        self.lbl_hits.config(text=str(hits))
        self.lbl_hit_ratio.config(text=f"{(hits / total) * 100:.2f}%")
        self.lbl_fault_ratio.config(text=f"{(faults / total) * 100:.2f}%")

    # ==========================================================================
    # RENDERING VISUAL GRID & TABLE
    # ==========================================================================

    def _draw_visual_grid(self, steps, num_frames):
        self.grid_canvas.delete("all")
        cell_w, cell_h, left_m, top_m = 56, 30, 95, 14

        # Row Labels
        row_labels = [("Page", self.ACCENT, "bold")] + [
            (f"Frame {f + 1}", self.FG_MUTED, "normal") for f in range(num_frames)
        ] + [("Result", self.FG_MUTED, "bold")]

        for idx, (text, color, weight) in enumerate(row_labels):
            self.grid_canvas.create_text(
                left_m - 12, top_m + idx * cell_h + cell_h / 2,
                text=text, anchor="e", fill=color, font=("Segoe UI", 9, weight)
            )

        # Columns
        for col_idx, step in enumerate(steps):
            x1 = left_m + col_idx * cell_w
            x2 = x1 + cell_w - 4
            cx = (x1 + x2) / 2

            # Requested Page Header
            self.grid_canvas.create_rectangle(x1, top_m, x2, top_m + cell_h - 2, fill=self.BG_INPUT, outline="")
            self.grid_canvas.create_text(cx, top_m + cell_h / 2, text=str(step["page"]), fill=self.FG_TEXT, font=("Segoe UI", 10, "bold"))

            # Frame Cells
            for f in range(num_frames):
                y1 = top_m + (f + 1) * cell_h
                y2 = y1 + cell_h - 2
                val = str(step["frames"][f]) if f < len(step["frames"]) else "-"
                fill = "#1E3A5F" if val == str(step["page"]) else self.BG_CARD

                self.grid_canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="#334155")
                self.grid_canvas.create_text(cx, (y1 + y2) / 2, text=val, fill=self.FG_TEXT, font=("Segoe UI", 10))

            # HIT / FAULT Badge
            sy1 = top_m + (num_frames + 1) * cell_h + 2
            sy2 = sy1 + cell_h - 4
            is_hit = step["status"] == "HIT"

            self.grid_canvas.create_rectangle(
                x1, sy1, x2, sy2,
                fill=self.HIT_COLOR if is_hit else self.FAULT_COLOR, outline=""
            )
            self.grid_canvas.create_text(
                cx, (sy1 + sy2) / 2,
                text=step["status"], fill="#052E16" if is_hit else "#FFFFFF",
                font=("Segoe UI", 8, "bold")
            )

        self.grid_canvas.configure(scrollregion=(
            0, 0, left_m + len(steps) * cell_w + 20, top_m + (num_frames + 2) * cell_h + 16
        ))

    def _populate_table(self, steps, num_frames):
        self.tree.delete(*self.tree.get_children())
        for s in steps:
            padded = [str(x) for x in s["frames"]] + ["-"] * (num_frames - len(s["frames"]))
            self.tree.insert("", "end", values=(
                s["step"], s["page"], " | ".join(padded), s["status"], s["replaced"]
            ))


if __name__ == "__main__":
    root = tk.Tk()
    PageReplacementApp(root)
    root.mainloop()
