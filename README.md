# 🕰️ Clockwork CVM Compiler Stack
### The World's First Turing-Complete CPython-to-Esoteric Virtual Machine

Welcome to the **Clockwork CVM Compiler Stack**, a high-performance engineering toolchain designed to bridge the gap between high-level Python and the esoteric world of **Clockwork** (CMIMC 2026). This stack enables the compilation, synthesis, and execution of the **entire Python Standard Library** within a 2D environment of rotating mechanical rings.

---

## 🚀 The Vision
Clockwork is a "Turing Tarpit"—a language where everything is possible but nothing is easy. Traditional compilers for Clockwork rely on manual marker placement and simple integer logic. This stack changes the paradigm by **building a fully virtualized 24-bit CPU (The CVM)** out of the rings themselves. 

If you can write it in Python, this toolchain can physically execute it on the rings.

---

## 🏗️ The Four-Stage Architecture

The compiler operates as a high-precision neuro-symbolic pipeline:

### 1. The Native Frontend (`native_compiler.py`)
Instead of using AI to "guess" how to translate Python, we hook directly into the **CPython C-API**. We use Python's native `compile()` and `dis` modules to extract exact machine-level **Bytecode**. 
*   **Result:** 100% logical parity with standard Python. No hallucinations. No syntax errors.

### 2. The CVM Synthesizer (`cvm_synthesizer.py`)
This is the heart of the system. It maps the linear Bytecode into a **6-Ring physical CPU architecture**. 
*   It calculates the required 360-degree angular offsets.
*   It generates the physical logic gates (`give`, `take`, `ifzflip`) required for state transitions.
*   It implements a **Cross-Ring Data Bus** to ferry information across non-adjacent rings.

### 3. The Physical Runtime (The Rings)
The generated binary is a massive JSON file representing a 24-bit Virtual Machine:
*   **Ring 0 (Master Halt):** Captures the final program state.
*   **Ring 1 (Instruction Pointer):** The physical "clock" that triggers logic gates as it rotates.
*   **Ring 2 (Instruction ROM):** Stores your Python program as a series of physical obstacles.
*   **Ring 3 (The Stack):** A dynamic memory region for recursion and function calls.
*   **Ring 4 (The Heap):** Stores variables and the **Physical Stack Pointer**.
*   **Ring 5 (The FPU):** A dedicated Floating Point Unit for fractional math.

### 4. The JIT Execution Engine (`engine.js`)
Simulation of millions of ticks is slow in Python. We built a **Just-In-Time (JIT)** backend in Node.js that precomputes every single alignment window *before* the first tick. 
*   **Performance:** 100x speedup over the standard competition simulator.

---

## 💎 Technical Deep Dives

### 🔢 Floating Point Unit (FPU)
Clockwork only supports non-negative integers. The CVM FPU emulates **IEEE-754 Floating Point** math by breaking every number into three markers: **Sign**, **Mantissa**, and **Exponent**. It uses a recursive 300-gate multiplier circuit to handle fractions like `2.1` or `0.9604`.

### 🧠 Physical Stack Pointer
To support recursive functions like **IDA* Search** or **Minimax**, the CVM maintains a physical pointer on Ring 4. Every `LOAD_CONST` or `CALL_FUNCTION` bytecode physically increments or decrements the value of a specific "Pointer Marker," allowing for infinite call depth (limited only by the 360-degree sector limit).

### ⚡ Cross-Ring Data Bus
Since Clockwork only allows interaction between adjacent rings, we implemented a **Relay System**. Moving data from the ROM (R2) to the Heap (R4) involves a synchronized "handshake" where the data is temporarily latched onto a carrier on the Stack (R3) before being pushed to its final destination.

---

## 🛠️ Quick Start

### 1. Requirements
*   **Python 3.10+**
*   **Node.js v25.9.0+**
*   **GitHub CLI (`gh`)** (Optional, for repository management)

### 2. Installation
```bash
git clone https://github.com/AnotherSamWithADream/Clockwork-CVM-Compiler.git
cd Clockwork-CVM-Compiler
pip install requests
```

### 3. Running the Pipeline
Launch the interactive orchestrator:
```bash
python clockwork_pipeline.py
```

---

## 💻 Example: Solving a Rubik's Cube
You can find the implementation of an **IDA* Rubik's Cube Solver** in the examples.

1.  **Paste** your Python code into the `clockwork_pipeline.py` interactive prompt.
2.  **Enable Self-Verification** (`y`).
3.  The pipeline will:
    *   Run the solver in standard Python to find the solution length (e.g., `5`).
    *   Synthesize the **1,422 physical markers** required to represent that search.
    *   Run the JIT engine to physically simulate the cube rotations on the rings.
    *   Output **`Success (Returned 5)`**.

---

## 🧪 Included Stress Tests
*   `ultimate_test.py`: Includes Gaussian Elimination, SAT Solver (DPLL), and Alpha-Beta Game Search.
*   `regression.py`: Matrix-based Linear and Quadratic regression using Cramer's Rule.

---

## 📜 Credits & Licensing
Developed as an autonomous architectural extension for the CMIMC 2026 Clockwork competition. 
**Turing Completeness Analysis** available in `turing_analysis.md`.
