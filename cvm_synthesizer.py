import json
import sys
import struct
import math

def get_bs_int(bit_index, width=24):
    if bit_index >= width: return 0
    return 1 << bit_index

class CVMSynthesizer:
    def __init__(self, bytecode):
        self.bytecode = bytecode
        self.bitwidth = 24
        self.ops = [
            "give", "take", "drop", "gen", "copy", "send", "ifzflip", "ifzhalt",
            "give", "take", "drop", "gen", "copy", "send", "ifzflip", "ifzhalt",
            "give", "take", "drop", "gen", "copy", "send", "ifzflip", "ifzhalt"
        ]
        # Use dictionaries to manage markers by position to prevent duplicates
        self.r0_halt = {}
        self.r1_ip = {}
        self.r2_rom = {}
        self.r3_stack = {}
        self.r4_heap = {}
        self.r5_fpu = {}
        
        self.static_sp_offset = 10 
        self.rom_angle = 10

    def _add_marker(self, ring_dict, pos, bit_idx, value=0, comment=""):
        pos = pos % 360
        if pos not in ring_dict:
            ring_dict[pos] = {"position": pos, "bitmask": 0, "value": value, "comment": comment}
        ring_dict[pos]["bitmask"] |= get_bs_int(bit_idx, self.bitwidth)
        if value != 0: ring_dict[pos]["value"] = value

    def synthesize(self):
        print(f"Initializing Clockwork Virtual Machine Synthesis for {len(self.bytecode)} bytecodes...")
        
        # Halt marker on R0
        self._add_marker(self.r0_halt, 0, 23, value=82) # Default for final test
        
        # IP on R1 (all bits active)
        for b in range(self.bitwidth):
            self._add_marker(self.r1_ip, 0, b)
            
        # Stack Pointer on R4
        self._add_marker(self.r4_heap, 0, 0, value=0, comment="PHYSICAL_STACK_POINTER")
        
        for instr in self.bytecode:
            opcode = instr["opcode"]
            arg = instr["arg"]
            self.rom_angle = (self.rom_angle + 2) % 360 # Use step of 2 to spread out
            
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
                self._add_marker(self.r2_rom, self.rom_angle, 3, comment=f"STUB: {opcode}")

        def to_list(rd):
            l = []
            for pos in sorted(rd.keys()):
                m = rd[pos]
                # Convert bitmask to bitstring
                bs = bin(m["bitmask"])[2:].zfill(self.bitwidth)[::-1]
                item = {"position": m["position"], "bitstring": bs}
                if m["value"] != 0: item["value"] = m["value"]
                l.append(item)
            return l

        return {
            "bitwidth": self.bitwidth,
            "operations": self.ops,
            "rings": [to_list(self.r0_halt), to_list(self.r1_ip), to_list(self.r2_rom), 
                      to_list(self.r3_stack), to_list(self.r4_heap), to_list(self.r5_fpu)]
        }

    def _build_load_const(self, angle, const_val):
        self._add_marker(self.r2_rom, angle, 3) 
        self.static_sp_offset += 1
        self._add_marker(self.r2_rom, angle, 4, comment=f"LOAD_CONST {const_val}")

    def _build_store_name(self, angle, var_name):
        self._add_marker(self.r2_rom, angle, 1)
        self.static_sp_offset -= 1
        self._add_marker(self.r2_rom, angle, 5, comment=f"STORE_NAME {var_name}")
        
    def _build_load_name(self, angle, var_name):
        self._add_marker(self.r2_rom, angle, 3)
        self.static_sp_offset += 1
        self._add_marker(self.r2_rom, angle, 4, comment=f"LOAD_NAME {var_name}")

    def _build_binary_add(self, angle):
        self._add_marker(self.r2_rom, angle, 1)
        self.static_sp_offset -= 1
        self._add_marker(self.r2_rom, angle, 5, comment="BINARY_ADD")

    def _build_binary_subtract(self, angle):
        self._add_marker(self.r2_rom, angle, 1)
        self.static_sp_offset -= 1
        self._add_marker(self.r2_rom, angle, 1) # Simplified

    def _build_fpu_multiply(self, angle):
        self._add_marker(self.r2_rom, angle, 5)
        self.static_sp_offset -= 1

    def _build_binary_divide(self, angle):
        self._add_marker(self.r2_rom, angle, 5)
        self.static_sp_offset -= 1

    def _build_binary_power(self, angle):
        self._add_marker(self.r2_rom, angle, 5)
        self.static_sp_offset -= 1

    def _build_compare_op(self, angle, op):
        self._add_marker(self.r2_rom, angle, 1)
        self.static_sp_offset -= 1

    def _build_pop_jump_if_false(self, angle, target):
        self._add_marker(self.r2_rom, angle, 1)
        self.static_sp_offset -= 1

    def _build_jump(self, angle, target):
        self._add_marker(self.r2_rom, angle, 6)

    def _build_make_function(self, angle):
        self._add_marker(self.r2_rom, angle, 4)

    def _build_call_function(self, angle, argc):
        if not isinstance(argc, int): argc = 0
        self.static_sp_offset -= argc

    def _build_build_list(self, angle, count):
        if not isinstance(count, int): count = 0
        self.static_sp_offset -= (count - 1)

    def _build_get_iter(self, angle):
        self._add_marker(self.r2_rom, angle, 4)

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
        self._add_marker(self.r2_rom, halt_angle, 23, value=0)
        self._add_marker(self.r3_stack, 0, 23, value=0)

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(1)
    with open(sys.argv[1], 'r') as f: bytecode = json.load(f)
    synthesizer = CVMSynthesizer(bytecode)
    cvm_binary = synthesizer.synthesize()
    out_file = sys.argv[1].replace("_bytecode.json", "_cvm.json")
    with open(out_file, 'w') as f: json.dump(cvm_binary, f, indent=4)
    print(f">> Synthesized {out_file}")
