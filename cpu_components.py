# Codecademy - CS104: Computer Architecture - Final Project
# Control unit, registers, and ALU classes

from memory import Memory, MemoryBus

# Control unit operates the fetch-decode-execute cycle of instructions within the CPU
class ControlUnit:
    def __init__(self, machine_code):
        self.machine_code = machine_code
        self.instruction_reg = "" # current 32-bit instruction
        self.program_counter = 0 # memory address of next instruction
        self.memory_address_reg = 0 # memory address of data to retrieve or store in memory
        self.memory_data_reg= "" # data retrieved from or to be stored in memory
        self.ALU = ALU()
        self.registers = Registers()
        self.memory_bus = MemoryBus()
        self.cache_on = False

    def __repr__(self):
        CU = f"\nControl Unit\nInstruction Register: {self.instruction_reg}\nProgram Counter: {bin(self.program_counter)[2:].zfill(8)}"
        return CU

    def update_display(self, update, end):
        print(update, end=end)

    def input_machine_code(self, machine_code):
        self.machine_code = machine_code
        self.update_display("\nCPU input:", "\n")
        for line in machine_code:
            self.update_display(line, "\n")

    def adjust_program_counter(self, pc):
        if pc > 63:
            value = pc - 63
            pc = -1 + value
        return pc

    def set_program_counter(self, value):
        pc = self.adjust_program_counter(self.program_counter + value)
        self.program_counter = pc

    def read_memory(self, name, address):
        data = name.read_memory(address)
        return data

    def write_memory(self, name, address, data):
        name.write_memory(address, data)

    def fetch_instruction(self):
        value = -1
        delay = 0
        link_pc = -1
        for i in range(len(self.machine_code)):
            instr = []
            self.update_display(f"\nCPU program counter: {bin(self.program_counter)[2:].zfill(8)}", "\n")
            for j in range(4): # fetches instruction from cache or main memory
                pc = self.adjust_program_counter(self.program_counter + j)
                if self.cache_on and j == 0:
                    self.memory_address_reg = bin(pc)[2:].zfill(8)
                    self.memory_bus.address_bus = self.memory_address_reg
                    memory = self.memory_bus.main_memory.cache_memory_on(self.program_counter)
                    self.memory_bus.cache_memory.cache_memory_on(memory)
                    self.update_display(f"CPU fetching instruction from cache memory", "\n")
                    self.memory_bus.data_bus = self.memory_bus.cache_memory.read_memory(pc)
                    self.memory_data_reg = self.memory_bus.data_bus
                    instr.append(self.memory_data_reg)
                elif self.cache_on and j > 0:
                    self.memory_address_reg = bin(pc)[2:].zfill(8)
                    self.memory_bus.address_bus = self.memory_address_reg
                    self.memory_bus.data_bus = self.memory_bus.cache_memory.read_memory(pc)
                    self.memory_data_reg = self.memory_bus.data_bus
                    instr.append(self.memory_data_reg)
                elif not self.cache_on and j == 0:
                    self.memory_address_reg = bin(pc)[2:].zfill(8)
                    self.memory_bus.address_bus = self.memory_address_reg
                    self.update_display(f"CPU fetching instruction from main memory", "\n")
                    self.memory_bus.data_bus = self.memory_bus.main_memory.read_memory(pc)
                    self.memory_data_reg = self.memory_bus.data_bus
                    instr.append(self.memory_data_reg)
                else:
                    self.memory_address_reg = bin(pc)[2:].zfill(8)
                    self.memory_bus.address_bus = self.memory_address_reg
                    self.memory_bus.data_bus = self.memory_bus.main_memory.read_memory(pc)
                    self.memory_data_reg = self.memory_bus.data_bus
                    instr.append(self.memory_data_reg)
            self.instruction_reg = "".join(instr)
            self.update_display(f"CPU instruction register: {self.instruction_reg}", "\n")
            self.set_program_counter(4) # increments program counter to point to next instruction

            value, link_pc = self.decode_execute_instruction(self.instruction_reg, value, link_pc)
            if value != -1:
                if delay == 1:
                    value -= 4
                    self.set_program_counter(value) # increments program counter for jump and branch instructions
                    if link_pc != -1:
                        self.write_memory(self.registers, 31, link_pc)
                        link_pc = -1
                    value = -1
                    delay = 0
                else:
                    delay = 1
            self.update_display(f"CPU program counter: {bin(self.program_counter)[2:].zfill(8)}", "\n")

    def decode_execute_instruction(self, instruction, value, link_pc):
        opcode = instruction[:6]
        if opcode in ("000000","001000","000101", "011100"):
            if instruction[26:] not in ("111111","000000","000011","111001"):
                rs = int(instruction[6:11], 2)
                rt = int(instruction[11:16], 2)
                a = self.read_memory(self.registers, rs)
                if opcode in ("000000", "011100"):
                    b = self.read_memory(self.registers, rt)
                    rd = int(instruction[16:21], 2)
                    func_code = instruction[26:]
                    result = self.ALU.op(opcode, a, b, func_code=func_code)
                    self.write_memory(self.registers, rd, result)
                elif opcode == "001000":
                    imd = list(bin(int(instruction[16:], 2))[2:])
                    imd.insert(0, "0")
                    result = self.ALU.op(opcode, a, "".join(imd))
                    self.write_memory(self.registers, rt, result)
                elif opcode == "000101":
                    b = self.read_memory(self.registers, rt)
                    ofs = instruction[16:]
                    result = self.ALU.op(opcode, a, b)
                    if result == 0:
                        value = int(self.ALU.op("000000", ofs, func_code="000000", shift=2), 2)
                        pc = self.adjust_program_counter(self.program_counter + value)
                        self.update_display(f"CPU program counter branching to main memory address {pc}", "\n")
            elif instruction[26:] in ("000000","000011","111001"):
                rt = int(instruction[11:16], 2)
                rd = int(instruction[16:21], 2)
                func_code = instruction[26:]
                a = self.read_memory(self.registers, rt)
                if instruction[26:] in ("000000","000011"):
                    sa = int(instruction[21:26], 2)
                    result = self.ALU.op(opcode, a, func_code=func_code, shift=sa)
                else:
                    result = self.ALU.op(opcode, a, func_code=func_code)
                self.write_memory(self.registers, rd, result)
            elif instruction[26:] == "111111":
                self.update_display("CPU terminating execution", "\n")

        elif opcode in ("100011", "101011", "101111"):
            base = int(instruction[6:11], 2)
            ofs = int(instruction[16:], 2)
            ofs_base = base + ofs
            if opcode in ("100011", "101011"):
                rt = int(instruction[11:16], 2)
            if opcode == "100011":
                if self.cache_on:
                    memory = self.memory_bus.main_memory.cache_memory_on(ofs_base, "lw")
                    tag = self.memory_bus.cache_memory.cache_memory_on(memory, "sw")
                    self.memory_address_reg = bin(tag)[2:].zfill(8)
                    self.memory_bus.address_bus = self.memory_address_reg
                    result = self.read_memory(self.memory_bus.cache_memory, tag)
                else:
                    self.memory_address_reg = bin(ofs_base)[2:].zfill(8)
                    self.memory_bus.address_bus = self.memory_address_reg
                    result = self.read_memory(self.memory_bus.main_memory, ofs_base)
                self.memory_bus.data_bus = result
                self.memory_data_reg = result
                self.write_memory(self.registers, rt, result)
            elif opcode == "101011":
                result = self.read_memory(self.registers, rt)
                self.memory_data_reg = result
                self.memory_bus.data_bus = self.memory_data_reg
                if self.cache_on:
                    self.memory_address_reg = bin(self.memory_bus.cache_memory.memory_idx + 1)[2:].zfill(8)
                    self.memory_bus.address_bus = self.memory_address_reg
                    self.write_memory(self.memory_bus.cache_memory, self.memory_bus.cache_memory.memory_idx+1, result)
                else:
                    self.memory_address_reg = bin(ofs_base)[2:].zfill(8)
                    self.memory_bus.address_bus = self.memory_address_reg
                    self.write_memory(self.memory_bus.main_memory, ofs_base, result)
            elif opcode == "101111":
                op = int(instruction[11:16], 2)
                if op == 0:
                    self.cache_on = False
                    self.memory_bus.cache_memory.cache_on = False
                    self.update_display("CPU cache memory off", "\n")
                elif op == 1:
                    self.cache_on = True
                    self.memory_bus.cache_memory.cache_on = True
                    self.update_display("CPU cache memory on", "\n")
                elif op == 2:
                    self.memory_bus.cache_memory.memory = [""] * 4
                    self.update_display("CPU cache memory flush", "\n")

        elif opcode in ("000010", "000011"):
            instr_idx = instruction[6:]
            pc = self.adjust_program_counter(int(self.ALU.op("000000", instr_idx, func_code="000000", shift=2).zfill(32), 2))
            value = pc - self.program_counter
            self.update_display(f"CPU program counter jumping to main memory address {pc}", "\n")
            if opcode == "000011":
                link_pc = self.adjust_program_counter(pc + 8)
        
        return value, link_pc

# Registers inherit memory class to read and write to CPU registers
class Registers(Memory):
    def __init__(self):
        super().__init__("Registers", [""] * 32, 1, 31)
        self.memory[0] = "0"

    def __repr__(self):
        return super().__repr__()

    def update_display(self, update, end):
        super().update_display(update, end)

    def set_max_idx(self, idx):
        self.max_idx = idx

    def adjust_register_idx(self, idx):
        return super().adjust_memory_idx(idx)

    def set_register_idx(self, value):
        super().set_memory_idx(value)

    def read_memory(self, address):
        self.update_display(f"CPU reading from register {str(address)}: {self.memory[address]}", "\n")
        return super().read_memory(address)

    def write_memory(self, address, data):
        super().write_memory(address, data)
        self.update_display(f"CPU writing to register {str(address)}: {data}", "\n")

# ALU performs arithmetic, bitwise logic, comparison, and shift operations to execute CPU instructions
class ALU:
    def __init__(self):
        self.accumulator_reg = "" # holds data values for ALU operations and results from ALU arithmethic or shift operations

    def __repr__(self):
        alu = f"\nArithmetic Logic Unit\nAccumulator Register: {self.accumulator_reg.zfill(32)}"
        return alu

    def AND_gate_(self, a, b):
        if a == 0 or b == 0:
            return 0
        return 1

    def OR_gate_(self, a, b):
        if a == 0 and b == 0:
            return 0
        return 1
    
    def XOR_gate_(self, a, b):
        if a == b:
            return 0
        return 1

    def NOT_gate_(self, a):
        if a == 1:
            return 0
        return 1
    
    def AND_gate(self, a, b):
        a_b = []
        bin2 = len(b)-1
        for bin1 in range(len(a)-1,-1,-1):
            if a[bin1] == "0" or b[bin2] == "0":
                a_b.insert(0, "0")
            else:
                a_b.insert(0, "1")
            bin2 -= 1
        a_b = "".join(a_b)
        return a_b

    def OR_gate(self, a, b):
        a_b = []
        bin2 = len(b)-1
        for bin1 in range(len(a)-1,-1,-1):
            if a[bin1] == "0" and b[bin2] == "0":
                a_b.insert(0, "0")
            else:
                a_b.insert(0, "1")
            bin2 -= 1
        a_b = "".join(a_b)
        return a_b

    def XOR_gate(self, a, b):
        a_b = []
        bin2 = len(b)-1
        for bin1 in range(len(a)-1,-1,-1):
            if a[bin1] == b[bin2]:
                a_b.insert(0, "0")
            else:
                a_b.insert(0, "1")
            bin2 -= 1
        a_b = "".join(a_b)
        return a_b

    def NOT_gate(self, a):
        a_lst = []
        for bin1 in range(len(a)-1,-1,-1):
            if a[bin1] == "1":
                a_lst.insert(0, "0")
            else:
                a_lst.insert(0, "1")
        a = "".join(a_lst)
        return a
    
    def NAND_gate(self, a, b):
        return self.NOT_gate(self.AND_gate(a, b))

    def NOR_gate(self, a, b):
        return self.NOT_gate(self.OR_gate(a, b))

    def XNOR_gate(self, a, b):
        return self.NOT_gate(self.XOR_gate(a, b))

    def _2s_complement(self, total):
        for i in range(len(total)):
            total[i] = str(self.NOT_gate_(int(total[i])))
        total = list(self.full_adder("".join(total), "01", 0))
        total[0] = "1"
        return total
        
    def half_adder(self, a, b):
        s = self.XOR_gate_(a, b)
        c = self.AND_gate_(a, b)
        return (s, c)

    def half_subt(self, a, b):
        d = self.XOR_gate_(a, b)
        brw = 0
        if a == 0 and b == 1:
            brw = 1
        return (d, brw)

    def left_shift(self, a, shift):
        a = list(a)
        for s in range(shift):
            a.pop(0)
            a.insert(-1, "0")
        a = "".join(a)
        self.accumulator_reg = a
        return self.accumulator_reg

    def arith_right_shift(self, a, shift):
        a = list(a)
        for s in range(shift):
            a.pop()
            a.insert(0, a[0])
        a = "".join(a)
        self.accumulator_reg = a
        return self.accumulator_reg

    def less_than(self, a, b):
        if a[0] == "1" and b[0] == "0" and a != "10":
            return 1
        elif b[0] == "1" and a[0] == "0":
            return 0
        a = list(a)
        b = list(b)
        bin2 = 2
        for bin1 in range(2, len(a)):
            if a[bin1] < b[bin2] and a[0] == "0" and b[0] == "0":
                return 1
            elif b[bin2] < a[bin1] and a[0] == "1" and b[0] == "1":
                return 1
            else:
                bin2 -= 1
        return 0

    def not_equal(self, a, b):
        if len(a) != len(b):
            return 1
        a = list(a)
        b = list(b)
        bin2 = 0
        for bin1 in range(len(a)):
            if a[bin1] == b[bin2]:
                bin2 += 1
                continue
            return 1
        return 0

    def full_adder(self, a, b, c):
        s_total = []
        a = list(a)
        b = list(b)
        a_s = a[0]
        b_s = b[0]
        a.pop(0)
        b.pop(0)
        if len(a) < len(b):
            a, b = b, a
        bin2 = len(b)-1
        for bin1 in range(len(a)-1,-1,-1):
            s, c_out1 = self.half_adder(int(a[bin1]), int(b[bin2]))
            s, c_out2 = self.half_adder(c, s)
            c = self.OR_gate_(c_out1, c_out2)
            s_total.insert(0, str(s))
            if bin2 > 0:
                bin2 -= 1
            elif bin2 == 0:
                b.insert(0, 0)
        if c == 1:
            s_total.insert(0, str(c))
        if a_s == "1" and b_s == "1":
            s_total.insert(0, "0")
            s_total = self._2s_complement(s_total)
        else:
            s_total.insert(0, "0")
        s = "".join(s_total)
        self.accumulator_reg = s
        return self.accumulator_reg    

    def full_subt(self, a, b):
        d_total = []
        s = "0"
        if int(a) < int(b):
            a, b = b, a
            s = "1"
        a = list(a)
        b = list(b)
        a.pop(0)
        b.pop(0)
        bin2 = len(b)-1
        for bin1 in range(len(a)-1,-1,-1):
            d, brw = self.half_subt(int(a[bin1]), int(b[bin2]))
            d_total.insert(0, str(d))
            if brw == 1:
                for bin3 in range(bin1,-1,-1):
                    if a[bin3-1] == "0":
                        a[bin3-1] = 1
                    elif a[bin3-1] == "1":
                        a[bin3-1] = 0
                        break
            if bin2 > 0:
                bin2 -= 1
            elif bin2 == 0:
                b.insert(0, "0")
        while d_total[0] == "0":
            d_total.pop(0)
        if s == "1":
            s = "0"
            d_total.insert(0, s)
            d_total = self._2s_complement(d_total)
        d = "".join(d_total)
        self.accumulator_reg = d
        return self.accumulator_reg

    def multpl(self, a, b):
        p_total = []
        p_s = "0"
        a_s = a[0]
        b_s = b[0]
        if a_s == b_s:
            if a_s == "1":
                a_s = "0"
                b_s = "0"
        if a_s != b_s:
            if a_s == "1":
                a_s = "0"
            else:
                b_s = "0"
            p_s = "1"
        a = a[1:]
        b = b[1:]
        if int(a, 2) > int(b, 2):
            multiplier = b
        else:
            multiplier = a
        if multiplier == b:
            a = a_s + a
            if int(multiplier, 2) % 2 == 0:
                for i in range(0, int(multiplier, 2), 2):
                    p_total.append(self.full_adder(a, a, 0))
            else:
                for i in range(0, int(multiplier, 2)-1, 2):
                    p_total.append(self.full_adder(a, a, 0))
                p_total.append(a)
            while len(p_total) > 1: 
                p_total.insert(0, self.full_adder(p_total[0], p_total[1], 0))
                p_total.pop(1)
                p_total.pop(1)
        elif multiplier == a:
            if multiplier % 2 == 0:
                for i in range(0, multiplier, 2):
                    p_total.append(self.full_adder(b, b, 0))
            else:
                for i in range(0, multiplier, 2):
                    p_total.append(self.full_adder(b, b, 0))
                p_total.append(b)
            while len(p_total) > 1: 
                p_total.insert(0, self.full_adder(p_total[0], p_total[1], 0))
                p_total.pop(1)
                p_total.pop(1)
        if p_s == "1":
            p_total = self._2s_complement(list(p_total[0]))
        p = "".join(p_total)
        self.accumulator_reg = p
        return self.accumulator_reg

    def op(self, opcode, a, b=0, c=0, func_code="000000", shift=1):
        if b:
            self.accumulator_reg = b.zfill(8) + a.zfill(8)
        elif shift:
            self.accumulator_reg = bin(shift)[2:].zfill(8) + a.zfill(8)
        else:
            self.accumulator_reg = a.zfill(8)
        if opcode in ("000000","001000", "011100"):
            if func_code == "100000" or opcode == "001000":
                return self.full_adder(a, b, c)
            elif func_code == "100010":
                return self.full_subt(a, b)
            elif func_code == "000010":
                return self.multpl(a, b)
            elif func_code == "101010":
                return self.less_than(a, b)
            elif func_code == "100100":
                return self.AND_gate(a, b)
            elif func_code == "100101":
                return self.OR_gate(a, b)
            elif func_code == "100110":
                return self.XOR_gate(a, b)
            elif func_code == "111001":
                return self.NOT_gate(a)
            elif func_code == "101001":
                return self.NAND_gate(a, b)
            elif func_code == "100111":
                return self.NOR_gate(a, b)
            elif func_code == "101101":
                return self.XNOR_gate(a, b)
            elif func_code == "000000":
                return self.left_shift(a, shift)
            elif func_code == "000011":
                return self.arith_right_shift(a, shift)
        elif opcode == "000101":
            return self.not_equal(a, b)