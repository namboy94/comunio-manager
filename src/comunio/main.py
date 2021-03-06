"""
LICENSE:
Copyright 2016 Hermann Krumrey

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

# These imports are necessary to get PyInstaller to actually bundle all required modules
# when creating a binary executable

# noinspection PyUnresolvedReferences
import tkinter
# noinspection PyUnresolvedReferences
import tkinter.filedialog
# noinspection PyUnresolvedReferences
import matplotlib.backends.backend_tkagg

# Suppresses Matplotlib warnings
import warnings
warnings.filterwarnings("ignore", module="matplotlib")

# imports
import sys
import argparse
from typing import Dict, List
from argparse import Namespace
from comunio.metadata import SentryLogger
from comunio.ui.LoginScreen import start as start_logi_gui
from comunio.ui.StatisticsViewer import start as start_gui
from comunio.scraper.ComunioSession import ComunioSession
from comunio.database.DatabaseManager import DatabaseManager
from comunio.calc.StatisticsCalculator import StatisticsCalculator
from comunio.credentials.CredentialsManager import CredentialsManager


def parse_arguments() -> Namespace:
    """
    Parses the command line aruments

    :return: the arguments as an argsparse namespace
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--gui", action="store_true",
                        help="Starts the program in GUI mode")
    parser.add_argument("-u", "--username",
                        help="The username with which to log in to comunio.de")
    parser.add_argument("-p", "--password",
                        help="The password with which to log in to comunio.de")
    parser.add_argument("-k", "--keep_creds", action="store_true",
                        help="Stores the given credentials in a local config file")
    parser.add_argument("-r", "--refresh", action="store_true",
                        help="Only updates the database, then quits")
    parser.add_argument("-s", "--summary", action="store_true",
                        help="Lists the current state of the comunio account")
    parser.add_argument("-x", "--xkcd", action="store_true",
                        help="Displays graphs generated by Matplotlib in the style of XKCD webcomics")
    return parser.parse_args()


def main() -> None:
    """
    Starts the Program by analyzing the given command line parameters and acting accordingly

    :return: None
    """
    try:

        args = parse_arguments()

        if args.username and args.password:
            credentials = CredentialsManager((args.username, args.password))
        else:
            credentials = CredentialsManager()

        handle_gui(vars(args), credentials) if args.gui else handle_cli(vars(args), credentials)

    except Exception as e:
        SentryLogger.sentry.captureException()
        raise e


def handle_cli(args: Dict[str, object], credentials: CredentialsManager) -> None:
    """
    Handles the behavious of the CLI of the program

    :param args:        the previously parsed console arguments
    :param credentials: the previously defined credential manager
    :return:            None
    """
    if credentials.get_credentials() == ("", ""):
        print("Please supply a username and password:\n")
        print("    Either via the --password and the --username parameters")
        print("        OR")
        print("    The config file found in " + credentials.get_config_file_location())
        sys.exit(1)

    if not args["refresh"] and not args["summary"]:
        print("No valid options passed. See the --help option for more information")
        sys.exit(1)

    if args["keep_creds"]:
        credentials.store_credentials()

    try:
        comunio = ComunioSession(credentials.get_credentials()[0], credentials.get_credentials()[1])
        database = DatabaseManager(comunio)
        calculator = StatisticsCalculator(comunio, database)

        if args["refresh"]:
            database.update_database()
            print("Database Successfully Updated")

        elif args["summary"]:
            print("\nCash:       {:,}".format(database.get_last_cash_amount()))
            print("Team value: {:,}".format(database.get_last_team_value_amount()))
            print("Balance:    {:,}".format(calculator.calculate_total_assets_delta()))
            print("\nPlayers:\n")

            players = database.get_players_on_day(0)
            print_player_list(players)

        else:
            print("No valid options passed. See the --help option for more information")

    except ReferenceError:
        print("Player data unavailable due to having 5 players on the transfer list.")
        print("Please Remove a player from the transfer list to continue.")
        print("The program will now exit")
    except ConnectionError:
        print("Connection to Comunio failed due to Network error")
    except PermissionError:
        print("The provided credentials are invalid")


def print_player_list(players: List[Dict[str, str]]) -> None:
    """
    Prints the player list in a nicely viewable table on the console

    :param players: the list of players
    :return:        None
    """
    players.append({"position": "Position", "name": "Name", "value": "Value", "points": "Points"})  # Header

    position_max_length = max(len(player["position"]) for player in players)
    name_max_length = max(len(player["name"]) for player in players)
    value_max_length = max(len(str(player["value"])) for player in players)
    points_max_length = max(len(str(player["points"])) for player in players)

    sorted_players = []
    order = ["Position", "Torhüter", "Abwehr", "Mittelfeld", "Sturm"]
    for position in order:
        for player in players:
            if player["position"] == position:
                player["points_graph"] = None
                player["value_graph"] = None
                sorted_players.append(player)

    for player in sorted_players:
        table_entry = "| " + player["position"].ljust(position_max_length) + " | "
        table_entry += player["name"].ljust(name_max_length) + " | "
        table_entry += str(player["value"]).ljust(value_max_length) + " | "
        table_entry += str(player["points"]).ljust(points_max_length) + " |"
        print(table_entry)


def handle_gui(args: Dict[str, object], credentials: CredentialsManager) -> None:
    """
    Handles the GUI initialization of the program

    :param args:        the arguments passed by argparse
    :param credentials: the previously defined credential manager
    :return:            None
    """
    comunio = start_logi_gui(credentials)
    if comunio is not None:
        database = DatabaseManager(comunio)
        calculator = StatisticsCalculator(comunio, database, bool(args["xkcd"]))
        start_gui(comunio, database, calculator)


if __name__ == "__main__":
    if sys.platform == "win32" and len(sys.argv) == 1:  # Automatically start in GUI mode when using windows,
        sys.argv.append("-g")                           # but only if no arguments were passed
    main()
