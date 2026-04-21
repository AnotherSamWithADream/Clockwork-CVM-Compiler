import dis
import sys
import json
import types

def compile_to_cvm_bytecode(python_file):
    """
    Bypasses the LLM entirely.
    Uses Python's native compiler to generate strict Virtual Machine Bytecode.
    This is the ONLY way to compile the entire Python Standard Library to Clockwork.
    """
    print(f"Compiling {python_file} using CPython Native Compiler...")
    with open(python_file, 'r') as f:
        code_str = f.read()

    # Compile the Python code into a native code object
    code_obj = compile(code_str, python_file, 'exec')

    cvm_instructions = []
    
    def process_code_object(c_obj):
        for instr in dis.Bytecode(c_obj):
            arg = instr.argval
            if isinstance(arg, types.CodeType):
                arg = f"<code object {arg.co_name}>"
            elif not isinstance(arg, (int, float, str, bool, type(None))):
                arg = repr(arg)
                
            op = {
                "opcode": instr.opname,
                "arg": arg,
                "offset": instr.offset
            }
            cvm_instructions.append(op)
            
        # Recursively process functions defined inside the code
        for const in c_obj.co_consts:
            if isinstance(const, types.CodeType):
                cvm_instructions.append({"opcode": "--- FUNCTION_BOUNDARY ---", "arg": const.co_name, "offset": 0})
                process_code_object(const)

    process_code_object(code_obj)
    
    out_file = python_file.replace(".py", "_bytecode.json")
    with open(out_file, "w") as f:
        json.dump(cvm_instructions, f, indent=4)
        
    print(f"Successfully compiled native bytecode to {out_file}")
    return out_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python native_compiler.py <file.py>")
        sys.exit(1)
    compile_to_cvm_bytecode(sys.argv[1])
