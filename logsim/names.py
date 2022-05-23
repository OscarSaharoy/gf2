"""Map variable names and string names to unique integers.

Used in the Logic Simulator project. Most of the modules in the project
use this module either directly or indirectly.

Classes
-------
Names - maps variable names and string names to unique integers.
"""

from collections import OrderedDict


class Names:

    """Map variable names and string names to unique integers.

    This class deals with storing grammatical keywords and user-defined words,
    and their corresponding name IDs, which are internal indexing integers. It
    provides functions for looking up either the name ID or the name string.
    It also keeps track of the number of error codes defined by other classes,
    and allocates new, unique error codes on demand.

    Parameters
    ----------
    No parameters.

    Public methods
    -------------
    unique_error_codes(self, num_error_codes): Returns a list of unique integer
                                               error codes.

    query(self, name_string): Returns the corresponding name ID for the
                        name string. Returns None if the string is not present.

    lookup(self, name_string_list): Returns a list of name IDs for each
                        name string. Adds a name if not already present.

    get_name_string(self, name_id): Returns the corresponding name string for
                        the name ID. Returns None if the ID is not present.
    """

    def __init__(self):
        """Initialise names list."""
        self.error_code_count = 0  # how many error codes have been declared
        self.name_count = 0
        self.name_map = {}

    def unique_error_codes(self, num_error_codes):
        """Return a list of unique integer error codes."""
        if not isinstance(num_error_codes, int):
            raise TypeError("Expected num_error_codes to be an integer.")
        self.error_code_count += num_error_codes
        return range(self.error_code_count - num_error_codes,
                     self.error_code_count)

    def query(self, name_string):
        """Return the corresponding name ID for name_string.

        If the name string is not present in the names list, return None.
        """

        # try to get the name id from the name map
        # and if it isnt there return none
        try:
            return self.name_map[name_string]
        except KeyError:
            return None

    def lookup(self, name_list):
        """Return a list of name IDs for each name string in name_string_list.

        If the name string is not present in the names list, add it.
        """

        # make sure all items in name list are strings
        if not all(isinstance(item, str) for item in name_list):
            raise TypeError(
                "All items in argument of Names.lookup must be strings")

        # Filter duplicate elements from name_list
        name_list_filtered = list(OrderedDict.fromkeys(name_list))
        # Create list of all names that are not in name_map
        new_names = [name for name in name_list_filtered
                     if name not in self.name_map.keys()]

        # create map of new names to ids
        new_names_map = {new_name: i + self.name_count
                         for i, new_name in enumerate(new_names)}
        self.name_count += len(new_names)

        # combine new and existing name maps
        self.name_map = {**self.name_map, **new_names_map}

        # find ids of names and return them
        return [self.name_map[name] for name in name_list]

    def get_name_string(self, query_id):
        """Return the corresponding name string for name_id.

        If the name_id is not an index in the names list, return None.
        """

        # use a generator to find name string matching id,
        # None at end means None is returned if no match found
        return next((name for name, name_id in self.name_map.items()
                     if name_id == query_id), None)
