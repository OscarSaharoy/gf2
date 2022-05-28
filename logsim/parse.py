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
                   sym_id=names.lookup(["test1"])[0]),
            Symbol(sym_type=scanner.EQUALS),
            Symbol(sym_type=scanner.NAME,
                   sym_id=names.lookup(["test1"])[0]),
            Symbol(sym_type=scanner.SEMICOLON),
            Symbol(sym_type=scanner.C_CLOSE),
            Symbol(sym_type=scanner.KEYWORD,
                   sym_id=scanner.CONNECTIONS_ID),
            Symbol(sym_type=scanner.C_OPEN),
            Symbol(sym_type=scanner.C_CLOSE),
            Symbol(sym_type=scanner.KEYWORD,
                   sym_id=scanner.OUTPUTS_ID),
            Symbol(sym_type=scanner.C_OPEN),
            Symbol(sym_type=scanner.C_CLOSE),
            Symbol(sym_type=scanner.KEYWORD,
                   sym_id=scanner.END_ID),
        ]

        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner

        self.sym = None  # current symbol from the scanner
        self.lookahead = self.test_symbols.pop(0)  # one symbol ahead
        self.error_count = 0

        DEVICES = Symbol(sym_type=self.scanner.KEYWORD,
                         sym_id=self.scanner.DEVICES_ID)
        CONNECTIONS = Symbol(sym_type=self.scanner.KEYWORD,
                             sym_id=self.scanner.CONNECTIONS_ID)
        OUTPUTS = Symbol(sym_type=self.scanner.KEYWORD,
                         sym_id=self.scanner.OUTPUTS_ID)

        self.parse_devices = lambda: \
            self.parse_block(DEVICES, self.parse_device)
        self.parse_connections = lambda: \
            self.parse_block(CONNECTIONS, self.parse_connection)
        self.parse_outputs = lambda: \
            self.parse_block(OUTPUTS, self.parse_output)

    def check_for(self, sym, error_info=None):

        self.sym = self.lookahead

        if sym and self.sym != sym:
            print(f"expected {sym.id}, found {self.sym.id}")
            self.error(error_info)

        if not self.test_symbols:
            return

        # self.lookahead = self.scanner.get_symbol()
        self.lookahead = self.test_symbols.pop(0)

    def error(self, error_info):

        self.error_count += 1

        if not error_info:
            return

        print(error_info["message"])

    def parse_network(self):
        """Parse the circuit definition file."""

        START = Symbol(sym_type=self.scanner.KEYWORD,
                       sym_id=self.scanner.START_ID)
        END = Symbol(sym_type=self.scanner.KEYWORD,
                     sym_id=self.scanner.END_ID)

        # program = "START", devices, connections, outputs, "END" ;

        self.check_for(START, error_info={"message": "error: expected START"})

        self.parse_devices()
        self.parse_connections()
        self.parse_outputs()

        self.check_for(END)

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

        self.parse_name()
        self.check_for(EQUALS)
        self.parse_type()
        self.check_for(SEMICOLON)

    def parse_connection(self):

        ARROW = Symbol(sym_type=self.scanner.ARROW)
        SEMICOLON = Symbol(sym_type=self.scanner.SEMICOLON)

        # connection = signal, ">", signal, ";"

        self.parse_signal()
        self.check_for(ARROW)
        self.parse_signal()
        self.check_for(SEMICOLON)

    def parse_output(self):

        TILDE = Symbol(sym_type=self.scanner.TILDE)
        SEMICOLON = Symbol(sym_type=self.scanner.SEMICOLON)

        # output = signal, "~", name, ";"

        self.parse_signal()
        self.check_for(TILDE)
        self.parse_name()
        self.check_for(SEMICOLON)

    def parse_type(self):

        # type = clock | switch | and | nand | or | nor | dtype | xor

        # type_parsers = { 0 : self.parse_clock }

        # type_parser = None

        self.check_for(None)

    def parse_name(self):
        self.check_for(None)

    def parse_signal(self):
        self.check_for(None)
