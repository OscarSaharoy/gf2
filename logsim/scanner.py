"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""
import sys
import linecache


def space_or_line(character):
    if character.isspace() or character == "/n":
        return True
    else:
        return False


class Symbol:

    """Encapsulate a symbol and store its properties.

    Parameters
    ----------
    No parameters.

    Public methods
    --------------
    No public methods.
    """

    def __init__(self, sym_type=None, sym_id=None, string=None):
        """Initialise symbol properties."""
        self.type = sym_type
        self.id = sym_id
        self.string = string

    def __eq__(self, other):
        """Check if this Symbol is the same as other."""

        if not isinstance(other, Symbol):
            return False

        return self.type == other.type and \
            self.id == other.id


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

        self.names = names
        self.path = path

        self.comment = "#"

        self.symbol_characters = ["", ";", "=", ",", ".", "~", ">", "(", ")",
                                  "{", "}"
                                  ]

        self.symbol_types = [self.EOF, self.SEMICOLON, self.EQUALS, self.COMMA,
                             self.DOT, self.TILDE, self.ARROW, self.B_OPEN,
                             self.B_CLOSE, self.C_OPEN, self.C_CLOSE,
                             self.KEYWORD, self.NUMBER, self.NAME
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
                         "DTYPE"
                         ]

        [self.START_ID, self.END_ID, self.DEVICES_ID, self.CONNECTIONS_ID,
         self.OUTPUTS_ID, self.CLOCK_ID, self.SWITCH_ID, self.AND_ID,
         self.NAND_ID, self.OR_ID, self.NOR_ID, self.XOR_ID,
         self.DTYPE_ID
         ] = self.names.lookup(self.keywords)

        self.open_file(path)

        self.current_character = ""
        self.line = 1
        self.char_offset = 0
        self.advance()

    def advance(self):
        """Move forward by one character in the file"""
        if self.current_character == '\n':
            self.line += 1
            self.char_offset = 0

        self.current_character = self.file.read(1)
        self.char_offset += 1

    def open_file(self, path):
        """Open and return the file specified by path."""
        try:
            self.file = open(path, 'r')

        except(IOError):
            print("Error! Specified file was not found.")
            sys.exit()

    def get_symbol(self):
        """Translate the next sequence of characters into a symbol.
        """
        self.skip_meaningless()

        symbol = Symbol()

        if self.current_character.isalpha():
            # This is a name or a keyword
            word = self.get_word()
            if word in self.keywords:
                symbol.type = self.KEYWORD
            else:
                symbol.type = self.NAME
            [symbol.id] = self.names.lookup([word])
            symbol.string = word

        elif self.current_character.isdigit():
            # This is a number. Only integers are accepted
            symbol.type = self.NUMBER
            symbol.id = self.get_number()
            symbol.string = str(symbol.id)

        elif self.current_character in self.symbol_characters:
            # Special symbol. Assign the appropriate type
            index = self.symbol_characters.index(self.current_character)
            symbol.type = self.symbol_types[index]
            symbol.string = self.current_character
            self.advance()

        else:
            # Something else, has no meaning, just skip it
            self.advance()

        return symbol

    def get_word(self):
        """Returns the string of characters up until the next non-
        alphanumeric character.
        """
        word = ""
        while self.current_character.isalnum() and \
                not self.current_character == "":
            word = word + self.current_character
            self.advance()
        return word

    def get_number(self):
        """Returns the integer represented by the next block of alphanumeric characters
        """
        number = ""
        while self.current_character.isdigit() and \
                not self.current_character == "":
            number = number + self.current_character
            self.advance()
        return int(number)

    def skip_spaces_and_lines(self):
        """A function to advance to the next character that is not a space or newline.
        """
        while space_or_line(self.current_character):
            self.advance()

    def skip_meaningless(self):
        """Advance until the current character is not a space, newline or
        part of a comment.
        """
        is_comment = False
        self.skip_spaces_and_lines()

        if self.current_character == self.comment:
            is_comment = True

        while is_comment:
            self.advance()
            # Advance until the comment end is found
            if self.current_character == self.comment:
                is_comment = False

                # Comment has ended, skip any following whitespace
                self.advance()
                self.skip_spaces_and_lines()

                # Check that the comment is not followed by a second comment
                if self.current_character == self.comment:
                    is_comment = True

    def get_file_line(self, line_number):
        return linecache.getline(self.path, line_number)
