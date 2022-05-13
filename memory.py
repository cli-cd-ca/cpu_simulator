# Codecademy - CS104: Computer Architecture - Final Project
# Parent memory, cache memory, main memory, and memory bus classes

# Parent memory class
class Memory:
    def __init__(self, name, memory, memory_idx, max_idx):
        self.name = name
        self.memory = memory
        self.memory_idx = memory_idx
        self.max_idx = max_idx

    def __repr__(self):
        memory = f"\n{self.name}\n{self.memory}"
        return memory

    def update_display(self, update, end):
        print(update, end=end)

    def adjust_memory_idx(self, idx):
        if idx > self.max_idx:
            value = idx - self.max_idx
            idx = -1 + value
        return idx

    def set_memory_idx(self, value):
        idx = self.adjust_memory_idx(self.memory_idx + value)
        self.memory_idx = idx

    def read_memory(self, address, memory="main_reg"):
        if memory == "cache":
            data = self.memory[self.memory_idx][address]
            self.set_memory_idx(1)
            return data
        return self.memory[address]

    def write_memory(self, address, data, memory="main_reg"):
        if memory == "cache":
            self.memory[self.memory_idx][address] = data
            self.set_memory_idx(1)
        else:
            self.memory[address] = data

# Cache memory inherits memory class to read and write cache memory     
class CacheMemory(Memory):
    def __init__(self):
        super().__init__("Cache Memory", [{}] * 4, 0, 3)
        self.cache_on = False

    def __repr__(self):
        return super().__repr__()

    def update_display(self, update, end):
        super().update_display(update, end)

    def adjust_cache_memory_tag(self, idx):
        return super().adjust_memory_idx(idx)

    def set_cache_memory_tag(self, value):
        super().set_memory_idx(value)

    def cache_memory_on(self, memory_lst, op="0"):
        if op in ("sw"):
            i = self.adjust_cache_memory_tag(self.memory_idx+1)
            self.memory[i][memory_lst[0][0]] = memory_lst[0][1]
        else:
            for i in range(4):
                self.memory[self.memory_idx+i] = {memory_lst[i][0]:memory_lst[i][1]}
        return i

    def read_memory(self, address):
        if self.cache_on:
            if self.memory[self.memory_idx][address]:
                self.update_display(f"CPU reading cache memory tag {str(address)} - HIT: {self.memory[self.memory_idx][address]}", "\n")
            else:
                self.update_display(f"CPU reading cache memory tag {str(address)} - MISS", "\n")
            return super().read_memory(address, "cache")
        else:
            self.update_display(f"CPU cache memory off", "\n")

    def write_memory(self, address, data):
        super().write_memory(address, data, "cache")
        self.update_display(f"CPU writing to cache memory tag {str(address)}: {data}", "\n")

# Main memory inherits memory class to read and write main memory and send memory to cache
class MainMemory(Memory):
    def __init__(self):
        super().__init__("Main Memory", [""] * 64, 0, 63)

    def __repr__(self):
        return super().__repr__()

    def update_display(self, update, end):
        super().update_display(update, end)

    def adjust_main_memory_idx(self, idx):
        return super().adjust_memory_idx(idx)

    def set_main_memory_idx(self, value):
        super().set_memory_idx(value)

    def cache_memory_on(self, pc, op="0"):
        self.memory_idx = pc
        memory = []
        if op == "lw":
            memory.append(self.memory[self.memory_idx])
        else:
            for i in range(4):
                i = self.adjust_main_memory_idx(pc+i)
                memory.append([i, self.memory[i]])
        return memory

    def read_memory(self, address):
        if self.memory[address]:
            self.update_display(f"CPU reading from main memory address {str(address)}: {self.memory[address]}", "\n")
        else:
            self.update_display(f"CPU reading from main memory address {str(address)}: no data at address {str(address)}", "\n")
        return super().read_memory(address)

    def write_memory(self, address, data, op="0"):
        super().write_memory(address, data)
        if op == "instr":
            self.update_display(f"Main memory storing instruction at address {str(address)}: {data}", "\n")
        else:
            self.update_display(f"CPU writing to main memory address {str(address)}: {data}", "\n")

# Memory bus connects the CPU to main and cache memory, stores instruction and data value input, and retrieves data
class MemoryBus:
    def __init__(self):
        self.main_memory = MainMemory()
        self.cache_memory = CacheMemory()
        self.address_bus = 0 # memory address where data will be stored or retrieved
        self.data_bus = "" # data to be stored or retrieved

    def __repr__(self):
        memory_bus = f"\nMemory Bus\nAddress Bus: {self.address_bus}\nData Bus: {self.data_bus}"
        return memory_bus

    def update_display(self, update, end):
        print(update, end=end)

    def store_instructions(self, machine_code):
        for line in machine_code:
            self.update_display(f"\nMemory Bus: {line}", "\n")
            idx_lst = []
            for i in range(4):
                idx = self.main_memory.adjust_main_memory_idx(self.main_memory.memory_idx + i)
                idx_lst.append(idx)
            for i in range(4):
                self.address_bus = bin(idx_lst[i])[2:].zfill(8)
                self.data_bus = line[8*i:8*(i+1)]
                self.main_memory.write_memory(int(self.address_bus, 2), self.data_bus, "instr")
            self.main_memory.set_main_memory_idx(4)

    def store_retrieve_data(self, machine_code):
        for line in machine_code:
            self.update_display(f"\nMemory bus: {line}", "\n")
            address = int(line[:8], 2)
            self.address_bus = bin(address)[2:].zfill(8)
            if line[23] == "0":
                data = line[24:]
                self.data_bus = data
                self.update_display(f"Main memory storing data at address {address}: {data}", "\n")
                self.main_memory.memory[address] = data
            elif line[23] == "1":
                data = self.main_memory.memory[address]
                self.data_bus = data
                self.update_display(f"Main memory retrieving data from address {address}: {data}", "\n")