# from scanner import Symbol

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
        self.lookahead = None  # one symbol ahead of the current symbol
        self.error_count = 0

        self.test_symbols = []

    def parse_network(self):
        """Parse the circuit definition file."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.

        self.check_for(self.scanner.KEYWORD, self.scanner.START_ID)

        self.parse_devices()
        self.parse_connections()
        self.parse_outputs()

        self.check_for(self.scanner.KEYWORD, self.scanner.END_ID)

        return self.error_count == 0

    def error(self):
        self.error_count += 1

    def check_for(self, sym_type, sym_id=None):

        self.sym = self.lookahead
        # self.lookahead = self.scanner.get_symbol()
        self.lookahead = self.test_symbols.pop(0)

        if self.sym.type != sym_type or sym_id and self.sym.id != sym_id:
            self.error()

    def parse_block(self, opening_symbol, inner_rule):

        # block = opening_symbol, "{", inner_rule, {inner_rule}, "}"

        self.check_for(opening_symbol.type, opening_symbol.id)
        self.check_for(self.scanner.C_OPEN)

        while self.lookahead.type != self.scanner.C_CLOSE:
            inner_rule()

        self.check_for(self.scanner.C_CLOSE)

    def parse_devices(self):

        # devices = "DEVICES", "{", device, {device}, "}"

        self.check_for(self.scanner.KEYWORD, self.scanner.DEVICES_ID)
        self.check_for(self.scanner.C_OPEN)

        while self.lookahead.type != self.scanner.C_CLOSE:
            self.parse_device()

        self.check_for(self.scanner.C_CLOSE)

    def parse_connections(self):

        # connections = "CONNECTIONS", "{", connection, {connection}, "}"

        self.check_for(self.scanner.KEYWORD, self.scanner.CONNECTIONS_ID)
        self.check_for(self.scanner.C_OPEN)

        while self.lookahead.type != self.scanner.C_CLOSE:
            self.parse_connection()

        self.check_for(self.scanner.C_CLOSE)

    def parse_outputs(self):

        # outputs = "OUTPUTS", "{", output, {output}, "}"

        self.check_for(self.scanner.KEYWORD, self.scanner.OUTPUTS_ID)
        self.check_for(self.scanner.C_OPEN)

        while self.lookahead.type != self.scanner.C_CLOSE:
            self.parse_output()

        self.check_for(self.scanner.C_CLOSE)

    def parse_device(self):

        # device = name, "=", type, ";"

        self.parse_name()
        self.check_for(self.scanner.EQUALS)
        self.parse_type()
        self.check_for(self.scanner.SEMICOLON)

    def parse_connection(self):

        # connection = signal, ">", signal, ";"

        self.parse_signal()
        self.check_for(self.scanner.ARROW)
        self.parse_signal()
        self.check_for(self.scanner.SEMICOLON)

    def parse_output(self):

        # output = signal, "~", name, ";"

        self.parse_signal()
        self.check_for(self.scanner.TILDE)
        self.parse_name()
        self.check_for(self.scanner.SEMICOLON)

    def parse_name(self):
        pass

    def parse_signal(self):
        pass
