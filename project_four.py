import tkinter as tk
from tkinter import ttk, messagebox


# ==============================================================================
# 1. PAGE REPLACEMENT ALGORITHMS (Pure Logic - Easy to Explain)
# ==============================================================================

def simulate_fifo(pages, num_frames):
    """First-In, First-Out (FIFO): Replaces the oldest page in memory."""
    frames = []
    replace_index = 0
    steps = []

    for i, page in enumerate(pages):
        replaced = "-"
        if page in frames:
            status = "HIT"
        else:
            status = "FAULT"
            if len(frames) < num_frames:
                frames.append(page)
            else:
                replaced = str(frames[replace_index])
                frames[replace_index] = page
                replace_index = (replace_index + 1) % num_frames

        steps.append({
            "step": i + 1,
            "page": page,
            "frames": frames.copy(),
            "status": status,
            "replaced": replaced
        })

    return steps


def simulate_lru(pages, num_frames):
    """Least Recently Used (LRU): Replaces the page unused for the longest time."""
    frames = []
    last_used = {}  # Tracks the most recent step index each page was accessed
    steps = []

    for i, page in enumerate(pages):
        replaced = "-"
        if page in frames:
            status = "HIT"
        else:
            status = "FAULT"
            if len(frames) < num_frames:
                frames.append(page)
            else:
                # Find the page in frames with the smallest last_used index
                lru_page = min(frames, key=lambda p: last_used[p])
                victim_idx = frames.index(lru_page)
                replaced = str(lru_page)
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


def simulate_optimal(pages, num_frames):
    """Optimal (OPT): Replaces the page that will not be used for the longest time."""
    frames = []
    steps = []

    for i, page in enumerate(pages):
        replaced = "-"
        if page in frames:
            status = "HIT"
        else:
            status = "FAULT"
            if len(frames) < num_frames:
                frames.append(page)
            else:
                # Look ahead in the remaining reference string
                future = pages[i + 1:]
                farthest_use = -1
                victim_idx = 0

                for idx, f_page in enumerate(frames):
                    if f_page not in future:
                        # Never used again -> best page to replace immediately
                        victim_idx = idx
                        break
                    next_use = future.index(f_page)
                    if next_use > farthest_use:
                        farthest_use = next_use
                        victim_idx = idx

                replaced = str(frames[victim_idx])
                frames[victim_idx] = page

        steps.append({
            "step": i + 1,
            "page": page,
            "frames": frames.copy(),
            "status": status,
            "replaced": replaced
        })

    return steps


# ==============================================================================
# 2. GRAPHICAL USER INTERFACE (Tkinter Dark Dashboard)
# ==============================================================================

class PageReplacementApp:
    # Color Palette
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

    # --- Top Header Bar ---
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

        tk.Button(
            controls, text="Load Sample", command=self.load_sample,
            bg=self.BG_INPUT, fg=self.FG_TEXT, font=("Segoe UI", 9, "bold"),
            relief="flat", padx=12, pady=6, cursor="hand2"
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            controls, text="Clear", command=self.clear_all,
            bg=self.FAULT_COLOR, fg=self.FG_TEXT, font=("Segoe UI", 9, "bold"),
            relief="flat", padx=12, pady=6, cursor="hand2"
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            controls, text="Run Simulation", command=self.run_simulation,
            bg=self.HIT_COLOR, fg="#052E16", font=("Segoe UI", 10, "bold"),
            relief="flat", padx=16, pady=6, cursor="hand2"
        ).pack(side="left")

    # --- Input Configuration & Metric Cards ---
    def _build_input_and_metrics(self):
        top_section = tk.Frame(self.root, bg=self.BG_MAIN)
        top_section.pack(fill="x", padx=16, pady=6)

        # Input Card
        input_card = tk.Frame(top_section, bg=self.BG_CARD, padx=16, pady=14)
        input_card.pack(fill="x", pady=(0, 10))

        # Reference String Input
        ref_box = tk.Frame(input_card, bg=self.BG_CARD)
        ref_box.pack(side="left", fill="x", expand=True, padx=(0, 14))
        tk.Label(
            ref_box, text="Page Reference String (space or comma separated whole numbers, e.g. 7 0 1 2 0 3)",
            font=("Segoe UI", 9), bg=self.BG_CARD, fg=self.FG_MUTED
        ).pack(anchor="w")
        self.ref_entry = tk.Entry(
            ref_box, font=("Segoe UI", 11), bg=self.BG_INPUT, fg=self.FG_TEXT,
            insertbackground=self.FG_TEXT, relief="flat"
        )
        self.ref_entry.pack(fill="x", ipady=5, pady=(3, 0))

        # Frames Input
        frame_box = tk.Frame(input_card, bg=self.BG_CARD)
        frame_box.pack(side="left", padx=(0, 14))
        tk.Label(
            frame_box, text="Frames (1 - 10)",
            font=("Segoe UI", 9), bg=self.BG_CARD, fg=self.FG_MUTED
        ).pack(anchor="w")
        self.frames_entry = tk.Entry(
            frame_box, width=10, font=("Segoe UI", 11), bg=self.BG_INPUT,
            fg=self.FG_TEXT, insertbackground=self.FG_TEXT, relief="flat"
        )
        self.frames_entry.insert(0, "3")
        self.frames_entry.pack(ipady=5, pady=(3, 0))

        # Algorithm Dropdown
        algo_box = tk.Frame(input_card, bg=self.BG_CARD)
        algo_box.pack(side="left")
        tk.Label(
            algo_box, text="Algorithm",
            font=("Segoe UI", 9), bg=self.BG_CARD, fg=self.FG_MUTED
        ).pack(anchor="w")
        self.algo_var = tk.StringVar(value="FIFO")
        self.algo_menu = ttk.Combobox(
            algo_box, textvariable=self.algo_var, state="readonly", width=16,
            font=("Segoe UI", 10), values=["FIFO", "LRU", "Optimal"]
        )
        self.algo_menu.pack(ipady=3, pady=(3, 0))

        # Summary Metric Cards
        metrics_row = tk.Frame(top_section, bg=self.BG_MAIN)
        metrics_row.pack(fill="x")

        self.lbl_total = self._create_metric_card(metrics_row, "Total References", "0", self.ACCENT)
        self.lbl_faults = self._create_metric_card(metrics_row, "Page Faults", "0", self.FAULT_COLOR)
        self.lbl_hits = self._create_metric_card(metrics_row, "Page Hits", "0", self.HIT_COLOR)
        self.lbl_hit_ratio = self._create_metric_card(metrics_row, "Hit Ratio", "0.00%", self.HIT_COLOR)
        self.lbl_fault_ratio = self._create_metric_card(metrics_row, "Fault Ratio", "0.00%", self.FAULT_COLOR)

    def _create_metric_card(self, parent, title, initial, color):
        card = tk.Frame(parent, bg=self.BG_CARD, padx=14, pady=10)
        card.pack(side="left", fill="x", expand=True, padx=(0, 8))

        tk.Label(
            card, text=title, font=("Segoe UI", 9),
            bg=self.BG_CARD, fg=self.FG_MUTED
        ).pack(anchor="w")
        val = tk.Label(
            card, text=initial, font=("Segoe UI", 15, "bold"),
            bg=self.BG_CARD, fg=color
        )
        val.pack(anchor="w")
        return val

    # --- Visual Frame Memory Grid (Canvas) ---
    def _build_visual_grid(self):
        grid_card = tk.Frame(self.root, bg=self.BG_CARD, padx=16, pady=12)
        grid_card.pack(fill="x", padx=16, pady=6)

        tk.Label(
            grid_card, text="Memory Frame Visualization",
            font=("Segoe UI", 11, "bold"), bg=self.BG_CARD, fg=self.FG_TEXT
        ).pack(anchor="w", pady=(0, 6))

        canvas_wrap = tk.Frame(grid_card, bg=self.BG_CARD)
        canvas_wrap.pack(fill="x")

        self.grid_canvas = tk.Canvas(
            canvas_wrap, height=180, bg=self.BG_MAIN, highlightthickness=0
        )
        h_scroll = ttk.Scrollbar(canvas_wrap, orient="horizontal", command=self.grid_canvas.xview)
        v_scroll = ttk.Scrollbar(canvas_wrap, orient="vertical", command=self.grid_canvas.yview)
        self.grid_canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)

        self.grid_canvas.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        canvas_wrap.columnconfigure(0, weight=1)

    # --- Step-by-Step Execution Log Table ---
    def _build_step_table(self):
        table_card = tk.Frame(self.root, bg=self.BG_CARD, padx=16, pady=12)
        table_card.pack(fill="both", expand=True, padx=16, pady=(6, 16))

        tk.Label(
            table_card, text="Step-by-Step Execution Log",
            font=("Segoe UI", 11, "bold"), bg=self.BG_CARD, fg=self.FG_TEXT
        ).pack(anchor="w", pady=(0, 6))

        cols = ("step", "page", "frames", "status", "replaced")
        headers = {
            "step": "Step", "page": "Page Requested", "frames": "Frames in Memory",
            "status": "Status", "replaced": "Replaced Page"
        }

        self.tree = ttk.Treeview(table_card, columns=cols, show="headings", height=7)
        for col in cols:
            self.tree.heading(col, text=headers[col])
            width = 240 if col == "frames" else 110
            self.tree.column(col, anchor="center", width=width)

        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # ==========================================================================
    # 3. STRICT INPUT VALIDATION & SIMULATION ACTIONS
    # ==========================================================================

    def _validate_inputs(self):
        """
        Strictly validates reference string and frame count.
        Rejects empty values, negative numbers, decimals, and letters.
        """
        raw_ref = self.ref_entry.get().strip()
        if not raw_ref:
            messagebox.showerror("Invalid Input", "Please enter a page reference string.")
            return None, None

        # Allow space or comma separation
        tokens = raw_ref.replace(",", " ").split()
        pages = []
        for token in tokens:
            if not token.isdigit():
                messagebox.showerror(
                    "Invalid Input",
                    f"'{token}' is not valid. Reference string must contain only whole numbers (0 or greater, no negatives or decimals)."
                )
                return None, None
            pages.append(int(token))

        raw_frames = self.frames_entry.get().strip()
        if not raw_frames.isdigit():
            messagebox.showerror(
                "Invalid Input",
                "Number of frames must be a whole number (no negatives, decimals, or letters)."
            )
            return None, None

        num_frames = int(raw_frames)
        if num_frames < 1 or num_frames > 10:
            messagebox.showerror("Invalid Input", "Number of frames must be between 1 and 10.")
            return None, None

        return pages, num_frames

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
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.lbl_total.config(text="0")
        self.lbl_faults.config(text="0")
        self.lbl_hits.config(text="0")
        self.lbl_hit_ratio.config(text="0.00%")
        self.lbl_fault_ratio.config(text="0.00%")

    def run_simulation(self):
        pages, num_frames = self._validate_inputs()
        if pages is None:
            return

        algo = self.algo_var.get()
        if algo == "FIFO":
            steps = simulate_fifo(pages, num_frames)
        elif algo == "LRU":
            steps = simulate_lru(pages, num_frames)
        else:
            steps = simulate_optimal(pages, num_frames)

        self._update_metrics(steps)
        self._draw_visual_grid(steps, num_frames)
        self._populate_table(steps, num_frames)

    def _update_metrics(self, steps):
        total = len(steps)
        faults = sum(1 for s in steps if s["status"] == "FAULT")
        hits = total - faults
        hit_ratio = (hits / total) * 100
        fault_ratio = (faults / total) * 100

        self.lbl_total.config(text=str(total))
        self.lbl_faults.config(text=str(faults))
        self.lbl_hits.config(text=str(hits))
        self.lbl_hit_ratio.config(text=f"{hit_ratio:.2f}%")
        self.lbl_fault_ratio.config(text=f"{fault_ratio:.2f}%")

    def _draw_visual_grid(self, steps, num_frames):
        self.grid_canvas.delete("all")
        cell_w = 56
        cell_h = 30
        left_margin = 95
        top_margin = 14

        # Row Labels
        self.grid_canvas.create_text(
            left_margin - 12, top_margin + cell_h / 2,
            text="Page", anchor="e", fill=self.ACCENT, font=("Segoe UI", 9, "bold")
        )
        for f in range(num_frames):
            y = top_margin + (f + 1) * cell_h + cell_h / 2
            self.grid_canvas.create_text(
                left_margin - 12, y,
                text=f"Frame {f + 1}", anchor="e", fill=self.FG_MUTED, font=("Segoe UI", 9)
            )
        status_y = top_margin + (num_frames + 1) * cell_h + cell_h / 2
        self.grid_canvas.create_text(
            left_margin - 12, status_y,
            text="Result", anchor="e", fill=self.FG_MUTED, font=("Segoe UI", 9, "bold")
        )

        # Draw Columns (one per reference)
        for col_idx, step in enumerate(steps):
            x1 = left_margin + col_idx * cell_w
            x2 = x1 + cell_w - 4

            # Header: Requested Page
            self.grid_canvas.create_rectangle(
                x1, top_margin, x2, top_margin + cell_h - 2,
                fill=self.BG_INPUT, outline=""
            )
            self.grid_canvas.create_text(
                (x1 + x2) / 2, top_margin + cell_h / 2,
                text=str(step["page"]), fill=self.FG_TEXT, font=("Segoe UI", 10, "bold")
            )

            # Frame Cells
            for f in range(num_frames):
                y1 = top_margin + (f + 1) * cell_h
                y2 = y1 + cell_h - 2
                val = str(step["frames"][f]) if f < len(step["frames"]) else "-"
                highlight = (val == str(step["page"]))
                box_fill = "#1E3A5F" if highlight else self.BG_CARD

                self.grid_canvas.create_rectangle(
                    x1, y1, x2, y2, fill=box_fill, outline="#334155"
                )
                self.grid_canvas.create_text(
                    (x1 + x2) / 2, (y1 + y2) / 2,
                    text=val, fill=self.FG_TEXT, font=("Segoe UI", 10)
                )

            # Status Badge (HIT / FAULT)
            sy1 = top_margin + (num_frames + 1) * cell_h + 2
            sy2 = sy1 + cell_h - 4
            is_hit = step["status"] == "HIT"
            badge_bg = self.HIT_COLOR if is_hit else self.FAULT_COLOR
            badge_fg = "#052E16" if is_hit else "#FFFFFF"

            self.grid_canvas.create_rectangle(x1, sy1, x2, sy2, fill=badge_bg, outline="")
            self.grid_canvas.create_text(
                (x1 + x2) / 2, (sy1 + sy2) / 2,
                text="HIT" if is_hit else "FAULT", fill=badge_fg, font=("Segoe UI", 8, "bold")
            )

        total_w = left_margin + len(steps) * cell_w + 20
        total_h = top_margin + (num_frames + 2) * cell_h + 16
        self.grid_canvas.configure(scrollregion=(0, 0, total_w, total_h))

    def _populate_table(self, steps, num_frames):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for s in steps:
            padded = [str(x) for x in s["frames"]] + ["-"] * (num_frames - len(s["frames"]))
            frames_str = " | ".join(padded)
            self.tree.insert("", "end", values=(
                s["step"], s["page"], frames_str, s["status"], s["replaced"]
            ))

if __name__ == "__main__":
    root = tk.Tk()
    app = PageReplacementApp(root)
    root.mainloop()
