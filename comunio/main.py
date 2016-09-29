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
from comunio.calc.StatisticsCalculator import StatisticsCalculator


def main() -> None:
    """
    Starts the Program by analyzing the given command line parameters and acting accordingly

    :return: None
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("username",  help="The username with which to log in to comunio.de")
    parser.add_argument("password", help="The password with which to log in to comunio.de")
    parser.add_argument("-g", "--gui", action="store_true", help="Starts the program in GUI mode")
    parser.add_argument("-u", "--update", action="store_true", help="Only updates the database, then quits")
    parser.add_argument("-s", "--summary", action="store_true", help="Lists the current state of the comunio account")
    args = parser.parse_args()

    comunio = ComunioSession(args.username, args.password)
    database = DatabaseManager(comunio)
    calculator = StatisticsCalculator(comunio, database)

    if args.gui:
        start_gui(comunio, database)
    elif args.list:
        print("Cash:       {:,}".format(database.get_last_cash_amount()))
        print("Team value: {:,}".format(database.get_last_team_value_amount()))
        print("Balance:    {:,}".format(calculator.calculate_total_assets_delta()))
        print("\n\nPlayers:\n")
        for player in database.get_players_on_day(0):
            print(player)
    elif args.update:
        database.update_database()

if __name__ == '__main__':
    main()
