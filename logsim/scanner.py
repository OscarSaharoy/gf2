"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""


class Symbol:

    """Encapsulate a symbol and store its properties.

    Parameters
    ----------
    No parameters.

    Public methods
    --------------
    No public methods.
    """

    def __init__(self):
        """Initialise symbol properties."""
        self.type = None
        self.id = None


class Scanner:

    """Read circuit definition file and translate the characters into symbols.

    Once supplied with the path to a valid definition file, the scanner
    translates the sequence of characters in the definition file into symbols
    that the parser can use. It also skips over comments and irrelevant
    formatting characters, such as spaces and line breaks.

    Parameters
    ----------
    path: path to the circuit definition file.
    names: instance of the names.Names() class.

    Public methods
    -------------
    get_symbol(self): Translates the next sequence of characters into a symbol
                      and returns the symbol.
    """

    def __init__(self, path, names):
        """Open specified file and initialise reserved words and IDs."""

        self.names = Names()
        
        self.symbol_characters = ["", ";", "=", ",", ".", "~", ">", "(", ")",
                                 "{", "}"]
        
        self.symbol_types = [self.EOF, self.SEMICOLON, self.EQUALS, self.COMMA,
                             self.DOT, self.TILDE, self.ARROW, self.B_OPEN,
                             self.B_CLOSE, self.C_OPEN, self.C_CLOSE,
                             self.KEYWORD, self.NUMBER, self.NAME,
                            ] = range(14)
        """Symbols:
        
        EOF:        End of file
        B_OPEN:     (
        B_CLOSE:    )
        C_OPEN:     {
        C_CLOSE:    }
        ARROW:      >
        """
        
        self.keywords = ["START", "END", "DEVICES", "CONNECTIONS", "OUTPUTS",
                        "CLOCK", "SWITCH", "AND", "NAND", "OR", "NOR", "XOR",
                         "DTYPE"]
        [self.START_ID, self.END_ID, self.DEVICES_ID, self.CONNECTIONS_ID,
        self.OUTPUTS_ID, self.CLOCK_ID, self.SWITCH_ID, self.AND_ID,
        self.NAND_ID, self.OR_ID, self.NOR_ID, self.XOR_ID,
        self.DTYPE_ID] = self.names.lookup(self.keywords)
        
        self.current_character = ""

    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""
        
        self.skip_spaces()  # Needs defining
        
        symbol = Symbol()
        
        if self.current_character.isalpha():  # Name
            pass
        elif self.current_character.isdigit():  # Number
            pass
        elif self.current_character in self.symbol_characters:  # Special symbol
            pass
        else:  # Something else
            pass
        
    def skip_spaces(self):
        """A function to advance to the next character that is not a space, newline
        or part of a comment.
        """
        pass
