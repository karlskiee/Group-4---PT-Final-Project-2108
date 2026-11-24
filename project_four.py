import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque


# ==============================================================================
# 1. SCHEDULING ALGORITHMS (Pure Logic - Separated from UI for Easy Explanation)
# ==============================================================================

def simulate_fcfs(processes):
    """First-Come, First-Served (Non-preemptive)."""
    # Sort by Arrival Time, then by original order
    ordered = sorted(processes, key=lambda p: (p["at"], p["order"]))
    current_time = 0
    gantt = []
    results = []

    for p in ordered:
        if current_time < p["at"]:
            gantt.append(("IDLE", current_time, p["at"]))
            current_time = p["at"]

        start = current_time
        end = start + p["bt"]
        gantt.append((p["pid"], start, end))

        ct = end
        tat = ct - p["at"]
        wt = tat - p["bt"]
        results.append({
            "pid": p["pid"], "at": p["at"], "bt": p["bt"],
            "ct": ct, "tat": tat, "wt": wt
        })
        current_time = end

    return results, gantt


def simulate_sjf(processes):
    """Shortest Job First (Non-preemptive)."""
    remaining = [p.copy() for p in processes]
    current_time = 0
    gantt = []
    results = []

    while remaining:
        # Filter processes that have already arrived
        available = [p for p in remaining if p["at"] <= current_time]

        if not available:
            # Jump to the next arriving process if CPU is idle
            next_arrival = min(p["at"] for p in remaining)
            gantt.append(("IDLE", current_time, next_arrival))
            current_time = next_arrival
            continue

        # Pick the shortest burst time (tie-breaker: arrival time, then order)
        chosen = min(available, key=lambda p: (p["bt"], p["at"], p["order"]))
        remaining.remove(chosen)

        start = current_time
        end = start + chosen["bt"]
        gantt.append((chosen["pid"], start, end))

        ct = end
        tat = ct - chosen["at"]
        wt = tat - chosen["bt"]
        results.append({
            "pid": chosen["pid"], "at": chosen["at"], "bt": chosen["bt"],
            "ct": ct, "tat": tat, "wt": wt
        })
        current_time = end

    return results, gantt


def simulate_rr(processes, quantum):
    """Round Robin (Preemptive with Time Quantum)."""
    ordered = sorted(processes, key=lambda p: (p["at"], p["order"]))
    remaining_bt = {p["pid"]: p["bt"] for p in ordered}
    ready_queue = deque()
    gantt = []
    results = []

    current_time = 0
    idx = 0
    total = len(ordered)

    while idx < total or ready_queue:
        # If no process is ready, advance time to the next arrival
        if not ready_queue:
            if current_time < ordered[idx]["at"]:
                gantt.append(("IDLE", current_time, ordered[idx]["at"]))
                current_time = ordered[idx]["at"]
            while idx < total and ordered[idx]["at"] <= current_time:
                ready_queue.append(ordered[idx])
                idx += 1

        current_proc = ready_queue.popleft()
        pid = current_proc["pid"]

        run_time = min(quantum, remaining_bt[pid])
        start = current_time
        end = start + run_time
        gantt.append((pid, start, end))

        current_time = end
        remaining_bt[pid] -= run_time

        # Add newly arrived processes BEFORE re-queueing the current process
        while idx < total and ordered[idx]["at"] <= current_time:
            ready_queue.append(ordered[idx])
            idx += 1

        if remaining_bt[pid] > 0:
            ready_queue.append(current_proc)
        else:
            ct = current_time
            tat = ct - current_proc["at"]
            wt = tat - current_proc["bt"]
            results.append({
                "pid": pid, "at": current_proc["at"], "bt": current_proc["bt"],
                "ct": ct, "tat": tat, "wt": wt
            })

    # Sort results by PID order for clean table display
    results.sort(key=lambda r: next(p["order"] for p in processes if p["pid"] == r["pid"]))
    return results, gantt


# ==============================================================================
# 2. GRAPHICAL USER INTERFACE (Tkinter Dark Dashboard)
# ==============================================================================

class SchedulerApp:
    # Color Palette
    BG_MAIN = "#0F172A"      # Dark Slate
    BG_CARD = "#1E293B"      # Card Surface
    BG_INPUT = "#334155"     # Input Fields
    FG_TEXT = "#F8FAFC"      # Primary Text
    FG_MUTED = "#94A3B8"     # Secondary Text
    ACCENT = "#38BDF8"       # Sky Blue
    SUCCESS = "#22C55E"      # Green
    DANGER = "#EF4444"       # Red

    GANTT_COLORS = [
        "#38BDF8", "#818CF8", "#34D399", "#FBBF24",
        "#F472B6", "#A78BFA", "#FB923C", "#2DD4BF"
    ]

    def __init__(self, root):
        self.root = root
        self.root.title("OS Process Scheduling Lab")
        self.root.geometry("1120x720")
        self.root.minsize(980, 650)
        self.root.configure(bg=self.BG_MAIN)

        self.processes = []
        self.process_counter = 1

        self._configure_styles()
        self._build_header()
        self._build_main_workspace()
        self._build_gantt_section()

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background=self.BG_CARD,
            foreground=self.FG_TEXT,
            fieldbackground=self.BG_CARD,
            rowheight=28,
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

    # --- Top Navigation / Control Bar ---
    def _build_header(self):
        header = tk.Frame(self.root, bg=self.BG_CARD, padx=20, pady=14)
        header.pack(fill="x", padx=16, pady=(16, 10))

        title_frame = tk.Frame(header, bg=self.BG_CARD)
        title_frame.pack(side="left")
        tk.Label(
            title_frame, text="OS Process Scheduling Lab",
            font=("Segoe UI", 16, "bold"), bg=self.BG_CARD, fg=self.ACCENT
        ).pack(anchor="w")
        tk.Label(
            title_frame, text="Simulate FCFS, Non-Preemptive SJF, and Round Robin",
            font=("Segoe UI", 9), bg=self.BG_CARD, fg=self.FG_MUTED
        ).pack(anchor="w")

        controls = tk.Frame(header, bg=self.BG_CARD)
        controls.pack(side="right")

        tk.Label(
            controls, text="Algorithm:", font=("Segoe UI", 10, "bold"),
            bg=self.BG_CARD, fg=self.FG_TEXT
        ).pack(side="left", padx=(0, 6))

        self.algo_var = tk.StringVar(value="FCFS")
        self.algo_menu = ttk.Combobox(
            controls, textvariable=self.algo_var, state="readonly", width=18,
            values=["FCFS", "SJF (Non-Preemptive)", "Round Robin"]
        )
        self.algo_menu.pack(side="left", padx=(0, 14))
        self.algo_menu.bind("<<ComboboxSelected>>", self._toggle_quantum)

        tk.Label(
            controls, text="Quantum:", font=("Segoe UI", 10, "bold"),
            bg=self.BG_CARD, fg=self.FG_TEXT
        ).pack(side="left", padx=(0, 6))

        self.quantum_entry = tk.Entry(
            controls, width=6, font=("Segoe UI", 10),
            bg=self.BG_INPUT, fg=self.FG_TEXT, insertbackground=self.FG_TEXT,
            relief="flat", disabledbackground="#1E293B", disabledforeground="#475569"
        )
        self.quantum_entry.insert(0, "2")
        self.quantum_entry.config(state="disabled")
        self.quantum_entry.pack(side="left", padx=(0, 16), ipady=4)

        tk.Button(
            controls, text="Load Sample", command=self.load_sample_data,
            bg=self.BG_INPUT, fg=self.FG_TEXT, font=("Segoe UI", 9, "bold"),
            relief="flat", padx=12, pady=6, cursor="hand2"
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            controls, text="Run Simulation", command=self.run_simulation,
            bg=self.SUCCESS, fg="#052E16", font=("Segoe UI", 10, "bold"),
            relief="flat", padx=16, pady=6, cursor="hand2"
        ).pack(side="left")

    # --- Middle Split Workspace ---
    def _build_main_workspace(self):
        workspace = tk.Frame(self.root, bg=self.BG_MAIN)
        workspace.pack(fill="both", expand=True, padx=16, pady=6)
        workspace.columnconfigure(0, weight=4)
        workspace.columnconfigure(1, weight=6)
        workspace.rowconfigure(0, weight=1)

        # LEFT CARD: Process Input & Queue
        left_card = tk.Frame(workspace, bg=self.BG_CARD, padx=16, pady=14)
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        tk.Label(
            left_card, text="1. Process Queue", font=("Segoe UI", 12, "bold"),
            bg=self.BG_CARD, fg=self.FG_TEXT
        ).pack(anchor="w", pady=(0, 10))

        form = tk.Frame(left_card, bg=self.BG_CARD)
        form.pack(fill="x", pady=(0, 10))

        # Input fields
        self.pid_entry = self._create_labeled_input(form, "Process ID", 0, "P1")
        self.at_entry = self._create_labeled_input(form, "Arrival (≥ 0)", 1, "0")
        self.bt_entry = self._create_labeled_input(form, "Burst (≥ 1)", 2, "4")

        btn_row = tk.Frame(left_card, bg=self.BG_CARD)
        btn_row.pack(fill="x", pady=(0, 12))

        tk.Button(
            btn_row, text="+ Add Process", command=self.add_process,
            bg=self.ACCENT, fg="#082F49", font=("Segoe UI", 9, "bold"),
            relief="flat", padx=12, pady=6, cursor="hand2"
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            btn_row, text="Remove Selected", command=self.remove_selected,
            bg=self.BG_INPUT, fg=self.FG_TEXT, font=("Segoe UI", 9),
            relief="flat", padx=10, pady=6, cursor="hand2"
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            btn_row, text="Clear All", command=self.clear_all,
            bg=self.DANGER, fg=self.FG_TEXT, font=("Segoe UI", 9, "bold"),
            relief="flat", padx=10, pady=6, cursor="hand2"
        ).pack(side="right")

        # Input Queue Table
        self.queue_tree = ttk.Treeview(
            left_card, columns=("pid", "at", "bt"), show="headings", height=8
        )
        for col, text in [("pid", "Process ID"), ("at", "Arrival Time"), ("bt", "Burst Time")]:
            self.queue_tree.heading(col, text=text)
            self.queue_tree.column(col, anchor="center", width=100)
        self.queue_tree.pack(fill="both", expand=True)

        # RIGHT CARD: Simulation Results & Metrics
        right_card = tk.Frame(workspace, bg=self.BG_CARD, padx=16, pady=14)
        right_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        tk.Label(
            right_card, text="2. Simulation Metrics & Results",
            font=("Segoe UI", 12, "bold"), bg=self.BG_CARD, fg=self.FG_TEXT
        ).pack(anchor="w", pady=(0, 10))

        # Metric Summary Cards
        metrics_row = tk.Frame(right_card, bg=self.BG_CARD)
        metrics_row.pack(fill="x", pady=(0, 12))

        self.avg_wt_label = self._create_metric_box(metrics_row, "Average Waiting Time", "0.00")
        self.avg_tat_label = self._create_metric_box(metrics_row, "Average Turnaround Time", "0.00")

        # Results Table
        cols = ("pid", "at", "bt", "ct", "tat", "wt")
        headers = {
            "pid": "PID", "at": "Arrival", "bt": "Burst",
            "ct": "Completion", "tat": "Turnaround", "wt": "Waiting"
        }
        self.result_tree = ttk.Treeview(right_card, columns=cols, show="headings", height=8)
        for col in cols:
            self.result_tree.heading(col, text=headers[col])
            self.result_tree.column(col, anchor="center", width=85)
        self.result_tree.pack(fill="both", expand=True)

    # --- Bottom Section: Gantt Chart ---
    def _build_gantt_section(self):
        gantt_card = tk.Frame(self.root, bg=self.BG_CARD, padx=16, pady=12)
        gantt_card.pack(fill="x", padx=16, pady=(6, 16))

        tk.Label(
            gantt_card, text="3. Gantt Chart Timeline",
            font=("Segoe UI", 12, "bold"), bg=self.BG_CARD, fg=self.FG_TEXT
        ).pack(anchor="w", pady=(0, 8))

        canvas_frame = tk.Frame(gantt_card, bg=self.BG_CARD)
        canvas_frame.pack(fill="x")

        self.gantt_canvas = tk.Canvas(
            canvas_frame, height=110, bg=self.BG_MAIN, highlightthickness=0
        )
        h_scroll = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.gantt_canvas.xview)
        self.gantt_canvas.configure(xscrollcommand=h_scroll.set)

        self.gantt_canvas.pack(fill="x")
        h_scroll.pack(fill="x")

    # --- Helper UI Builders ---
    def _create_labeled_input(self, parent, label_text, col, default_val):
        box = tk.Frame(parent, bg=self.BG_CARD)
        box.grid(row=0, column=col, sticky="ew", padx=(0, 8))
        parent.columnconfigure(col, weight=1)

        tk.Label(
            box, text=label_text, font=("Segoe UI", 9),
            bg=self.BG_CARD, fg=self.FG_MUTED
        ).pack(anchor="w")

        entry = tk.Entry(
            box, font=("Segoe UI", 10), bg=self.BG_INPUT, fg=self.FG_TEXT,
            insertbackground=self.FG_TEXT, relief="flat"
        )
        entry.insert(0, default_val)
        entry.pack(fill="x", ipady=5, pady=(2, 0))
        return entry

    def _create_metric_box(self, parent, title, initial_value):
        box = tk.Frame(parent, bg=self.BG_INPUT, padx=14, pady=10)
        box.pack(side="left", fill="x", expand=True, padx=(0, 8))

        tk.Label(
            box, text=title, font=("Segoe UI", 9),
            bg=self.BG_INPUT, fg=self.FG_MUTED
        ).pack(anchor="w")

        val_label = tk.Label(
            box, text=initial_value, font=("Segoe UI", 16, "bold"),
            bg=self.BG_INPUT, fg=self.ACCENT
        )
        val_label.pack(anchor="w")
        return val_label

    # ==========================================================================
    # 3. INPUT VALIDATION & ACTIONS (Blocks Negatives, Decimals, Letters)
    # ==========================================================================

    def _parse_whole_number(self, raw_value, field_name, min_val=0):
        """
        Strictly validates that input is a non-negative whole number.
        Rejects empty strings, negative signs, decimals, and letters.
        """
        cleaned = raw_value.strip()
        if not cleaned.isdigit():
            messagebox.showerror(
                "Invalid Input",
                f"{field_name} must be a whole number (no negatives, decimals, or letters)."
            )
            return None

        number = int(cleaned)
        if number < min_val:
            messagebox.showerror(
                "Invalid Input",
                f"{field_name} must be at least {min_val}."
            )
            return None

        return number

    def _toggle_quantum(self, event=None):
        if self.algo_var.get() == "Round Robin":
            self.quantum_entry.config(state="normal")
        else:
            self.quantum_entry.config(state="disabled")

    def add_process(self):
        pid = self.pid_entry.get().strip()
        if not pid:
            messagebox.showerror("Invalid Input", "Process ID cannot be empty.")
            return

        if any(p["pid"].lower() == pid.lower() for p in self.processes):
            messagebox.showerror("Duplicate Process", f"Process '{pid}' already exists.")
            return

        at = self._parse_whole_number(self.at_entry.get(), "Arrival Time", min_val=0)
        if at is None:
            return

        bt = self._parse_whole_number(self.bt_entry.get(), "Burst Time", min_val=1)
        if bt is None:
            return

        self.processes.append({
            "pid": pid, "at": at, "bt": bt, "order": self.process_counter
        })
        self.queue_tree.insert("", "end", values=(pid, at, bt))

        # Auto-increment Process ID for convenience
        self.process_counter += 1
        self.pid_entry.delete(0, "end")
        self.pid_entry.insert(0, f"P{self.process_counter}")
        self.at_entry.delete(0, "end")
        self.at_entry.insert(0, "0")
        self.bt_entry.delete(0, "end")
        self.bt_entry.insert(0, "1")

    def remove_selected(self):
        selected = self.queue_tree.selection()
        if not selected:
            return
        for item in selected:
            pid = str(self.queue_tree.item(item, "values")[0])
            self.processes = [p for p in self.processes if p["pid"] != pid]
            self.queue_tree.delete(item)

    def clear_all(self):
        self.processes.clear()
        self.process_counter = 1
        for tree in (self.queue_tree, self.result_tree):
            for item in tree.get_children():
                tree.delete(item)
        self.gantt_canvas.delete("all")
        self.avg_wt_label.config(text="0.00")
        self.avg_tat_label.config(text="0.00")
        self.pid_entry.delete(0, "end")
        self.pid_entry.insert(0, "P1")

    def load_sample_data(self):
        self.clear_all()
        samples = [("P1", 0, 5), ("P2", 1, 3), ("P3", 2, 8), ("P4", 3, 6)]
        for pid, at, bt in samples:
            self.processes.append({
                "pid": pid, "at": at, "bt": bt, "order": self.process_counter
            })
            self.queue_tree.insert("", "end", values=(pid, at, bt))
            self.process_counter += 1
        self.pid_entry.delete(0, "end")
        self.pid_entry.insert(0, f"P{self.process_counter}")

    def run_simulation(self):
        if not self.processes:
            messagebox.showwarning("No Processes", "Add at least one process before running.")
            return

        algo = self.algo_var.get()
        if algo == "FCFS":
            results, gantt = simulate_fcfs(self.processes)
        elif algo == "SJF (Non-Preemptive)":
            results, gantt = simulate_sjf(self.processes)
        else:
            quantum = self._parse_whole_number(self.quantum_entry.get(), "Time Quantum", min_val=1)
            if quantum is None:
                return
            results, gantt = simulate_rr(self.processes, quantum)

        self._display_results(results)
        self._draw_gantt_chart(gantt)

    def _display_results(self, results):
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)

        total_wt = 0
        total_tat = 0
        for r in results:
            total_wt += r["wt"]
            total_tat += r["tat"]
            self.result_tree.insert("", "end", values=(
                r["pid"], r["at"], r["bt"], r["ct"], r["tat"], r["wt"]
            ))

        count = len(results)
        self.avg_wt_label.config(text=f"{total_wt / count:.2f} ms")
        self.avg_tat_label.config(text=f"{total_tat / count:.2f} ms")

    def _draw_gantt_chart(self, gantt):
        self.gantt_canvas.delete("all")
        if not gantt:
            return

        # Assign a consistent color to each unique process
        color_map = {}
        color_idx = 0
        for pid, _, _ in gantt:
            if pid != "IDLE" and pid not in color_map:
                color_map[pid] = self.GANTT_COLORS[color_idx % len(self.GANTT_COLORS)]
                color_idx += 1

        x_cursor = 24
        y_top, y_bottom = 22, 72
        unit_width = 36  # Pixels per unit of time

        for pid, start, end in gantt:
            duration = end - start
            block_w = max(duration * unit_width, 42)
            fill_color = "#334155" if pid == "IDLE" else color_map[pid]
            text_color = self.FG_MUTED if pid == "IDLE" else "#0F172A"

            # Draw process block
            self.gantt_canvas.create_rectangle(
                x_cursor, y_top, x_cursor + block_w, y_bottom,
                fill=fill_color, outline=self.BG_MAIN, width=2
            )
            self.gantt_canvas.create_text(
                x_cursor + block_w / 2, (y_top + y_bottom) / 2,
                text=pid, fill=text_color, font=("Segoe UI", 10, "bold")
            )
            # Draw start time label
            self.gantt_canvas.create_text(
                x_cursor, y_bottom + 14,
                text=str(start), fill=self.FG_TEXT, font=("Segoe UI", 9)
            )
            x_cursor += block_w

        # Draw final completion time label
        final_time = gantt[-1][2]
        self.gantt_canvas.create_text(
            x_cursor, y_bottom + 14,
            text=str(final_time), fill=self.FG_TEXT, font=("Segoe UI", 9, "bold")
        )

        self.gantt_canvas.configure(scrollregion=(0, 0, x_cursor + 30, 110))

if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerApp(root)
    root.mainloop()
