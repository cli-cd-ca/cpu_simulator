# Codecademy - CS104: Computer Architecture - Final Project
# CPU simulator that processes instructions and data values from parsed input files
# Assembler and CPU classes

from cpu_components import ControlUnit

# Assembler fetches and parses assembly instructions and data values and outputs machine code
class Assembler:
    def __init__(self, file):
        self.file = file
        self.lines = []
        self.register_idx_key = {"zero": 0, "at": 1, "v0": 2, "v1": 3, "a0": 4, "a1": 5, "a2": 6, "a3": 7, "t0": 8, "t1": 9, 
        "t2": 10, "t3": 11, "t4": 12, "t5": 13, "t6": 14, "t7": 15, "s0": 16, "s1": 17, "s2": 18, "s3": 19, "s4": 20, "s5": 21, 
        "s6": 22, "s7": 23, "t8": 24, "t9": 25, "k0": 26, "k1": 27, "gp": 28, "sp": 29, "fp": 30, "s8": 30, "ra": 31}
        
    def update_display(self, update, end):
        print(update, end=end)

    def input_file(self, file):
        self.file = file
        machine_code = self.parse()
        return machine_code

    def parse(self):
        machine_code = []
        with open(self.file, "r") as f:
            self.lines = f.readlines()
            self.update_display("\nAssembler parsing input:", "\n")
        
        for line in self.lines:
            self.update_display(line, "")
            instr = line.split(" ")

            # parse data values
            if len(instr[0]) == 8: # memory address
                if len(instr) == 2:
                    if "-" in instr[1]:
                        data = instr[1].split("-")
                        data = bin(int(instr[1]))[3:].zfill(8)
                        data = list(data)
                        data[0] = "1"
                        data = "".join(data)
                    else:
                        data = bin(int(instr[1]))[2:].zfill(8)
                    instr[1] = "".zfill(16)
                    instr.append(data)
                else:
                    instr.append("1".zfill(16)) # 0 means store data and 1 means retrieve data
                    instr.append("".zfill(8))
                machine_code.append("".join(instr))

            # parse instructions
            # MIPS32 ISA except NOT, NAND, XNOR, HALT additions
            elif instr[0] in ("ADD", "SUB", "MUL", "SLT", "SLL", "SRA", "AND", "OR", "XOR", "NOT", "NAND", "NOR", "XNOR", "HALT"):
                if instr[0] == "ADD":   
                    func_code = "100000" 
                elif instr[0] == "SUB":
                    func_code = "100010"
                elif instr[0] == "MUL":
                    func_code = "000010"
                elif instr[0] == "SLT":
                    func_code = "101010"
                elif instr[0] == "SLL":
                    func_code = "000000"
                elif instr[0] == "SRA":
                    func_code = "000011"
                elif instr[0] == "AND":
                    func_code = "100100"
                elif instr[0] == "OR":
                    func_code = "100101"
                elif instr[0] == "XOR":
                    func_code = "100110"
                elif instr[0] == "NOT":
                    func_code = "111001"
                elif instr[0] == "NAND":
                    func_code = "101001"
                elif instr[0] == "NOR":
                    func_code = "100111"
                elif instr[0] == "XNOR":
                    func_code = "101101"
                elif instr[0] == "HALT": 
                    func_code = "111111"
                
                if instr[0] in ("ADD", "SUB", "MUL", "SLT", "SLL", "SRA", "AND", "OR", "XOR", "NOT", "NAND", "NOR", "XNOR"):
                    instr[1] = instr[1].split(",")[0]
                    instr[2] = instr[2].split(",")[0]
                    rd = bin(self.register_idx_key[instr[1].split("$")[1]])[2:].zfill(5)
                    if instr[0] != "NOT":
                        if "\n" in instr[3]:
                            instr[3] = instr[3].split("\n")[0]
                    if instr[0] in ("ADD", "SUB", "MUL", "SLT", "AND", "OR", "XOR", "NAND", "NOR", "XNOR"):
                        rs = bin(self.register_idx_key[instr[2].split("$")[1]])[2:].zfill(5)
                        rt = bin(self.register_idx_key[instr[3].split("$")[1]])[2:].zfill(5)
                        instr[1] = rs
                        instr.append("00000")
                    elif instr[0] in ("SLL", "SRA", "NOT"):
                        rt = bin(self.register_idx_key[instr[2].split("$")[1]])[2:].zfill(5)
                        instr[1] = "00000"
                        if instr[0] != "NOT":
                            sa = bin(self.register_idx_key[instr[3].split("$")[1]])[2:].zfill(5)
                            instr.append(sa)
                        else:
                            instr.append("00000")
                    instr[2] = rt
                    instr[3] = rd

                elif instr[0] == "HALT":
                    zero_extd = instr[1].replace(";", "0").zfill(20)
                    instr[1] = zero_extd
                
                if instr[0] == "MUL":
                    instr[0] = "011100"
                else:
                    instr[0] = "000000"

                instr.append(func_code)
                machine_code.append("".join(instr))

            elif instr[0] == "ADDI":
                instr[0] = "001000"
                rt = bin(self.register_idx_key[instr[1].split(",")[0].split("$")[1]])[2:].zfill(5)
                rs = bin(self.register_idx_key[instr[2].split(",")[0].split("$")[1]])[2:].zfill(5)
                imd = bin(int(instr[3]))[2:].zfill(16)
                instr[1] = rs
                instr[2] = rt
                instr[3] = imd
                machine_code.append("".join(instr))

            elif instr[0] == "BNE":
                instr[0] = "000101"
                rs = bin(self.register_idx_key[instr[1].split("$")[1]])[2:].zfill(5)
                rt = bin(self.register_idx_key[instr[2].split("$")[1]])[2:].zfill(5)
                ofs = bin(int(instr[3]))[2:].zfill(16)
                instr[1] = rs
                instr[2] = rt
                instr[3] = ofs
                machine_code.append("".join(instr))

            elif instr[0] in ("J", "JAL"):
                if instr[0] == "J":
                    instr[0] = "000010"
                elif instr[0] == "JAL":
                    instr[0] = "000011"
                instr_idx = bin(int(instr[1]))[2:].zfill(26)
                instr[1] = instr_idx
                machine_code.append("".join(instr))

            elif instr[0] in ("LW", "SW"):
                if instr[0] == "LW":
                    instr[0] = "100011"
                elif instr[0] == "SW":
                    instr[0] = "101011"
                rt = bin(self.register_idx_key[instr[1].split(",")[0].split("$")[1]])[2:].zfill(5) 
                ofs_base = instr[2].split("(")
                ofs = bin(int(ofs_base[0]))[2:].zfill(16)
                base = ofs_base[1].split(")")[0]
                base = bin(self.register_idx_key[base.split("$")[1]])[2:].zfill(5)
                instr[1] = base
                instr[2] = rt
                instr.append(ofs)
                machine_code.append("".join(instr))
                
            elif instr[0] == "CACHE":
                instr[0] = "101111"
                op = bin(int(instr[1]))[2:].zfill(5)
                instr[1] = "00000"
                instr.append(op)
                instr.append("".zfill(16))
                machine_code.append("".join(instr))

        self.update_display("\n\nAssembler output:", "\n")
        for line in machine_code:
            self.update_display(line, "\n")

        return machine_code

# CPU processes input machine code instructions through a control unit, arithmetic logic unit, registers, and memory bus access to cache and main memory 
class CPU:
    def __init__(self, machine_code):
        self.machine_code = machine_code
        self.control_unit = ControlUnit(machine_code)

        self.update_display("\nCPU input:", "\n")
        for line in machine_code:
            self.update_display(line, "\n")

    def __repr__(self):
        cpu = f"\nCentral Processing Unit (CPU)\n\nMemory Address Register: {self.control_unit.memory_address_reg}\nMemory Data Register: {self.control_unit.memory_data_reg}\n{self.control_unit}\n{self.control_unit.ALU}\n{self.control_unit.registers}"
        return cpu
    
    def update_display(self, update, end):
        print(update, end=end)

assembler = Assembler('data_instruction_input.txt')
machine_code1 = assembler.parse()
machine_code2 = assembler.input_file('data_input.txt')
machine_code3 = assembler.input_file('instruction_input.txt')
CPU = CPU(machine_code1)
CPU.control_unit.memory_bus.store_retrieve_data(machine_code2)
print(CPU.control_unit.memory_bus)
print(CPU.control_unit.memory_bus.main_memory)
CPU.control_unit.memory_bus.store_instructions(machine_code1)
print(CPU.control_unit.memory_bus)
print(CPU.control_unit.memory_bus.main_memory)
CPU.control_unit.fetch_instruction()
print(CPU.control_unit.memory_bus)
print(CPU.control_unit.registers)
CPU.control_unit.input_machine_code(machine_code3)
CPU.control_unit.memory_bus.store_instructions(machine_code3)
print(CPU.control_unit.memory_bus)
print(CPU.control_unit.memory_bus.main_memory)
CPU.control_unit.fetch_instruction()
print(CPU.control_unit.memory_bus)
print(CPU.control_unit.memory_bus.cache_memory)
print(CPU)