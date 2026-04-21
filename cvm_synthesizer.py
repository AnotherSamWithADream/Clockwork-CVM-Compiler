import json
import sys
import struct
import math

def get_bs(bit_index, width=24):
    bs = ['0'] * width
    if bit_index < width:
        bs[bit_index] = '1'
    return "".join(bs)

def float_to_fpu_parts(f):
    if f == 0.0: return 0, 0, 1024
    sign = 1 if f < 0 else 0
    f = abs(f)
    mantissa = int(f * 10000)
    exponent = 4
    return sign, mantissa, exponent

class CVMSynthesizer:
    def __init__(self, bytecode):
        self.bytecode = bytecode
        self.bitwidth = 24
        self.ops = [
            "give", "take", "drop", "gen", "copy", "send", "ifzflip", "ifzhalt",
            "give", "take", "drop", "gen", "copy", "send", "ifzflip", "ifzhalt",
            "give", "take", "drop", "gen", "copy", "send", "ifzflip", "ifzhalt"
        ]
        self.r0_halt = []
        self.r1_ip = []
        self.r2_rom = []
        self.r3_stack = []
        self.r4_heap = []
        self.r5_fpu = []
        self.static_sp_offset = 10 
        self.rom_angle = 10

    def synthesize(self):
        print(f"Initializing Clockwork Virtual Machine Synthesis for {len(self.bytecode)} bytecodes...")
        
        self.r0_halt.append({"position": 0, "bitstring": get_bs(23, self.bitwidth), "value": 82})
        self.r1_ip.append({"position": 0, "bitstring": "1" * self.bitwidth})
        self.r4_heap.append({"position": 0, "bitstring": "0"*self.bitwidth, "value": 0, "comment": "PHYSICAL_STACK_POINTER"})
        
        for instr in self.bytecode:
            opcode = instr["opcode"]
            arg = instr["arg"]
            self.rom_angle = (self.rom_angle + 1) % 360
            
            if opcode == "LOAD_CONST":
                self._build_load_const(self.rom_angle, arg)
            elif opcode in ("STORE_NAME", "STORE_FAST", "STORE_ATTR"):
                self._build_store_name(self.rom_angle, arg)
            elif opcode in ("LOAD_NAME", "LOAD_FAST", "LOAD_GLOBAL", "LOAD_METHOD", "LOAD_ATTR"):
                self._build_load_name(self.rom_angle, arg)
            elif opcode == "BINARY_ADD":
                self._build_binary_add(self.rom_angle)
            elif opcode == "BINARY_SUBTRACT":
                self._build_binary_subtract(self.rom_angle)
            elif opcode == "BINARY_MULTIPLY":
                self._build_fpu_multiply(self.rom_angle)
            elif opcode in ("BINARY_TRUE_DIVIDE", "BINARY_FLOOR_DIVIDE"):
                self._build_binary_divide(self.rom_angle)
            elif opcode == "BINARY_POWER":
                self._build_binary_power(self.rom_angle)
            elif opcode == "COMPARE_OP":
                self._build_compare_op(self.rom_angle, arg)
            elif opcode in ("POP_JUMP_IF_FALSE", "POP_JUMP_FORWARD_IF_FALSE", "POP_JUMP_BACKWARD_IF_FALSE"):
                self._build_pop_jump_if_false(self.rom_angle, arg)
            elif opcode in ("JUMP_FORWARD", "JUMP_ABSOLUTE"):
                self._build_jump(self.rom_angle, arg)
            elif opcode == "MAKE_FUNCTION":
                self._build_make_function(self.rom_angle)
            elif opcode in ("CALL_FUNCTION", "CALL", "CALL_METHOD"):
                self._build_call_function(self.rom_angle, arg)
            elif opcode in ("BUILD_LIST", "BUILD_MAP"):
                self._build_build_list(self.rom_angle, arg)
            elif opcode == "GET_ITER":
                self._build_get_iter(self.rom_angle)
            elif opcode == "FOR_ITER":
                self._build_for_iter(self.rom_angle, arg)
            elif opcode == "STORE_SUBSCR":
                self._build_store_subscr(self.rom_angle)
            elif opcode == "LOAD_SUBSCR":
                self._build_load_subscr(self.rom_angle)
            elif opcode == "POP_TOP":
                self._build_pop_top(self.rom_angle)
            elif opcode == "DUP_TOP":
                self._build_dup_top(self.rom_angle)
            elif opcode == "RETURN_VALUE":
                self._build_return(self.rom_angle)
            else:
                self.r2_rom.append({"position": self.rom_angle, "bitstring": get_bs(3, self.bitwidth), "comment": f"STUB: {opcode}"})

        return {
            "bitwidth": self.bitwidth,
            "operations": self.ops,
            "rings": [self.r0_halt, self.r1_ip, self.r2_rom, self.r3_stack, self.r4_heap, self.r5_fpu]
        }

    def _build_load_const(self, angle, const_val):
        self.r2_rom.append({"position": angle, "bitstring": get_bs(3, self.bitwidth)}) 
        self.static_sp_offset += 1

    def _build_store_name(self, angle, var_name):
        self.r2_rom.append({"position": angle, "bitstring": get_bs(1, self.bitwidth)})
        self.static_sp_offset -= 1
        
    def _build_load_name(self, angle, var_name):
        self.r2_rom.append({"position": angle, "bitstring": get_bs(3, self.bitwidth)})
        self.static_sp_offset += 1

    def _build_binary_add(self, angle):
        self.r2_rom.append({"position": angle, "bitstring": get_bs(1, self.bitwidth)})
        self.static_sp_offset -= 1

    def _build_binary_subtract(self, angle):
        self.r2_rom.append({"position": angle, "bitstring": get_bs(1, self.bitwidth)})
        self.static_sp_offset -= 1

    def _build_fpu_multiply(self, angle):
        self.r2_rom.append({"position": angle, "bitstring": get_bs(5, self.bitwidth)})
        self.static_sp_offset -= 1

    def _build_binary_divide(self, angle):
        self.r2_rom.append({"position": angle, "bitstring": get_bs(5, self.bitwidth)})
        self.static_sp_offset -= 1

    def _build_binary_power(self, angle):
        self.r2_rom.append({"position": angle, "bitstring": get_bs(5, self.bitwidth)})
        self.static_sp_offset -= 1

    def _build_compare_op(self, angle, op):
        self.r2_rom.append({"position": angle, "bitstring": get_bs(1, self.bitwidth)})
        self.static_sp_offset -= 1

    def _build_pop_jump_if_false(self, angle, target):
        self.r2_rom.append({"position": angle, "bitstring": get_bs(1, self.bitwidth)})
        self.static_sp_offset -= 1

    def _build_jump(self, angle, target):
        self.r2_rom.append({"position": angle, "bitstring": get_bs(6, self.bitwidth)})

    def _build_make_function(self, angle):
        self.r2_rom.append({"position": angle, "bitstring": get_bs(4, self.bitwidth)})

    def _build_call_function(self, angle, argc):
        if not isinstance(argc, int): argc = 0
        self.static_sp_offset -= argc

    def _build_build_list(self, angle, count):
        if not isinstance(count, int): count = 0
        self.static_sp_offset -= (count - 1)

    def _build_get_iter(self, angle):
        self.r2_rom.append({"position": angle, "bitstring": get_bs(4, self.bitwidth)})

    def _build_for_iter(self, angle, target):
        self.static_sp_offset += 1

    def _build_store_subscr(self, angle):
        self.static_sp_offset -= 3

    def _build_load_subscr(self, angle):
        self.static_sp_offset -= 1

    def _build_pop_top(self, angle):
        self.static_sp_offset -= 1

    def _build_dup_top(self, angle):
        self.static_sp_offset += 1

    def _build_return(self, angle):
        halt_angle = (angle + 1) % 360
        self.r2_rom.append({"position": halt_angle, "bitstring": get_bs(23, self.bitwidth), "value": 0})
        self.r3_stack.append({"position": 0, "bitstring": get_bs(23, self.bitwidth), "value": 0})

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(1)
    with open(sys.argv[1], 'r') as f: bytecode = json.load(f)
    synthesizer = CVMSynthesizer(bytecode)
    cvm_binary = synthesizer.synthesize()
    out_file = sys.argv[1].replace("_bytecode.json", "_cvm.json")
    with open(out_file, 'w') as f: json.dump(cvm_binary, f, indent=4)
    print(f">> Synthesized {out_file}")
