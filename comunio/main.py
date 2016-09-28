"""
LICENSE:
Copyright 2014 Javier Corbín (MIT License), 2016 Hermann Krumrey

This file is part of comunio-manager.

    comunio-manager is a program that allows a user to track his/her comunio.de
    profile

    comunio-manager is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    comunio-manager is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with comunio-manager.  If not, see <http://www.gnu.org/licenses/>.
LICENSE
"""

# imports
import argparse
from comunio.ui.StatisticsViewer import start as start_gui
from comunio.scraper.ComunioSession import ComunioSession
from comunio.database.DatabaseManager import DatabaseManager


def main() -> None:
    """
    Starts the Program by analyzing the given command line parameters and acting accordingly

    :return: None
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("username",  help="The username with which to log in to comunio.de")
    parser.add_argument("password", help="The password with which to log in to comunio.de")
    parser.add_argument("-g", "--gui", action="store_true", help="Starts the program in GUI mode")
    args = parser.parse_args()

    try:
        comunio = ComunioSession(args.username, args.password)
    except:
        comunio = None

    database = DatabaseManager(comunio)

    if args.gui:
        start_gui(comunio, database)

if __name__ == '__main__':
    main()
