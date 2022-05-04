# CPU Simulator

I made a CPU simulator that processes instructions and data values using a MIPS32 instruction set architecture. The assembler class parses assembly language 
input files and outputs machine code. The CPU class takes machine code and sends it to the control unit by initializing a control unit instance within the 
class. The control unit class contains instances of the CPU's arithmetic logic unit (ALU), registers, and memory bus to access main and cache memory. This is so 
the control unit can direct the fetch-decode-execute cycle of CPU instructions. 

The control unit class contains four registers that facilitate the instruction cycle: 
- the instruction register holds the current instruction
- the program counter points to the next instruction in memory
- the memory address register holds the address in memory to be accessed for data storage or retrieval
- the memory data register holds data retrieved from or to be stored in memory. 

The ALU class contains another CPU register, the accumulator register, that holds data values to be processed by the ALU and stores results from ALU arithmetic 
and shift operations. These were the five registers I chose to implement besides the CPU's main registers. 

### MIPS Instructions
The ALU class executes r-type (register data) instructions including arithmetic, bitwise logic, and comparison operations, and shift operations that are used in 
i-type (immediate value) branch instructions and j-type (jump) instructions. The arithmetic operations include `ADD`, `SUB`, `MUL`, and i-type `ADDI`, the 
bitwise logic operations include `AND`, `OR`, `XOR`, `NOT`, `NAND`, `NOR`, and `XNOR` (`NOT`, `NAND`, and `XNOR` are additions to MIPS32 instructions), the 
comparison operations include `SLT` and i-type `BNE`, and the shift operations include `SLL` and `SRA`. The instructions that use shift operations include `BNE` 
and j-type `J` and `JAL`. 

The memory classes (registers, cache, and main memory) inherit a parent memory class to share functionality and the memory bus class contains instances of cache 
and main memory to simulate the memory bus connecting the CPU to memory. The memory bus also contains an address bus property to hold the memory address to be 
accessed and a data bus property to hold data retrieved from or to be stored in memory. The memory bus executes i-type memory instructions including `LW`, `SW`, 
and `CACHE` memory codes (instead of `CACHE` operations). The `HALT` instruction is an addition and is included as a `SPECIAL` operation with r-type 
instructions although it is not a specific type of instruction.   

To simulate CPU processing, the main program file ('cpu_simulator.py') initializes instances of the assembler and CPU classes and inputs instruction and data 
value files (including two modified Codecademy files) to the assembler and CPU. I added calls to store the data values and instructions and start the 
fetch-decode-execute cycle. There are print statements to output information that is not a direct update of CPU processing, including what is in the address bus 
and data bus, what is stored in memory after it is accessed, and what is in the CPU's registers at the end of input processing.  
