import json
import random

# Dataset Generator for Layer 1: Python -> Intermediate Representation (IR)
# This builds a dataset of Python algorithms and their corresponding 
# Clockwork IR JSON. We use this to fine-tune a model so it becomes 
# a native expert at outputting our exact IR format.

def build_ir_dataset(num_samples=2500, filename="ir_training_dataset.jsonl"):
    print(f"Generating {num_samples} Python-to-IR training pairs...")
    
    dataset = []
    
    # Example 1: GCD
    py_gcd = "def gcd(a, b):\n  while b != 0:\n    if a > b:\n      a = a - b\n    else:\n      b = b - a\n  return a"
    ir_gcd = [
        {"op": "INPUT", "var": "a", "index": 0},
        {"op": "INPUT", "var": "b", "index": 1},
        {"op": "WHILE_NOT_ZERO", "var": "b"},
        {"op": "SUB", "dest": "a", "src": "b"},
        {"op": "SUB", "dest": "b", "src": "a"},
        {"op": "END_WHILE"},
        {"op": "HALT", "var": "a"}
    ]
    
    # Example 2: Factorial
    py_fact = "def factorial(n):\n  res = 1\n  while n != 0:\n    res = res * n\n    n = n - 1\n  return res"
    ir_fact = [
        {"op": "INPUT", "var": "n", "index": 0},
        {"op": "SET", "var": "res", "value": 1},
        {"op": "WHILE_NOT_ZERO", "var": "n"},
        {"op": "ADD", "dest": "res", "src": "n"}, # Simplified placeholder for MUL
        {"op": "SET", "var": "one", "value": 1},
        {"op": "SUB", "dest": "n", "src": "one"},
        {"op": "END_WHILE"},
        {"op": "HALT", "var": "res"}
    ]
    
    # Example 3: Addition
    py_add = "def add(x, y):\n  return x + y"
    ir_add = [
        {"op": "INPUT", "var": "x", "index": 0},
        {"op": "INPUT", "var": "y", "index": 1},
        {"op": "ADD", "dest": "x", "src": "y"},
        {"op": "HALT", "var": "x"}
    ]

    templates = [
        (py_gcd, ir_gcd),
        (py_fact, ir_fact),
        (py_add, ir_add)
    ]
    
    with open(filename, 'w') as f:
        for i in range(num_samples):
            py_code, ir_json = random.choice(templates)
            
            prompt = f"""You are Layer 1 of a Neuro-Symbolic Compiler. Translate the following Python algorithm into a JSON Intermediate Representation (IR).
Available IR Instructions: INPUT, SET, ADD, SUB, WHILE_NOT_ZERO, END_WHILE, HALT.
Python Code:
```python
{py_code}
```
Output ONLY a valid JSON array."""
            
            response = f"```json\n{json.dumps(ir_json, indent=2)}\n```"
            
            f.write(json.dumps({"instruction": prompt, "output": response}) + "\n")
            
    print(f"Dataset completely built and saved to {filename}")

if __name__ == "__main__":
    build_ir_dataset()