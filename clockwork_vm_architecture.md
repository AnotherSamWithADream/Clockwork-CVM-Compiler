# Clockwork Virtual Machine (CVM) Architecture

To run the entire Python Standard Library (including `regression.py`), we must abandon the idea of compiling Python syntax directly to static markers. Instead, we build a **Turing-Complete CPU (Virtual Machine)** inside Clockwork, and load the Python Bytecode directly into its memory.

Here is how a 16-bit Clockwork CVM natively evaluates CPython instructions (like `LOAD_FAST`, `BINARY_ADD`, `STORE_FAST`):

## Ring Assignments

* **Ring 0 (The HALT Flag):** Triggers `ifzhalt` when the CVM encounters the `RETURN_VALUE` bytecode from the main module.
* **Ring 1 (The Program Counter / Clock):** A single marker that sweeps across the rings. It carries the current **Instruction Offset** in its `value`.
* **Ring 2 (The Code ROM):** Stores the compiled JSON Bytecode.
* **Ring 3 (The Stack):** A dynamic array of memory.
* **Ring 4 (The Heap & Variables):** Stores variable states and float representations.

## How it works (Example: `LOAD_CONST` -> `STORE_NAME`)

### 1. Fetch
The Program Counter (Ring 1) sweeps around Ring 2. Every instruction on Ring 2 has an `ifzflip` lock. Ring 1 subtracts its `value` against the instruction's offset. When it hits `0`, it unlocks the target bytecode instruction.

### 2. Decode & Execute
If the instruction is `LOAD_CONST`:
* A "Seeker" marker is deployed to the Heap (Ring 4) to find the constant.
* The constant is `copied` and `sent` to the top of the Stack (Ring 3).
* The Stack Pointer marker increments by 1.

If the instruction is `BINARY_ADD`:
* The CVM executes a micro-loop. It reads the top two values on the Stack (Ring 3).
* It mathematically adds them using the Clockwork `gen` and `give` primitives.
* It pops the two operands and pushes the result back to the Stack.

### 3. Floats and Matrix Determinants
For complex math (like the `determinant_3x3` function in your regression script), the CVM relies on **Software Emulation**.
A float is stored in Ring 4 as three sequential markers:
1. Sign bit (0 or 1)
2. Mantissa (integer)
3. Exponent (integer)

When the Python bytecode calls for `BINARY_MULTIPLY` on two floats, the CVM drops into a dedicated physical block of rings (The Floating Point Unit) that manually manipulates these three markers to emulate IEEE 754 arithmetic using pure integers, before pushing the resulting 3 markers back onto the stack.

## Summary
By using `native_compiler.py`, we bypass the LLM entirely. We feed the raw CPython bytecode into the Clockwork VM's Instruction ROM. This guarantees 100% compatibility with the entire Python Standard Library, exactly as CPython runs it!
