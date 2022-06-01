"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""
from scanner import Symbol
import functools


class ParseError(Exception):
    """Represents an error in parsing.

    Raised if there is an error in the parsing of a number, name or
    symbol. It allows us to break out of recursion many levels deep and
    recover to a known state.
    """

    pass


class Parser:
    """Parse the definition file and build the logic network.

    The parser deals with error handling. It analyses the syntactic and
    semantic correctness of the symbols it receives from the scanner, and
    then builds the logic network. If there are errors in the definition file,
    the parser detects this and tries to recover from it, giving helpful
    error messages.

    Parameters
    ----------
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.
    scanner: instance of the scanner.Scanner() class.

    Public methods
    --------------
    parse_network(self): Parses the circuit definition file.
    """

    def __init__(self, names, devices, network, monitors, scanner,
                 no_stop=False):
        """Initialise constants."""
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner

        # If no_stop is true then the parser will attempt to make devices,
        # connections and monitors even if an error has been found
        # (for testing)
        self.no_stop = no_stop

        self.sym = None  # current symbol from the scanner
        self.lookahead = self.scanner.get_symbol()  # one symbol ahead
        self.error_count = 0

    def make_keyword_symbol(self, string):
        """Create a Symbol object correcponding to the provided string."""
        return Symbol(sym_type=self.scanner.KEYWORD,
                      sym_id=self.names.lookup([string])[0],
                      string=string)

    def next_sym(self):
        """Step forward to get the next sym and lookahead."""
        self.sym = self.lookahead
        self.lookahead = self.scanner.get_symbol()

    def parse_literal(self, sym):
        """Handle parsing of a specific provided symbol.

        eg. a keyword or bracket.
        """
        self.next_sym()

        if sym and self.sym != sym:
            self.error(message=f'expected "{sym.string}", '
                               f'found "{self.sym.string}"')

    def parse_number(self):
        """Handle parsing of a number and return its symbol."""
        self.next_sym()

        if self.sym.type != self.scanner.NUMBER:
            self.error(message=f'expected a number, found "{self.sym.string}"')

        return self.sym

    def parse_name(self):
        """Handle parsing of a name and return the symbol representing it."""
        self.next_sym()

        if self.sym.type != self.scanner.NAME:
            self.error(message=f'expected a name, found "{self.sym.string}"')

        return self.sym

    def error(self, message="error!"):
        """Handle an error in parsing.

        Show the provided error message, increment the error count and
        raise the ParseError to be caught further up the recursion and
        try to recover.
        """
        if not self.error_count:
            print("errors detected in input file :(")

        self.error_count += 1

        print(f"\nat line {self.sym.line}, "
              f"offset {self.sym.char_offset}")
        print(self.scanner.get_file_line(self.sym.line).strip('\n'))
        print(" " * (self.sym.char_offset - 1) + "^")
        print(f">>> error: {message}\n")

        raise ParseError

    def recover(self):
        """Recover from a parsing error by proceeding to a known state.

        Try to forward the parser onto the next symbol where we know what
        state we're in eg. to the end of the statement with a semicolon or
        the end of the block with a curly bracket.
        """
        C_CLOSE = Symbol(self.scanner.C_CLOSE)
        SEMICOLON = Symbol(self.scanner.SEMICOLON)
        EOF = Symbol(self.scanner.EOF)

        while self.sym not in [SEMICOLON, EOF, C_CLOSE] \
                and self.lookahead != C_CLOSE:
            self.next_sym()

    def parse_network(self):
        """Parse the circuit definition file."""
        START = self.make_keyword_symbol("START")
        END = self.make_keyword_symbol("END")
        EOF = Symbol(sym_type=self.scanner.EOF, string="EOF")

        DEVICES = self.make_keyword_symbol("DEVICES")
        CONNECTIONS = self.make_keyword_symbol("CONNECTIONS")
        OUTPUTS = self.make_keyword_symbol("OUTPUTS")

        def parse_devices():
            self.parse_block(DEVICES, self.parse_device)

        def parse_connections():
            self.parse_block(CONNECTIONS, self.parse_connection)

        def parse_outputs():
            self.parse_block(OUTPUTS, self.parse_output)

        # program = "START", devices, connections, outputs, "END"

        try:

            self.parse_literal(START)

            parse_devices()
            parse_connections()
            parse_outputs()

            self.parse_literal(END)
            self.parse_literal(EOF)

        # parsing failed
        except ParseError:
            pass

        if self.error_count:
            print(f"number of errors: {self.error_count}")
        # check that all device inputs are connected
        if not self.network.check_network():
            print("Warning: Some device inputs are not connected")
        return self.error_count == 0

    def parse_block(self, opening_symbol, inner_rule):
        """Parse a block.

        A block is defined by an opening symbol followed by a set of
        statements parsed by inner_rule inisde curly brackets.
        The DEVICS, CONNECTIONS, and OUTPUTS sections are all blocks.
        """
        C_OPEN = Symbol(sym_type=self.scanner.C_OPEN, string="{")
        C_CLOSE = Symbol(sym_type=self.scanner.C_CLOSE, string="}")

        # block = opening_symbol, "{", inner_rule, {inner_rule}, "}"

        self.parse_literal(opening_symbol)
        self.parse_literal(C_OPEN)

        while C_CLOSE not in [self.sym, self.lookahead]:
            try:
                inner_rule()
            except ParseError:
                self.recover()

        if self.sym != C_CLOSE:
            self.parse_literal(C_CLOSE)

    def parse_device(self):
        """Parse a device statement.

        A device statement defines the name and type of a device.
        """
        EQUALS = Symbol(sym_type=self.scanner.EQUALS, string="=")
        SEMICOLON = Symbol(sym_type=self.scanner.SEMICOLON, string=";")

        # device = name, "=", type, ";"

        device_name = self.parse_name()
        self.parse_literal(EQUALS)
        device_type, device_argument = self.parse_type()
        self.parse_literal(SEMICOLON)

        self.make_device(device_name.id, device_type.id,
                         device_argument.id if device_argument else None)
        return device_name, device_type, device_argument

    def parse_connection(self):
        """Parse a connection between two signals."""
        ARROW = Symbol(sym_type=self.scanner.ARROW, string=">")
        SEMICOLON = Symbol(sym_type=self.scanner.SEMICOLON, string=";")

        # connection = signal, ">", signal, ";"

        lhs_signal_name, lhs_signal_pin = self.parse_signal()
        self.parse_literal(ARROW)
        rhs_signal_name, rh2_signal_pin = self.parse_signal()
        self.parse_literal(SEMICOLON)

        lhs_pin_id = rhs_pin_id = None
        if lhs_signal_pin is not None:
            lhs_pin_id = lhs_signal_pin.id
        if rh2_signal_pin is not None:
            rhs_pin_id = rh2_signal_pin.id

        self.make_connection(lhs_signal_name.id, lhs_pin_id,
                             rhs_signal_name.id, rhs_pin_id)
        return lhs_signal_name, lhs_signal_pin, rhs_signal_name, rh2_signal_pin

    def parse_output(self):
        """Parse an output - a name assigned to a signal."""
        # TILDE = Symbol(sym_type=self.scanner.TILDE, string="~")
        SEMICOLON = Symbol(sym_type=self.scanner.SEMICOLON, string=";")

        # output = signal, "~", name, ";"

        signal_name, signal_pin = self.parse_signal()
        self.parse_literal(SEMICOLON)

        if signal_pin is None:
            pin_id = None
        else:
            pin_id = signal_pin.id

        self.make_monitor(signal_name.id, pin_id)
        return signal_name, signal_pin

    def parse_type(self):
        """Parse a device type definition expression."""
        types_taking_arg = ["CLOCK", "SWITCH", "AND", "NAND", "OR", "NOR"]
        types_without_arg = ["DTYPE", "XOR"]

        taking_arg_symbols = [self.make_keyword_symbol(string)
                              for string in types_taking_arg]
        no_arg_symbols = [self.make_keyword_symbol(string)
                          for string in types_without_arg]

        arg_type_parsers = \
            {symbol.id: functools.partial(self.parse_type_func,
                                          symbol, self.parse_number)
             for symbol in taking_arg_symbols}

        no_arg_type_parsers = \
            {symbol.id: functools.partial(self.parse_type_func, symbol)
             for symbol in no_arg_symbols}

        type_parsers = {**arg_type_parsers, **no_arg_type_parsers}

        # type = clock | switch | and | nand | or | nor | dtype | xor

        try:
            return type_parsers[self.lookahead.id]()
        except KeyError:
            self.next_sym()
            self.error(message=f'expected a device type name, '
                               f'found "{self.sym.string}"')

    def parse_type_func(self, opening_symbol, inside_rule=None):
        """Inner function to parse_type.

        This function is constructed to match a certain device type
        and return its parameters.
        """
        B_OPEN = Symbol(sym_type=self.scanner.B_OPEN, string="(")
        B_CLOSE = Symbol(sym_type=self.scanner.B_CLOSE, string=")")
        argument = None

        # type_func = opening_symbol, "(", inside_rule, ")"

        self.parse_literal(opening_symbol)

        if inside_rule:
            self.parse_literal(B_OPEN)
            argument = inside_rule()
            self.parse_literal(B_CLOSE)

        return opening_symbol, argument

    def parse_signal(self):
        """Parse a signal.

        Parse eg. a device pin output and return the symbols
        representing the device name and pin name.
        """
        DOT = Symbol(sym_type=self.scanner.DOT, string=".")
        device = pin = None

        # signal = name, [ ".", name ]

        device = self.parse_name()

        if self.lookahead == DOT:
            self.parse_literal(DOT)
            pin = self.parse_name()

        return device, pin

    def make_device(self, device_name, device_type, device_argument):
        """Create a device from parsed information.

        Take the device info in the parameters and pass it to the
        devices object to add it into the network, handling errors.
        """
        if self.error_count == 0 or self.no_stop:
            error_type = self.devices.make_device(
                device_name, device_type, device_argument)

            if error_type != self.devices.NO_ERROR:
                if error_type == self.devices.INVALID_QUALIFIER:
                    self.error("invalid qualifier")
                elif error_type == self.devices.NO_QUALIFIER:
                    self.error("no qualifier")
                elif error_type == self.devices.QUALIFIER_PRESENT:
                    self.error("unexpected qualifier")
                elif error_type == self.devices.DEVICE_PRESENT:
                    self.error("device already defined")
                else:
                    self.error("bad device")

    def make_connection(self, device_1, pin_1, device_2, pin_2):
        """Add a connection between two devices parsed from the input file."""
        if self.error_count == 0 or self.no_stop:
            error_type = self.network.make_connection(
                device_1, pin_1, device_2, pin_2)

            if error_type != self.network.NO_ERROR:
                if error_type == self.network.INPUT_TO_INPUT:
                    self.error("input cannot connect to input")
                elif error_type == self.network.OUTPUT_TO_OUTPUT:
                    self.error("output cannot connect to output")
                elif error_type == self.network.INPUT_CONNECTED:
                    self.error("input already connected")
                elif error_type == self.network.DEVICE_ABSENT:
                    self.error("device absent")
                else:
                    self.error("port absent")

    def make_monitor(self, device_id, output_id, cycles_completed=0):
        """Add monitored output to the self.monitors object."""
        if self.error_count == 0 or self.no_stop:
            error_type = self.monitors.make_monitor(
                device_id, output_id, cycles_completed)

            if error_type != self.monitors.NO_ERROR:
                if error_type == self.network.DEVICE_ABSENT:
                    self.error("device absent")
                elif error_type == self.monitors.NOT_OUTPUT:
                    self.error("pin is not an output")
                elif error_type == self.monitors.MONITOR_PRESENT:
                    self.error("output is already monitored")
                else:
                    self.error()
