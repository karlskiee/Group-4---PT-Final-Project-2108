# OS Page Replacement Simulator

An interactive desktop GUI built with Python and Tkinter to visualize and compare **FIFO**, **Least Recently Used (LRU)**, and **Optimal** operating system page replacement algorithms.

---

## Features

- **Three Replacement Algorithms:** Compare **FIFO**, **LRU**, and **Optimal** side by side on the same input.
- **Interactive Memory Grid:** Visualizes frame states, highlighted page hits, and `HIT` / `FAULT` badges across every step.
- **Step-by-Step Execution Log:** Detailed table showing requested pages, current frames in memory, status, and replaced victim pages.
- **Live Metrics Dashboard:** Automatically calculates Total References, Page Faults, Page Hits, Hit Ratio, and Fault Ratio.
- **Built-in Visual Guide:** Includes a scrollable in-app guide explaining inputs and simulation behavior.

---

## Requirements

- **Python 3.7+**
- **Tkinter** (bundled with standard Python on Windows & macOS)
- *Zero external `pip` dependencies required.*

> **Linux Users:** If Tkinter is not pre-installed, install it with:
> ```bash
> sudo apt update && sudo apt install python3-tk
> ```

---

## Getting Started

1. **Clone the repository**
   ```bash
   git clone [https://github.com/your-username/os-page-replacement-simulator.git](https://github.com/your-username/os-page-replacement-simulator.git)
   cd os-page-replacement-simulator
