#!/usr/bin/env python3

"""Preliminary exercises for Part IIA Project GF2."""
import sys, re 
from mynames import MyNames


def open_file(path):
    """Open and return the file specified by path."""

    try:

        return open( path, "r" )

    except FileNotFoundError:

        print( "error: file", path, "was not found" )
        sys.exit()


def get_next_character(input_file):
    """Read and return the next character in input_file."""

    return input_file.read(1)


def get_next_non_whitespace_character(input_file):
    """Seek and return the next non-whitespace character in input_file."""

    next_char = get_next_character( input_file )
    
    if next_char.isspace():
        return get_next_non_whitespace_character( input_file )

    return next_char


def get_next_number(input_file):
    """Seek the next number in input_file.

    Return the number (or None) and the next non-numeric character.
    """

    builtup_string = ""
    
    while True:
    
        next_char = get_next_character( input_file )
        
        builtup_string += next_char

        match = re.search( "\D*(\d+)(\D)", builtup_string )

        if match:
            return [match.group(1), match.group(2)]

        if next_char == "":
            return [None, ""]
        
    


def get_next_name(input_file):
    """Seek the next name string in input_file.

    Return the name string (or None) and the next non-alphanumeric character.
    """

    builtup_string = ""
    
    while True:
    
        next_char = get_next_character( input_file )
        
        builtup_string += next_char

        match = re.search( "\W*([a-zA-Z]\w+)([\s\W])", builtup_string )

        if match:
            return [match.group(1), match.group(2)]

        if next_char == "":
            return [None, ""]
        


def main():
    """Preliminary exercises for Part IIA Project GF2."""

    # Check command line arguments
    arguments = sys.argv[1:]
    
    if len(arguments) != 1:
        print("Error! One command line argument is required.")
        sys.exit()

    else:

        file_path = sys.argv[-1]

        # Print the path provided and try to open the file for reading

        print( "Provided file path:", file_path ) 
        print("\nNow opening file...")

        file_object = open_file( file_path ) 

        print("\nNow reading file...")
        # Print out all the characters in the file, until the end of file

        while True:
            
            next_char = get_next_character( file_object ) 
            print( next_char, end="" )

            if next_char == "":
                break
            

        print("\nNow skipping spaces...")
        # Print out all the characters in the file, without spaces

        file_object.seek(0)

        while True:
            
            next_char = get_next_non_whitespace_character( file_object ) 
            print( next_char, end="" )

            if next_char == "":
                break
            
        print("\nNow reading numbers...")
        # Print out all the numbers in the file

        file_object.seek(0)

        while True:
            
            number_and_next_char = get_next_number( file_object ) 
 
            if number_and_next_char[0] is None:
                break
             
            print( number_and_next_char[0], end=" " )

        print("\nNow reading names...")
        # Print out all the names in the file

        file_object.seek(0)

        while True:
            
            name_and_next_char = get_next_name( file_object ) 
 
            if name_and_next_char[0] is None:
                break
             
            print( name_and_next_char[0], end=" " )

        print("\nNow censoring bad names...")
        # Print out only the good names in the file
        name = MyNames()
        bad_name_ids = [name.lookup("Terrible"), name.lookup("Horrid"),
                        name.lookup("Ghastly"), name.lookup("Awful")]

        file_object.seek(0)

        while True:
            
            name_and_next_char = get_next_name( file_object ) 
 
            if name_and_next_char[0] is None:
                break
            
            if name.lookup( name_and_next_char[0] ) > 3:
                print( name_and_next_char[0], end=" " )
       

        print( "\nclosing file" )
        file_object.close()


if __name__ == "__main__":
    main()



