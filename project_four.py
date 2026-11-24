"""
PT 101 - Platform Technologies | Final Project
Topic 4: Disk Scheduling Algorithms (FCFS, SSTF, SCAN / Elevator)

Reference:
    Silberschatz, A., Galvin, P. B., & Gagne, G. (Operating System Concepts)
"""

import tkinter as tk
from tkinter import ttk, messagebox


# ==============================================================================
# PART 1: INPUT VALIDATION
# Checks that all inputs are numbers and stay within [disk_min, disk_max].
# ==============================================================================
def validate_inputs(min_text, max_text, head_text, queue_text):
    # 1. Check disk minimum and maximum
    try:
        disk_min = int(min_text.strip())
        disk_max = int(max_text.strip())
    except ValueError:
        return False, "Disk Minimum and Maximum must be whole numbers."

    if disk_min < 0:
        return False, "Disk Minimum cannot be negative."
    if disk_min >= disk_max:
        return False, "Disk Minimum must be less than Disk Maximum."

    # 2. Check initial head position
    try:
        initial_head = int(head_text.strip())
    except ValueError:
        return False, "Initial Head Position must be a whole number."

    if initial_head < disk_min or initial_head > disk_max:
        return False, f"Initial Head must be between {disk_min} and {disk_max}."

    # 3. Check request queue (accepts commas or spaces)
    cleaned_text = queue_text.replace(",", " ")
    items = cleaned_text.split()

    if len(items) == 0:
        return False, "Please enter at least one cylinder request."

    request_queue = []
    for item in items:
        try:
            cylinder = int(item)
        except ValueError:
            return False, f"'{item}' is not a valid cylinder number."

        if cylinder < disk_min or cylinder > disk_max:
            return False, f"Request {cylinder} is outside the disk range ({disk_min}-{disk_max})."

        request_queue.append(cylinder)

    return True, (disk_min, disk_max, initial_head, request_queue)


# ==============================================================================
# PART 2: DISK SCHEDULING ALGORITHMS (FCFS, SSTF, SCAN)
# Each function returns: (service_sequence, step_list, total_movement)
# ==============================================================================

def solve_fcfs(initial_head, request_queue):
    """
    FCFS (First-Come, First-Served):
    Services requests in the exact order they appear in the queue.
    """
    current = initial_head
    total_movement = 0
    sequence = [str(initial_head)]
    steps = []

    step_number = 1
    for target in request_queue:
        movement = abs(current - target)
        total_movement += movement

        steps.append((
            step_number,
            current,
            target,
            f"|{current} - {target}|",
            movement,
            total_movement,
            "Next in queue"
        ))

        sequence.append(str(target))
        current = target
        step_number += 1

    return sequence, steps, total_movement


def solve_sstf(initial_head, request_queue):
    """
    SSTF (Shortest Seek Time First):
    Always picks the unvisited request closest to the current head position.
    """
    current = initial_head
    unvisited = list(request_queue)  # Make a copy so original queue stays intact
    total_movement = 0
    sequence = [str(initial_head)]
    steps = []

    step_number = 1
    while len(unvisited) > 0:
        # Find the request with the smallest distance from the current head
        closest_req = unvisited[0]
        shortest_dist = abs(current - closest_req)

        for req in unvisited:
            dist = abs(current - req)
            if dist < shortest_dist:
                shortest_dist = dist
                closest_req = req

        # Move to the closest request and remove it from unvisited
        unvisited.remove(closest_req)
        total_movement += shortest_dist

        steps.append((
            step_number,
            current,
            closest_req,
            f"|{current} - {closest_req}|",
            shortest_dist,
            total_movement,
            "Closest cylinder"
        ))

        sequence.append(str(closest_req))
        current = closest_req
        step_number += 1

    return sequence, steps, total_movement


def solve_scan(initial_head, request_queue, disk_min, disk_max, direction, reach_boundary):
    """
    SCAN (Elevator Algorithm):
    Sweeps in the chosen direction, servicing requests along the way.
    Reaches the disk boundary before reversing if requests exist on the other side.
    """
    current = initial_head
    total_movement = 0
    sequence = [str(initial_head)]
    steps = []
    step_number = 1

    # Separate requests into Left (< initial_head), Right (> initial_head), and Equal
    equal_requests = []
    left_requests = []
    right_requests = []

    for req in request_queue:
        if req == initial_head:
            equal_requests.append(req)
        elif req < initial_head:
            left_requests.append(req)
        else:
            right_requests.append(req)

    # Sort left side descending (e.g., 37, 14) and right side ascending (e.g., 65, 98)
    left_requests.sort(reverse=True)
    right_requests.sort()

    # First, service any request already at the starting head position
    for req in equal_requests:
        steps.append((step_number, current, req, f"|{current} - {req}|", 0, total_movement, "Already at head"))
        sequence.append(str(req))
        step_number += 1

    if direction == "Left":
        # 1. Move Left towards disk_min
        for req in left_requests:
            movement = abs(current - req)
            total_movement += movement
            steps.append((step_number, current, req, f"|{current} - {req}|", movement, total_movement, "Moving Left"))
            sequence.append(str(req))
            current = req
            step_number += 1

        # 2. If there are requests on the Right, hit disk_min first (if enabled), then reverse
        if len(right_requests) > 0:
            if reach_boundary and current != disk_min:
                movement = abs(current - disk_min)
                total_movement += movement
                steps.append((
                    step_number, current, disk_min, f"|{current} - {disk_min}|",
                    movement, total_movement, "Hit Min Boundary"
                ))
                sequence.append(f"[{disk_min}]")
                current = disk_min
                step_number += 1

            for req in right_requests:
                movement = abs(current - req)
                total_movement += movement
                steps.append((step_number, current, req, f"|{current} - {req}|", movement, total_movement, "Reversed Right"))
                sequence.append(str(req))
                current = req
                step_number += 1

    else:  # direction == "Right"
        # 1. Move Right towards disk_max
        for req in right_requests:
            movement = abs(current - req)
            total_movement += movement
            steps.append((step_number, current, req, f"|{current} - {req}|", movement, total_movement, "Moving Right"))
            sequence.append(str(req))
            current = req
            step_number += 1

        # 2. If there are requests on the Left, hit disk_max first (if enabled), then reverse
        if len(left_requests) > 0:
            if reach_boundary and current != disk_max:
                movement = abs(current - disk_max)
                total_movement += movement
                steps.append((
                    step_number, current, disk_max, f"|{current} - {disk_max}|",
                    movement, total_movement, "Hit Max Boundary"
                ))
                sequence.append(f"[{disk_max}]")
                current = disk_max
                step_number += 1

            for req in left_requests:
                movement = abs(current - req)
                total_movement += movement
                steps.append((step_number, current, req, f"|{current} - {req}|", movement, total_movement, "Reversed Left"))
                sequence.append(str(req))
                current = req
                step_number += 1

    return sequence, steps, total_movement


# ==============================================================================
# PART 3: GUI HELPER FUNCTIONS (UPDATING TABLES & DRAWING THE CHART)
# ==============================================================================

def fill_trace_table(tree, steps):
    """Clears and fills a step-by-step trace table."""
    for row in tree.get_children():
        tree.delete(row)

    for step in steps:
        tree.insert("", "end", values=(
            step[0],              # Step #
            step[1],              # From Cylinder
            step[2],              # To Cylinder
            step[3],              # Formula |a - b|
            f"{step[4]} cyl",     # Movement
            f"{step[5]} cyl",     # Cumulative Total
            step[6]               # Note
        ))


def draw_seek_chart(canvas, disk_min, disk_max, initial_head, fcfs_steps, sstf_steps, scan_steps):
    """Draws a simple line graph showing how the disk head moves across cylinders."""
    canvas.delete("all")

    # Canvas dimensions and margins
    left_margin = 50
    right_margin = 630
    top_margin = 35
    bottom_margin = 205
    usable_width = right_margin - left_margin
    usable_height = bottom_margin - top_margin

    # Draw top axis line and cylinder markers (Min, Middle, Max)
    canvas.create_line(left_margin, top_margin, right_margin, top_margin, fill="black", width=2)
    mid_cyl = (disk_min + disk_max) // 2

    for cyl, x_pos in [(disk_min, left_margin), (mid_cyl, (left_margin + right_margin) // 2), (disk_max, right_margin)]:
        canvas.create_line(x_pos, top_margin - 5, x_pos, bottom_margin, fill="#E0E0E0", dash=(3, 3))
        canvas.create_text(x_pos, top_margin - 15, text=str(cyl), font=("Arial", 9, "bold"))

    # Helper function to plot one algorithm's path
    def plot_path(steps, color):
        # Build list of visited cylinders starting from initial_head
        cylinders = [initial_head]
        for s in steps:
            cylinders.append(s[2])

        total_points = len(cylinders)
        y_gap = usable_height / max(1, total_points - 1)

        coords = []
        for i in range(total_points):
            # Convert cylinder number to X pixel position
            ratio = (cylinders[i] - disk_min) / (disk_max - disk_min)
            x = left_margin + (ratio * usable_width)
            y = top_margin + (i * y_gap)
            coords.append((x, y, cylinders[i]))

        # Connect points with lines and draw dots
        for i in range(len(coords) - 1):
            canvas.create_line(coords[i][0], coords[i][1], coords[i + 1][0], coords[i + 1][1], fill=color, width=2)

        for x, y, cyl in coords:
            canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill=color, outline=color)
            canvas.create_text(x, y - 9, text=str(cyl), fill=color, font=("Arial", 8, "bold"))

    # Plot all three algorithms in distinct colors
    plot_path(fcfs_steps, "red")
    plot_path(sstf_steps, "blue")
    plot_path(scan_steps, "green")


def run_simulation():
    """Main button action: validates inputs, runs all 3 algorithms, and updates the UI."""
    valid, result = validate_inputs(
        min_entry.get(),
        max_entry.get(),
        head_entry.get(),
        queue_entry.get()
    )

    if not valid:
        messagebox.showerror("Invalid Input", result)
        return

    disk_min, disk_max, initial_head, request_queue = result
    direction = scan_dir_var.get()
    reach_boundary = boundary_var.get()

    # Run the 3 algorithms
    fcfs_seq, fcfs_steps, fcfs_total = solve_fcfs(initial_head, request_queue)
    sstf_seq, sstf_steps, sstf_total = solve_sstf(initial_head, request_queue)
    scan_seq, scan_steps, scan_total = solve_scan(
        initial_head, request_queue, disk_min, disk_max, direction, reach_boundary
    )

    # Update Summary Info Label
    summary_label.config(
        text=f"Initial Head: {initial_head}   |   Disk Range: {disk_min} to {disk_max}   |   Request Queue: {request_queue}"
    )

    # Update Comparison Table
    for row in comp_tree.get_children():
        comp_tree.delete(row)

    num_requests = len(request_queue)
    lowest_total = min(fcfs_total, sstf_total, scan_total)

    rows = [
        ("FCFS (First-Come, First-Served)", fcfs_total, round(fcfs_total / num_requests, 2), " -> ".join(fcfs_seq)),
        ("SSTF (Shortest Seek Time First)", sstf_total, round(sstf_total / num_requests, 2), " -> ".join(sstf_seq)),
        (f"SCAN / Elevator ({direction})", scan_total, round(scan_total / num_requests, 2), " -> ".join(scan_seq)),
    ]

    for algo_name, total_mov, avg_mov, seq_str in rows:
        remark = "Best (Lowest Movement)" if total_mov == lowest_total else "-"
        comp_tree.insert("", "end", values=(algo_name, f"{total_mov} cylinders", f"{avg_mov} cyl", remark, seq_str))

    # Update Individual Trace Tables & Totals
    fcfs_header.config(text=f"FCFS Service Sequence: {' -> '.join(fcfs_seq)}\nTotal Head Movement: {fcfs_total} cylinders")
    sstf_header.config(text=f"SSTF Service Sequence: {' -> '.join(sstf_seq)}\nTotal Head Movement: {sstf_total} cylinders")
    scan_header.config(text=f"SCAN Service Sequence: {' -> '.join(scan_seq)}\nTotal Head Movement: {scan_total} cylinders")

    fill_trace_table(fcfs_tree, fcfs_steps)
    fill_trace_table(sstf_tree, sstf_steps)
    fill_trace_table(scan_tree, scan_steps)

    # Draw Visual Chart
    draw_seek_chart(chart_canvas, disk_min, disk_max, initial_head, fcfs_steps, sstf_steps, scan_steps)


def load_test_case(d_min, d_max, head, queue, direction):
    """Fills the input boxes with a preset test case and runs it."""
    min_entry.delete(0, tk.END)
    min_entry.insert(0, d_min)

    max_entry.delete(0, tk.END)
    max_entry.insert(0, d_max)

    head_entry.delete(0, tk.END)
    head_entry.insert(0, head)

    queue_entry.delete(0, tk.END)
    queue_entry.insert(0, queue)

    scan_dir_var.set(direction)
    boundary_var.set(True)
    run_simulation()


def clear_all():
    """Clears all input fields."""
    min_entry.delete(0, tk.END)
    max_entry.delete(0, tk.END)
    head_entry.delete(0, tk.END)
    queue_entry.delete(0, tk.END)


# ==============================================================================
# PART 4: TKINTER GUI WINDOW LAYOUT
# ==============================================================================
window = tk.Tk()
window.title("PT 101 - Topic 4: Disk Scheduling Simulator (FCFS, SSTF, SCAN)")
window.geometry("1080x680")

# Top Title Banner
header_frame = tk.Frame(window, bg="#1F3A52", pady=10, padx=15)
header_frame.pack(fill="x")
tk.Label(
    header_frame, text="DISK SCHEDULING SIMULATOR (FCFS, SSTF, SCAN)",
    fg="white", bg="#1F3A52", font=("Arial", 14, "bold")
).pack(anchor="w")
tk.Label(
    header_frame, text="PT 101 - Platform Technologies | Topic 4",
    fg="#D9E2EC", bg="#1F3A52", font=("Arial", 9)
).pack(anchor="w")

# Main Layout Frame
main_frame = tk.Frame(window, padx=10, pady=10)
main_frame.pack(fill="both", expand=True)

# --- LEFT PANEL: USER INPUTS ---
input_frame = tk.LabelFrame(main_frame, text="Input Parameters", font=("Arial", 10, "bold"), padx=12, pady=10)
input_frame.pack(side="left", fill="y", padx=(0, 10))

tk.Label(input_frame, text="Disk Minimum Cylinder:").pack(anchor="w")
min_entry = tk.Entry(input_frame, width=28)
min_entry.insert(0, "0")
min_entry.pack(anchor="w", pady=(2, 8))

tk.Label(input_frame, text="Disk Maximum Cylinder:").pack(anchor="w")
max_entry = tk.Entry(input_frame, width=28)
max_entry.insert(0, "199")
max_entry.pack(anchor="w", pady=(2, 8))

tk.Label(input_frame, text="Initial Head Position:").pack(anchor="w")
head_entry = tk.Entry(input_frame, width=28)
head_entry.insert(0, "53")
head_entry.pack(anchor="w", pady=(2, 8))

tk.Label(input_frame, text="Request Queue (comma/space separated):").pack(anchor="w")
queue_entry = tk.Entry(input_frame, width=28)
queue_entry.insert(0, "98, 183, 37, 122, 14, 124, 65, 67")
queue_entry.pack(anchor="w", pady=(2, 10))

tk.Label(input_frame, text="Initial SCAN Direction:").pack(anchor="w")
scan_dir_var = tk.StringVar(value="Left")
tk.Radiobutton(input_frame, text="Left (Towards Disk Min)", variable=scan_dir_var, value="Left").pack(anchor="w")
tk.Radiobutton(input_frame, text="Right (Towards Disk Max)", variable=scan_dir_var, value="Right").pack(anchor="w")

boundary_var = tk.BooleanVar(value=True)
tk.Checkbutton(
    input_frame, text="Reach disk boundary before reversing", variable=boundary_var
).pack(anchor="w", pady=(8, 12))

tk.Button(
    input_frame, text="Calculate & Compare", bg="#2B6CB0", fg="white",
    font=("Arial", 10, "bold"), width=24, command=run_simulation
).pack(pady=4)

tk.Button(input_frame, text="Clear Inputs", width=24, command=clear_all).pack(pady=2)

# Preset Test Cases (for easy live demo)
tk.Label(input_frame, text="Sample Test Cases:", font=("Arial", 9, "bold")).pack(anchor="w", pady=(15, 4))
tk.Button(
    input_frame, text="Test 1: Textbook Default", width=24,
    command=lambda: load_test_case("0", "199", "53", "98, 183, 37, 122, 14, 124, 65, 67", "Left")
).pack(pady=2)
tk.Button(
    input_frame, text="Test 2: SCAN Moving Right", width=24,
    command=lambda: load_test_case("0", "199", "50", "82, 170, 43, 140, 24, 16, 190", "Right")
).pack(pady=2)
tk.Button(
    input_frame, text="Test 3: Range 0 - 499", width=24,
    command=lambda: load_test_case("0", "499", "215", "410, 95, 320, 15, 250, 480, 130", "Left")
).pack(pady=2)

# --- RIGHT PANEL: TABS FOR RESULTS ---
notebook = ttk.Notebook(main_frame)
notebook.pack(side="left", fill="both", expand=True)

# TAB 1: Comparison & Graph
tab_summary = tk.Frame(notebook, padx=10, pady=10)
notebook.add(tab_summary, text="Comparison & Visual Graph")

summary_label = tk.Label(tab_summary, text="", font=("Arial", 9, "bold"), fg="#1F3A52")
summary_label.pack(anchor="w", pady=(0, 8))

comp_cols = ("Algorithm", "Total Movement", "Avg Movement", "Remark", "Service Sequence")
comp_tree = ttk.Treeview(tab_summary, columns=comp_cols, show="headings", height=4)
for col, width in [("Algorithm", 190), ("Total Movement", 120), ("Avg Movement", 100), ("Remark", 145), ("Service Sequence", 260)]:
    comp_tree.heading(col, text=col)
    comp_tree.column(col, width=width)
comp_tree.pack(fill="x", pady=(0, 10))

# Legend for the graph
legend_frame = tk.Frame(tab_summary)
legend_frame.pack(anchor="w", pady=(2, 2))
tk.Label(legend_frame, text="Head Movement Graph:   ", font=("Arial", 9, "bold")).pack(side="left")
tk.Label(legend_frame, text="■ FCFS   ", fg="red", font=("Arial", 9, "bold")).pack(side="left")
tk.Label(legend_frame, text="■ SSTF   ", fg="blue", font=("Arial", 9, "bold")).pack(side="left")
tk.Label(legend_frame, text="■ SCAN", fg="green", font=("Arial", 9, "bold")).pack(side="left")

chart_canvas = tk.Canvas(tab_summary, width=680, height=230, bg="white", relief="solid", borderwidth=1)
chart_canvas.pack(fill="both", expand=True, pady=(4, 0))

# Helper function to create the 3 identical Trace Tabs
def create_trace_tab(tab_title):
    tab = tk.Frame(notebook, padx=10, pady=10)
    notebook.add(tab, text=tab_title)

    header_lbl = tk.Label(tab, text="", font=("Arial", 10, "bold"), justify="left")
    header_lbl.pack(anchor="w", pady=(0, 8))

    cols = ("Step", "From", "To", "Formula", "Movement", "Cumulative", "Note")
    tree = ttk.Treeview(tab, columns=cols, show="headings")
    for col, width in [("Step", 50), ("From", 80), ("To", 80), ("Formula", 110), ("Movement", 95), ("Cumulative", 105), ("Note", 150)]:
        tree.heading(col, text=col)
        tree.column(col, width=width, anchor="center")
    tree.pack(fill="both", expand=True)

    return header_lbl, tree

fcfs_header, fcfs_tree = create_trace_tab("FCFS Step-by-Step")
sstf_header, sstf_tree = create_trace_tab("SSTF Step-by-Step")
scan_header, scan_tree = create_trace_tab("SCAN Step-by-Step")

# TAB 5: User Guide
tab_guide = tk.Frame(notebook, padx=12, pady=12)
notebook.add(tab_guide, text="User Guide")
guide_box = tk.Text(tab_guide, wrap="word", font=("Arial", 10))
guide_box.insert("1.0", """HOW TO USE THIS PROGRAM:
1. Enter the Disk Minimum and Maximum cylinder numbers (example: 0 to 199).
2. Enter the Initial Head Position (where the read/write arm starts).
3. Enter the Request Queue separated by commas or spaces.
4. Select the Initial SCAN Direction (Left goes toward Min, Right goes toward Max).
5. Click 'Calculate & Compare' to see the service sequence, step-by-step math, total head movement, and visual graph.

FORMULAS USED:
- Step Head Movement = |Current Cylinder - Next Cylinder|
- Total Head Movement = Sum of all step movements
- Average Seek Length = Total Head Movement / Number of Requests
""")
guide_box.config(state="disabled")
guide_box.pack(fill="both", expand=True)

# Run default example when program opens
run_simulation()
window.mainloop()