import sys
import json
import subprocess
import os

def run_cvm_pipeline(py_file_path, test_file):
    print("\n=============================================")
    print("   CLOCKWORK NATIVE VIRTUAL MACHINE COMPILER  ")
    print("=============================================\n")
    
    # Phase 1: Native CPython Bytecode Compilation
    print(f"[Phase 1] Compiling {py_file_path} to Bytecode...")
    result = subprocess.run([sys.executable, "native_compiler.py", py_file_path], capture_output=True, text=True)
    if result.returncode != 0:
        print(">> Compilation failed:")
        print(result.stderr)
        return
    print(">> Bytecode successfully generated.")
    
    bytecode_file = py_file_path.replace(".py", "_bytecode.json")
    
    # Phase 2: CVM Synthesis (CPU Mapping)
    print("\n[Phase 2] Synthesizing Clockwork CPU Layout (CVM)...")
    result = subprocess.run([sys.executable, "cvm_synthesizer.py", bytecode_file], capture_output=True, text=True)
    if result.returncode != 0:
        print(">> Synthesis failed:")
        print(result.stderr)
        return
    print(result.stdout.strip())
    
    cvm_file = py_file_path.replace(".py", "_cvm.json")
    
    # Phase 3: JIT Execution
    if test_file and os.path.exists(test_file):
        print(f"\n[Execution] Running {cvm_file} on JIT Engine...")
        result = subprocess.run(["node", "engine.js", "-c", cvm_file, "-t", test_file, "-v"], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
    else:
        print("\n[Execution] No test file provided. Compilation complete.")
    
    print("\nCVM Pipeline Process Complete!")

def main():
    # Headless mode if arguments provided
    if len(sys.argv) >= 2:
        py_file = sys.argv[1]
        test_file = sys.argv[2] if len(sys.argv) > 2 else None
        if not os.path.exists(py_file):
            print(f"Error: {py_file} not found.")
            sys.exit(1)
        run_cvm_pipeline(py_file, test_file)
        return

    # Interactive Menu
    print("=============================================")
    print("   CLOCKWORK CVM INTERACTIVE INTERFACE       ")
    print("=============================================")
    print("1. Compile and run a Python file")
    print("2. Paste Python code directly")
    choice = input("Enter choice (1/2): ").strip()
    
    if choice == "1":
        py_file = input("Enter the path to the Python file: ").strip()
        if not os.path.exists(py_file):
            print(f"Error: {py_file} not found.")
            sys.exit(1)
            
        test_file = input("Enter test file path (optional, press Enter for manual input): ").strip()
        
        if not test_file:
            manual_input = input("Enter test input values (comma separated, e.g. 10,20 or press Enter for empty): ").strip()
            manual_expected = input("Enter expected output integer: ").strip()
            
            if manual_expected:
                inp_list = [int(x.strip()) for x in manual_input.split(',')] if manual_input else []
                test_data = [{"input": inp_list, "output": [int(manual_expected)]}]
                test_file = "manual_test.json"
                with open(test_file, "w") as f:
                    json.dump(test_data, f)
                    
        run_cvm_pipeline(py_file, test_file)
        
    elif choice == "2":
        print("\nPaste your Python code below. Type 'EOF' on a new line and press Enter:")
        lines = []
        try:
            while True:
                line = input()
                if line.strip() == "EOF": break
                lines.append(line)
        except EOFError: pass
        
        py_code = "\n".join(lines)
        if not py_code.strip():
            print("No code provided.")
            sys.exit(1)
            
        temp_file = "interactive_temp.py"
        with open(temp_file, "w") as f:
            f.write(py_code)
            
        test_file = input("Enter test file path (optional, press Enter for manual input): ").strip()
        
        if not test_file:
            manual_input = input("Enter test input values (comma separated, e.g. 10,20 or press Enter for empty): ").strip()
            manual_expected = input("Enter expected output integer: ").strip()
            
            if manual_expected:
                inp_list = [int(x.strip()) for x in manual_input.split(',')] if manual_input else []
                test_data = [{"input": inp_list, "output": [int(manual_expected)]}]
                test_file = "manual_test.json"
                with open(test_file, "w") as f:
                    json.dump(test_data, f)

        run_cvm_pipeline(temp_file, test_file)
        
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()
