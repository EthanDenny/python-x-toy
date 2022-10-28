import sys
import re

program_counter = 16 # Equivalent to 'PC' in the TOY Reference Card.
registers = {} # Equivalent to 'R' in the TOY Reference Card.
memory = {} # Equivalent to 'M' in the TOY Reference Card.
debug_mode = False # Output the details of every instruction.


def debug(out):
    if debug_mode: print(out)

# Executes the instruction found at the memory location determined by the
# program counter. Returns True if the program should halt, otherwise False.
def execute():
    instruction = load_memory(hex_string(program_counter))

    # 'opcode', 'd', 's', 't', and 'addr' are the names given by the TOY
    # Reference Card. For consistency, they are also used here.
    opcode = instruction[0]
    d = instruction[1]
    s = instruction[2]
    t = instruction[3]
    addr = instruction[2:4]

    # Instructions 1 through 6 perform math operations on the values found
    # in two registers. For simplicity, those registers are loaded and
    # converted to decimal form.
    a = decimal(registers[s])
    b = decimal(registers[t])

    # All opcode values are taken from the TOY Reference Card.

    match opcode:
        case '1': # Add
            debug(f'Adding register {s} ({registers[s]}) to register {t} \
                    ({registers[t]}) and storing the result in register {d}')
            result = a + b
            check_range(result)
            store_register(d, long_hex_string(result))
        case '2': # Subtract
            debug(f'Subtracting register {t} ({registers[t]}) from register {s} \
                    ({registers[s]}) and storing the result in register {d}')
            result = a - b
            check_range(result)
            store_register(d, long_hex_string(result))
        case '3': # Binary AND
            debug(f'Performing binary AND on registers {s} and {t} and storing \
                    the result in register {d}')
            result = a & b
            check_range(result)
            store_register(d, long_hex_string(result))
        case '4': # Binary OR
            debug(f'Performing binary OR on registers {s} and {t} and storing the \
                    result in register {d}')
            result = a ^ b
            check_range(result)
            store_register(d, long_hex_string(result))
        case '5': # Binary left shift
            debug(f'Performing binary left shift on registers {s} by {t} and \
                    storing the result in register {d}')
            result = a << b
            check_range(result)
            store_register(d, long_hex_string(result))
        case '6': # Binary right shift
            debug(f'Performing binary right shift on registers {s} by {t} and \
                    storing the result in register {d}')
            result = a >> b
            check_range(result)
            store_register(d, long_hex_string(result))

        # Store value 'addr' in register 'd'.
        case '7':
            debug(f'Storing {addr} in register {d}')
            store_register(d, addr)
        # Store the value found at memory location 'addr' in register 'd',
        case '8':
            if addr == 'FF':
                debug(f'Storing input in memory {addr}')
                memory[addr] = input(': ')
            debug(f'Storing memory {addr} ({memory[addr]}) in register {d}')
            store_register(d, memory[addr])
        # Store the value in register 'd' in memory location 'addr',
        case '9':
            if addr == 'FF':
                debug(f'Storing register {d} ({registers[d]}) in memory {addr} \
                        and printing {registers[d]}')
            else:
                debug(f'Storing register {d} ({registers[d]}) in memory {addr}')
            store_memory(addr, registers[d])
        # Store the value found at the memory location defined by the value in
        # register 't', in register 'd' (See TOY Reference Card for a clearer
        # explanation).
        case 'A':
            if registers[t] == 'FF':
                debug(f'Storing register {d} ({registers[d]}) in memory \
                        {load_memory(registers[t])} and printing {registers[d]}')
            else:
                debug(f'Storing register {d} ({registers[d]}) in memory \
                        {load_memory(registers[t])}')
            store_register(d, load_memory(registers[t]))
        # Store the value found at the memory location defined by the value in
        # register 't', in the memory location defined by the value in register 'd'
        # (See TOY Reference Card for a clearer explanation).
        case 'B':
            if registers[t] == 'FF':
                debug(f'Storing register {d} ({registers[d]}) in memory \
                        {registers[t]} and printing {registers[d]}')
            else:
                debug(f'Storing register {d} ({registers[d]}) in memory \
                        {registers[t]}')
            store_memory(registers[t], registers[d])

        case '0': # Halt
            debug('Halting')
            return None
        # If the value in register 'd' == 0, set the program counter to 'addr'.
        case 'C':
            if decimal(registers[d]) == 0:
                debug(f'Checked if register {d} ({registers[d]}) was equal to \
                        zero - it was, so set the program counter to \
                        {decimal(addr)}')
                return decimal(addr)
            else:
                debug(f'Checked if register {d} ({registers[d]}) was equal to \
                        zero - it was not')
        # If the value in register 'd' > 0, set the program counter to 'addr'.
        case 'D':
            if int(registers[d], 16) > 0:
                debug(f'Checked if register {d} ({registers[d]}) was greater than \
                        zero - it was, so set the program counter to \
                        {decimal(addr)}')
                return decimal(addr)
            else:
                debug(f'Checked if register {d} ({registers[d]}) was greater than \
                        zero - it was not')
        # Set the program counter to the value in register 'd'.
        case 'E':
            debug(f'Setting the program counter to register {d} \
                    ({decimal(registers[d]) + 1})')
            return decimal(registers[d]) + 1
        # Set the program counter in register 'd', and set the program counter to
        # 'addr'.
        case 'F':
            debug(f'Storing the program counter \
                    ({hex_string(program_counter)}) in register {d} \
                    and setting the program counter to {decimal(addr)}')
            store_register(d, hex_string(program_counter))
            return decimal(addr)

    return program_counter + 1


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
    global debug_mode

    # There are no extra arguments
    if len(sys.argv) == 1:
        file_name = input('File name: ')
    # There is only one extra argumen (a file name to load).
    elif len(sys.argv) >= 2:
        file_name = sys.argv[1]
        # There are two or more extra arguments, if the first of these is '1',
        # activate debug mode.
        if len(sys.argv) >= 3:
            debug_mode = sys.argv[2] == '1'

    current_line = 0
    with open(file_name, 'r') as f:
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
        raise Exception(f'Error at {hex_string(program_counter)}: \
                          Operation outside the range of -32768 and 32767 \
                          ({str(value)})')


def store_memory(address, value):
    address = str(address).zfill(2)[-2:]
    value = str(value).zfill(4)

    # Output if we are writing to memory location 'FF'.
    if address == 'FF':
        print('> ' + value + ',', decimal(value))

    memory[address] = value


def store_register(address, value):
    address = str(address)[-1:]
    value = str(value).zfill(4)
    if address == '00':
        raise Exception(f'Error at {convert_to_hex_string(program_counter)}: \
                          Register 00 is reserved')
    registers[address] = value


if __name__ == '__main__':
    # Initialize registers and memory.
    for i in range(16):
        registers[hex_string(i)] = '0000'
    for i in range(256):
        memory[long_hex_string(i)] = '0000'

    main()
