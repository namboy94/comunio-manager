# Comunio Manager

Comunio Manager is a program designed to help Comunio players with managing their
teams by collecting information about their player's performance and market value

This is accomplished by parsing the comunio.de website itself and storing the
parsed values in a local SQLite3 database.

## Installation

If you don't have python installed, please do so beforehand

If you have pip installed, you can simply run ```pip install comunio```
(or ```pip install comunio --user``` to install as non-root, which is probably
the preferred way to do it). 

If you can not use pip, you can also install the program by downloading the source
and running ```python setup.py install``` or ```python setup.py install --user```
in the root directory (which is the one containing a setup.py file)

## Usage

To use the program, you need to supply it with a username and password as
positional arguments. Then you can add options to make the program do what you want
it to.

**Example**: username = namboy94, password = hunter2

    comunio namboy94 hunter2
    
This will run the program, updating the database while doing so and exit.

### Options

   -g , --gui           Starts the program's GUI mode
   -u , --update        Updates the local database, then exits the program
   -l , --list          Prints a short summary of the player's account to the console
   

## Further Information

[Documentation(HTML)]()

[Documentation(PDF)]()

[Python Package Index Site]()

[Git Statistics]()

[Changelog]()