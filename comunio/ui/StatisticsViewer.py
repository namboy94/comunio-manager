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


# imports
import sys
from comunio.ui.stats import Ui_StatisticsWindow
from comunio.scraper.ComunioSession import ComunioSession
from comunio.database.DatabaseManager import DatabaseManager
from comunio.calc.StatisticsCalculator import StatisticsCalculator
from PyQt5.QtWidgets import QMainWindow, QApplication, QHeaderView, QTreeWidgetItem


class StatisticsViewer(QMainWindow, Ui_StatisticsWindow):
    """
    Class that models the QT GUI for displaying Comunio statistics
    """

    def __init__(self, comunio_session: ComunioSession, database_manager: DatabaseManager,
                 parent: QMainWindow = None) -> None:
        """
        Sets up the interactive UI elements

        :param comunio_session:  An initialized comunio session, or None
        :param database_manager: An initialized Database Manager object
        :param parent:           The parent window
        """
        super().__init__(parent)
        self.setupUi(self)

        self.__players = []

        self.__comunio_session = comunio_session
        self.__database_manager = database_manager
        self.__statistics_calculator = StatisticsCalculator(comunio_session, database_manager)

        for i in range(0, 8):  # Makes headers all the same size
            self.player_table.header().setSectionResizeMode(i, QHeaderView.Stretch)

        cash = database_manager.get_last_cash_amount()
        team_value = database_manager.get_last_team_value_amount()
        display_name = comunio_session.get_screen_name()

        self.greeting_label.setText(self.greeting_label.text().replace("<username>", display_name))
        self.cash_display.setText("{:,}€".format(cash))
        self.team_value_display.setText("{:,}€".format(team_value))

        self.total_assets_display.setText("{:,}".format(cash + team_value))
        self.balance_display.setText("{:,}".format(self.__statistics_calculator.calculate_total_assets_delta()))

        self.__fill_player_table()

        self.player_table.itemSelectionChanged.connect(self.__select_player)

    def __fill_player_table(self) -> None:
        """
        Fills the player table with the current data in the local database
        :return: None
        """
        unordered_players = self.__database_manager.get_players_on_day(0)
        players = []

        # Sort the player entries
        order = ["Torhüter", "Abwehr", "Mittelfeld", "Sturm"]
        for position in order:
            for player in unordered_players:
                if player["position"] == position:
                    players.append(player)

        for player in players:

            self.__players.append(player)

            position = player["position"]
            name = player["name"]
            points = str(player["points"])
            current_value = player["value"]
            buy_value = self.__database_manager.get_player_buy_value(name)
            total_player_delta = current_value - buy_value

            yesterday_value = self.__database_manager.get_player_on_day(name, -1)
            try:
                yesterday_value = yesterday_value["value"]
                tendency = current_value - yesterday_value
                yesterday_value = "{:,}".format(yesterday_value)
                tendency = "{:,}€".format(tendency)
            except TypeError:
                yesterday_value = "---"
                tendency = "---"

            buy_value = "{:,}".format(buy_value)
            current_value = "{:,}€".format(current_value)
            total_player_delta = "{:,}€".format(total_player_delta)

            self.player_table.addTopLevelItem(QTreeWidgetItem([position,
                                                               name,
                                                               points,
                                                               buy_value,
                                                               yesterday_value,
                                                               current_value,
                                                               total_player_delta,
                                                               tendency]))

    def __select_player(self) -> None:
        """
        Called whenever the user selects a player from the table. Fills the side info and generates
        the value history graph

        :return: None
        """
        player = self.__players[self.player_table.selectedIndexes()[0].row()]

        self.player_name_label.setText(player["name"])
        self.player_position_label.setText(player["position"])
        self.player_points_label.setText(str(player["points"]))
        self.player_value_label.setText("{:,}".format(player["value"]))
        self.fill_player_value_graph(player["name"])

    def fill_player_value_graph(self, player: str) -> None:
        """
        Fills the player value graph widget with a graph displaying the player's previous values
        over time

        :param player: The name of the player whose graph should be generated
        :return:       None
        """
        historic_data = self.__database_manager.get_historic_values_for_player(player)
        # TODO Fill the graph


def start(comunio_session: ComunioSession or None, database_manager: DatabaseManager) -> None:
    """
    Starts the Statistics Viewer GUI.

    :param comunio_session:  An initialized comunio session, or None
    :param database_manager: An initialized Database Manager object
    :return:                 None
    """
    app = QApplication(sys.argv)
    form = StatisticsViewer(comunio_session, database_manager)
    form.show()
    app.exec_()
