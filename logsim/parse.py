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

        self.test_symbols = [
            Symbol(sym_type=scanner.KEYWORD,
                   sym_id=scanner.START_ID),
            Symbol(sym_type=scanner.KEYWORD,
                   sym_id=scanner.DEVICES_ID),
            Symbol(sym_type=scanner.C_OPEN),
            Symbol(sym_type=scanner.NAME,
                   sym_id=names.lookup(["c1"])[0]),
            Symbol(sym_type=scanner.EQUALS),
            Symbol(sym_type=scanner.KEYWORD,
                   sym_id=names.lookup(["CLOCK"])[0]),
            Symbol(sym_type=scanner.B_OPEN),
            Symbol(sym_type=scanner.NUMBER,
                   sym_id=1),
            Symbol(sym_type=scanner.B_CLOSE),
            Symbol(sym_type=scanner.SEMICOLON),
            Symbol(sym_type=scanner.NAME,
                   sym_id=names.lookup(["c1"])[0]),
            Symbol(sym_type=scanner.EQUALS),
            Symbol(sym_type=scanner.KEYWORD,
                   sym_id=names.lookup(["XOR"])[0]),
            Symbol(sym_type=scanner.SEMICOLON),
            Symbol(sym_type=scanner.NAME,
                   sym_id=names.lookup(["c2"])[0]),
            Symbol(sym_type=scanner.EQUALS),
            Symbol(sym_type=scanner.KEYWORD,
                   sym_id=names.lookup(["CLOCK"])[0]),
            Symbol(sym_type=scanner.B_OPEN),
            Symbol(sym_type=scanner.NUMBER,
                   sym_id=4),
            Symbol(sym_type=scanner.B_CLOSE),
            Symbol(sym_type=scanner.SEMICOLON),
            Symbol(sym_type=scanner.C_CLOSE),
            Symbol(sym_type=scanner.KEYWORD,
                   sym_id=scanner.CONNECTIONS_ID),
            Symbol(sym_type=scanner.C_OPEN),
            Symbol(sym_type=scanner.NAME,
                   sym_id=names.lookup(["c2"])[0]),
            Symbol(sym_type=scanner.ARROW),
            Symbol(sym_type=scanner.NAME,
                   sym_id=names.lookup(["c1"])[0]),
            Symbol(sym_type=scanner.DOT),
            Symbol(sym_type=scanner.NAME,
                   sym_id=names.lookup(["out"])[0]),
            Symbol(sym_type=scanner.SEMICOLON),
            Symbol(sym_type=scanner.NAME,
                   sym_id=names.lookup(["c1"])[0]),
            Symbol(sym_type=scanner.ARROW),
            Symbol(sym_type=scanner.NAME,
                   sym_id=names.lookup(["c2"])[0]),
            Symbol(sym_type=scanner.SEMICOLON),
            Symbol(sym_type=scanner.C_CLOSE),
            Symbol(sym_type=scanner.KEYWORD,
                   sym_id=scanner.OUTPUTS_ID),
            Symbol(sym_type=scanner.C_OPEN),
            Symbol(sym_type=scanner.NAME,
                   sym_id=names.lookup(["c1"])[0]),
            Symbol(sym_type=scanner.TILDE),
            Symbol(sym_type=scanner.NAME,
                   sym_id=names.lookup(["clock"])[0]),
            Symbol(sym_type=scanner.SEMICOLON),
            Symbol(sym_type=scanner.C_CLOSE),
            Symbol(sym_type=scanner.KEYWORD,
                   sym_id=scanner.END_ID),
            Symbol(sym_type=scanner.EOF)
        ]

        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner

        self.sym = None  # current symbol from the scanner
        self.lookahead = self.test_symbols.pop(0)  # one symbol ahead
        self.error_count = 0

    def check_for(self, sym, error_info=None):

        self.sym = self.lookahead

        if sym and self.sym != sym:
            print(f"expected {sym.type, sym.id}, \
                    found {self.sym.type, self.sym.id}")
            self.error(error_info)

        if not self.test_symbols:
            return

        # self.lookahead = self.scanner.get_symbol()
        self.lookahead = self.test_symbols.pop(0)

    def error(self, error_info=None):

        self.error_count += 1
        raise ValueError

        if not error_info:
            return

        print(error_info["message"])

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

        self.check_for(START, error_info={"message": "error: expected START"})

        parse_devices()
        parse_connections()
        parse_outputs()

        self.check_for(END)
        self.check_for(EOF)

        return self.error_count == 0

    def parse_block(self, opening_symbol, inner_rule):

        C_OPEN = Symbol(sym_type=self.scanner.C_OPEN)
        C_CLOSE = Symbol(sym_type=self.scanner.C_CLOSE)

        # block = opening_symbol, "{", inner_rule, {inner_rule}, "}"

        self.check_for(opening_symbol)
        self.check_for(C_OPEN)

        while self.lookahead != C_CLOSE:
            inner_rule()

        self.check_for(C_CLOSE)

    def parse_device(self):

        EQUALS = Symbol(sym_type=self.scanner.EQUALS)
        SEMICOLON = Symbol(sym_type=self.scanner.SEMICOLON)

        # device = name, "=", type, ";"

        device_name = self.parse_name()
        self.check_for(EQUALS)
        device_type, device_argument = self.parse_type()
        self.check_for(SEMICOLON)

        return device_name, device_type, device_argument

    def parse_connection(self):

        ARROW = Symbol(sym_type=self.scanner.ARROW)
        SEMICOLON = Symbol(sym_type=self.scanner.SEMICOLON)

        # connection = signal, ">", signal, ";"

        lhs_signal_name, lhs_signal_pin = self.parse_signal()
        self.check_for(ARROW)
        rhs_signal_name, rh2_signal_pin = self.parse_signal()
        self.check_for(SEMICOLON)

        return lhs_signal_name, lhs_signal_pin, rhs_signal_name, rh2_signal_pin

    def parse_output(self):

        TILDE = Symbol(sym_type=self.scanner.TILDE)
        SEMICOLON = Symbol(sym_type=self.scanner.SEMICOLON)

        # output = signal, "~", name, ";"

        signal_name, signal_pin = self.parse_signal()
        self.check_for(TILDE)
        output_name = self.parse_name()
        self.check_for(SEMICOLON)

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
            self.error()

    def parse_type_func(self, opening_symbol, inside_rule=None):

        B_OPEN = Symbol(sym_type=self.scanner.B_OPEN)
        B_CLOSE = Symbol(sym_type=self.scanner.B_CLOSE)
        argument = None

        # type_func = opening_symbol, "(", inside_rule, ")" ;

        self.check_for(opening_symbol)

        if inside_rule:
            self.check_for(B_OPEN)
            argument = inside_rule()
            self.check_for(B_CLOSE)

        return opening_symbol, argument

    def parse_number(self):

        self.sym = self.lookahead

        if self.sym.type != self.scanner.NUMBER:
            self.error()

        if not self.test_symbols:
            self.error()
            return

        # self.lookahead = self.scanner.get_symbol()
        self.lookahead = self.test_symbols.pop(0)

        return self.sym

    def parse_name(self):

        self.sym = self.lookahead

        if self.sym.type != self.scanner.NAME:
            self.error()

        if not self.test_symbols:
            self.error()
            return

        # self.lookahead = self.scanner.get_symbol()
        self.lookahead = self.test_symbols.pop(0)

        return self.sym

    def parse_signal(self):

        DOT = Symbol(sym_type=self.scanner.DOT)
        device = pin = None

        # signal = name, [ ".", name ]

        device = self.parse_name()

        if self.lookahead == DOT:
            self.check_for(DOT)
            pin = self.parse_name()

        return device, pin
