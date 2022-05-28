from scanner import Symbol

"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""


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

    def __init__(self, names, devices, network, monitors, scanner):
        """Initialise constants."""

        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner

        self.sym = None  # current symbol from the scanner
        self.lookahead = self.scanner.get_symbol()  # one symbol ahead
        self.error_count = 0

    def next_sym(self):
        self.sym = self.lookahead

        if not self.test_symbols:
            return

        self.lookahead = self.scanner.get_symbol()

    def parse_literal(self, sym):

        self.next_sym()

        if sym and self.sym != sym:
            self.error(message=f'expected "{sym.string}", \
                                 found "{self.sym.string}"')

    def error(self, message="error!"):

        self.error_count += 1

        print(f">>> error: {message}")

        raise ValueError

    def parse_network(self):
        """Parse the circuit definition file."""

        START = Symbol(sym_type=self.scanner.KEYWORD,
                       sym_id=self.scanner.START_ID)
        END = Symbol(sym_type=self.scanner.KEYWORD,
                     sym_id=self.scanner.END_ID)
        EOF = Symbol(sym_type=self.scanner.EOF)

        DEVICES = Symbol(sym_type=self.scanner.KEYWORD,
                         sym_id=self.scanner.DEVICES_ID)
        CONNECTIONS = Symbol(sym_type=self.scanner.KEYWORD,
                             sym_id=self.scanner.CONNECTIONS_ID)
        OUTPUTS = Symbol(sym_type=self.scanner.KEYWORD,
                         sym_id=self.scanner.OUTPUTS_ID)

        def parse_devices():
            self.parse_block(DEVICES, self.parse_device)

        def parse_connections():
            self.parse_block(CONNECTIONS, self.parse_connection)

        def parse_outputs():
            self.parse_block(OUTPUTS, self.parse_output)

        # program = "START", devices, connections, outputs, "END" ;

        self.parse_literal(START)

        parse_devices()
        parse_connections()
        parse_outputs()

        self.parse_literal(END)
        self.parse_literal(EOF)

        return self.error_count == 0

    def parse_block(self, opening_symbol, inner_rule):

        C_OPEN = Symbol(sym_type=self.scanner.C_OPEN)
        C_CLOSE = Symbol(sym_type=self.scanner.C_CLOSE)

        # block = opening_symbol, "{", inner_rule, {inner_rule}, "}"

        self.parse_literal(opening_symbol)
        self.parse_literal(C_OPEN)

        while self.lookahead != C_CLOSE:
            inner_rule()

        self.parse_literal(C_CLOSE)

    def parse_device(self):

        EQUALS = Symbol(sym_type=self.scanner.EQUALS)
        SEMICOLON = Symbol(sym_type=self.scanner.SEMICOLON)

        # device = name, "=", type, ";"

        device_name = self.parse_name()
        self.parse_literal(EQUALS)
        device_type, device_argument = self.parse_type()
        self.parse_literal(SEMICOLON)

        return device_name, device_type, device_argument

    def parse_connection(self):

        ARROW = Symbol(sym_type=self.scanner.ARROW)
        SEMICOLON = Symbol(sym_type=self.scanner.SEMICOLON)

        # connection = signal, ">", signal, ";"

        lhs_signal_name, lhs_signal_pin = self.parse_signal()
        self.parse_literal(ARROW)
        rhs_signal_name, rh2_signal_pin = self.parse_signal()
        self.parse_literal(SEMICOLON)

        return lhs_signal_name, lhs_signal_pin, rhs_signal_name, rh2_signal_pin

    def parse_output(self):

        TILDE = Symbol(sym_type=self.scanner.TILDE)
        SEMICOLON = Symbol(sym_type=self.scanner.SEMICOLON)

        # output = signal, "~", name, ";"

        signal_name, signal_pin = self.parse_signal()
        self.parse_literal(TILDE)
        output_name = self.parse_name()
        self.parse_literal(SEMICOLON)

        return signal_name, signal_pin, output_name

    def parse_type(self):

        CLOCK = Symbol(sym_type=self.scanner.KEYWORD,
                       sym_id=self.scanner.CLOCK_ID)
        SWITCH = Symbol(sym_type=self.scanner.KEYWORD,
                        sym_id=self.scanner.SWITCH_ID)
        AND = Symbol(sym_type=self.scanner.KEYWORD,
                     sym_id=self.scanner.AND_ID)
        NAND = Symbol(sym_type=self.scanner.KEYWORD,
                      sym_id=self.scanner.NAND_ID)
        OR = Symbol(sym_type=self.scanner.KEYWORD,
                    sym_id=self.scanner.OR_ID)
        NOR = Symbol(sym_type=self.scanner.KEYWORD,
                     sym_id=self.scanner.NOR_ID)
        DTYPE = Symbol(sym_type=self.scanner.KEYWORD,
                       sym_id=self.scanner.DTYPE_ID)
        XOR = Symbol(sym_type=self.scanner.KEYWORD,
                     sym_id=self.scanner.XOR_ID)

        # type = clock | switch | and | nand | or | nor | dtype | xor

        type_parsers = {
            CLOCK.id: lambda: self.parse_type_func(CLOCK, self.parse_number),
            SWITCH.id: lambda: self.parse_type_func(SWITCH, self.parse_number),
            AND.id: lambda: self.parse_type_func(AND, self.parse_number),
            NAND.id: lambda: self.parse_type_func(NAND, self.parse_number),
            OR.id: lambda: self.parse_type_func(OR, self.parse_number),
            NOR.id: lambda: self.parse_type_func(NOR, self.parse_number),
            DTYPE.id: lambda: self.parse_type_func(DTYPE),
            XOR.id: lambda: self.parse_type_func(XOR),
        }

        try:
            return type_parsers[self.lookahead.id]()
        except KeyError:
            self.error(message=f'expected a device type name,\
                                 found "{self.lookahead.string}"')

    def parse_type_func(self, opening_symbol, inside_rule=None):

        B_OPEN = Symbol(sym_type=self.scanner.B_OPEN)
        B_CLOSE = Symbol(sym_type=self.scanner.B_CLOSE)
        argument = None

        # type_func = opening_symbol, "(", inside_rule, ")" ;

        self.parse_literal(opening_symbol)

        if inside_rule:
            self.parse_literal(B_OPEN)
            argument = inside_rule()
            self.parse_literal(B_CLOSE)

        return opening_symbol, argument

    def parse_number(self):

        self.next_sym()

        if self.sym.type != self.scanner.NUMBER:
            self.error(message=f'expected a number, found "{self.sym.string}"')

        return self.sym

    def parse_name(self):

        self.next_sym()

        if self.sym.type != self.scanner.NAME:
            self.error(message=f'expected a name, found "{self.sym.string}"')

        return self.sym

    def parse_signal(self):

        DOT = Symbol(sym_type=self.scanner.DOT)
        device = pin = None

        # signal = name, [ ".", name ]

        device = self.parse_name()

        if self.lookahead == DOT:
            self.parse_literal(DOT)
            pin = self.parse_name()

        return device, pin
