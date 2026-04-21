# Clockwork CVM Compiler Stack
### A Turing-Complete CPython-to-Esoteric Virtual Machine Compiler

This repository contains the first full-scale compiler toolchain for the **Clockwork** esoteric programming language (CMIMC Competition 2026). The stack enables the compilation and execution of the **entire Python Standard Library** within Clockwork's 2D rotating mechanical rings.

## 🚀 Key Features
*   **Native CPython Compiler:** Bypasses LLM hallucinations by using CPython's actual `compile` and `dis` modules to generate machine-readable bytecode.
*   **Clockwork Virtual Machine (CVM):** A 24-bit virtualized CPU architecture physically mapped onto concentric rings, featuring a moving Stack Pointer and a dedicated FPU (Floating Point Unit).
*   **JIT Simulation Engine:** A Node.js backend that precomputes ring alignments, capable of simulating millions of ticks instantly.
*   **Interactive Orchestrator:** A unified CLI for compiling Python files or pasting code directly into the rings.
*   **QLoRA Training Stack:** A professional-grade fine-tuning pipeline to train specialized AI models to understand the physical physics of the rings.

## 🏗️ Architecture
The compiler uses a **Two-Stage Synthesis** approach:
1.  **Frontend:** `native_compiler.py` rips Python code into Bytecode.
2.  **Backend:** `cvm_synthesizer.py` builds the mechanical rings (Stack, Heap, ROM, IP, FPU) required to physically execute that logic.

For more details, see [Clockwork VM Architecture](clockwork_vm_architecture.md) and the [Turing Completeness Analysis](turing_analysis.md).

## 🛠️ Installation
Ensure you have Python 3.10+ and Node.js installed.

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/Clockwork-CVM-Compiler.git
cd Clockwork-CVM-Compiler

# Install Python dependencies
pip install requests
# (Optional: for AI training)
pip install torch transformers datasets peft trl bitsandbytes accelerate
```

## 💻 Usage
Run the interactive pipeline:
```bash
python clockwork_pipeline.py
```

### Modes:
*   **File Mode:** Provide a `.py` file to compile it into a Clockwork binary.
*   **Paste Mode:** Copy-paste any Python snippet (including recursion and matrix math) directly into the terminal.
*   **Interactive Testing:** Manually provide inputs and expected outputs to verify your code inside the rings.

## 🧪 Examples
You can find complex examples like **Gaussian Elimination**, **SAT Solvers**, and **Alpha-Beta Search** in `ultimate_test.py`.

## 📜 Credits
Developed as an autonomous architectural extension for the CMIMC 2026 Clockwork competition.
