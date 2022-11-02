import sys
import re

program_counter = 16 # Equivalent to 'PC' in the TOY Reference Card.
registers = {} # Equivalent to 'R' in the TOY Reference Card.
memory = {} # Equivalent to 'M' in the TOY Reference Card.
debug_mode = False # Output the details of every instruction.
ascii_mode = False # I/O is converterd to and from ASCII text (as opposed to decimals)


def print_debug(opcode, d, s, t, addr):
    if not debug_mode: return
    message = ''

    match opcode:
        case '1':
            message = f'Adding register {s} ({registers[s]}) to register {t} ({registers[t]}) and storing the result in register {d}'
        case '2':
            message = f'Subtracting register {t} ({registers[t]}) from register {s} ({registers[s]}) and storing the result in register {d}'
        case '3':
            message = f'Performing binary AND on registers {s} and {t} and storing the result in register {d}'
        case '4':
            message = f'Performing binary OR on registers {s} and {t} and storing the result in register {d}'
        case '5':
            message = f'Performing binary left shift on registers {s} by {t} and storing the result in register {d}'
        case '6':
            message = f'Performing binary right shift on registers {s} by {t} and storing the result in register {d}'

        case '7':
            message = f'Storing {addr} in register {d}'
        case '8':
            if addr == 'FF': message = f'Storing input in memory {addr}'
            else: message = f'Storing memory {addr} ({memory[addr]}) in register {d}'
        case '9':
            if addr == 'FF': message = f'Storing register {d} ({registers[d]}) in memory {addr} and printing {registers[d]}'
            else: message = f'Storing register {d} ({registers[d]}) in memory {addr}'
        case 'A':
            if registers[t] == 'FF': message = f'Storing register {d} ({registers[d]}) in memory {load_memory(registers[t])} and printing {registers[d]}'
            else: message = f'Storing register {d} ({registers[d]}) in memory {load_memory(registers[t])}'
        case 'B':
            if registers[t] == 'FF': message = f'Storing register {d} ({registers[d]}) in memory {registers[t]} and printing {registers[d]}'
            else: message = f'Storing register {d} ({registers[d]}) in memory {registers[t]}'

        case '0': # Halt
            message = 'Halting'
        case 'C':
            if decimal(registers[d]) == 0: message = f'Checked if register {d} ({registers[d]}) was equal to zero - it was, so set the program counter to {decimal(addr)}'
            else: message = f'Checked if register {d} ({registers[d]}) was equal to zero - it was not'
        case 'D':
            if int(registers[d], 16) > 0: message = f'Checked if register {d} ({registers[d]}) was greater than zero - it was, so set the program counter to {decimal(addr)}'
            else: message = f'Checked if register {d} ({registers[d]}) was greater than zero - it was not'
        case 'E':
            message = f'Setting the program counter to register {d} ({decimal(registers[d]) + 1})'
        case 'F':
            message = f'Storing the program counter ({hex_string(program_counter)}) in register {d} and setting the program counter to {decimal(addr)}'
        
    print(message)

def throw_error(message):
    print(f'Error (line {hex_string(program_counter)}): {message}')
    sys.exit()

def split_current_instruction():
    instruction = load_memory(hex_string(program_counter))

    # 'opcode', 'd', 's', 't', and 'addr' are the names given by the TOY
    # Reference Card. For consistency, they are also used here.
    opcode = instruction[0]
    d = instruction[1]
    s = instruction[2]
    t = instruction[3]
    addr = instruction[2:4]

    return opcode, d, s, t, addr


# Executes the instruction found at the memory location determined by the
# program counter. Returns True if the program should halt, otherwise False.
def execute():
    opcode, d, s, t, addr = split_current_instruction()
    
    print_debug(opcode, d, s, t, addr)

    # Instructions 1 through 6 perform math operations on the values found
    # in two registers. For simplicity, those registers are loaded and
    # converted to decimal form.
    a = decimal(registers[s])
    b = decimal(registers[t])

    # All opcode values are taken from the TOY Reference Card.
    match opcode:
        case '1':
            result = a + b
            check_range(result)
            store_register(d, long_hex_string(result))
        case '2':
            result = a - b
            check_range(result)
            store_register(d, long_hex_string(result))
        case '3':
            result = a & b
            check_range(result)
            store_register(d, long_hex_string(result))
        case '4':
            result = a ^ b
            check_range(result)
            store_register(d, long_hex_string(result))
        case '5':
            result = a << b
            check_range(result)
            store_register(d, long_hex_string(result))
        case '6':
            result = a >> b
            check_range(result)
            store_register(d, long_hex_string(result))

        case '7':
            store_register(d, addr)
        case '8':
            if addr == 'FF':
                response = input(': ')
                if ascii_mode: response = ord(response)
                memory[addr] = response
            store_register(d, memory[addr])
        case '9':
            store_memory(addr, registers[d])

        case 'A':
            # Store the value found at the memory location defined by the value in
            # register 't', in register 'd' (See TOY Reference Card for a clearer
            # explanation).
            store_register(d, load_memory(registers[t]))

        case 'B':
            # Store the value found at the memory location defined by the value in
            # register 't', in the memory location defined by the value in register 'd'
            # (See TOY Reference Card for a clearer explanation).
            store_memory(registers[t], registers[d])

        case '0':
            # Halt
            return None
        case 'C':
            if decimal(registers[d]) == 0: return decimal(addr)
        case 'D':
            if int(registers[d], 16) > 0: return decimal(addr)
        case 'E':
            return decimal(registers[d]) + 1
        case 'F':
            store_register(d, hex_string(program_counter))
            return decimal(addr)

    return program_counter + 1


# Converts an integer to an 'XX' format where X is a hex digit.
def short_hex_string(i):
    return hex_string(i)[-1]

# Converts an integer to an 'XX' format where X is a hex digit.
def hex_string(i):
    hex_string = hex(i)
    return hex_string[hex_string.find('x') + 1:].upper().zfill(2)

# Converts an integer to an '00XX' format where X is a hex digit.
def long_hex_string(i):
    return hex_string(i).zfill(4)


# Accounts for a four-digit hexadecimal two's complement representation.
def decimal(x):
    decimal = int(x, 16)
    if decimal > 32767: decimal -= 65536
    return decimal


def load_memory(location):
    # Truncates the argument because it may be longer than necessary.
    return memory[location[-2:]]


def main():
    global program_counter
    global debug_mode
    global ascii_mode

    if len(sys.argv) > 1:
        filename = sys.argv[1]
        if len(sys.argv) > 2:
            debug_mode = '--debug' in sys.argv[2:]
            ascii_mode = '--ascii' in sys.argv[2:]
    else:
        print()
        print('Usage:')
        print('  <filename> [options]')
        print()
        print('Options:')
        print('  --debug  Show a detailed message every time an instruction is executed')
        print('  --ascii  Input and output is converted to and from ASCII text (e.g. inputting \'A\' will yield 65)')
        print()
        return


    current_line = 0
    with open(filename, 'r') as f:
        for line in f:
            current_line += 1

            # Treat any line starting with the pattern XX: XXXX as an
            # instruction, where X is a hex digit. Any additional text on the
            # line is considered a comment.
            if re.match(r'[0-9A-F]{2}: [0-9A-F]{4}', line):
                memory[line[0:2]] = line[4:8]

            # Ignore any comment, program declaration, function declaration, or
            # whitespace, respectively. Program and function declarations have
            # no effect on the actual exectution.
            if (re.match(r'//', line)
                or re.match(r'program', line)
                or re.match(r'function', line)
                or re.match(r'\s*$', line)):
                continue

            # raise Exception(f'Error: Unrecognized line format')

    while program_counter != None:
        program_counter = execute()


# Check that a value is between -2^15 and 2^15-1
def check_range(value):
    if value < -32768 or 32767 < value:
        throw_error(f'Operation outside the range of -32768 and 32767 ({str(value)})')


def store_memory(address, value):
    address = str(address).zfill(2)[-2:]
    value = str(value).zfill(4)

    # Output if we are writing to memory location 'FF'.
    if address == 'FF':
        output = decimal(value)
        if ascii_mode: output = chr(output)
        print('> ' + value + ',', output)

    memory[address] = value


def store_register(address, value):
    address = str(address)[-1:]
    value = str(value).zfill(4)
    if address == '00':
        throw_error(f'Register 00 is reserved')
    registers[address] = value


if __name__ == '__main__':
    # Initialize registers and memory.
    for i in range(16):
        registers[short_hex_string(i)] = '0000'
    for i in range(256):
        memory[hex_string(i)] = '0000'

    main()
