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
from PyQt5.QtWidgets import QMainWindow, QApplication, QHeaderView


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

        self.__comunio_session = comunio_session
        self.__database_manager = database_manager
        self.__statistics_calculator = StatisticsCalculator(comunio_session, database_manager)

        for i in range(0, 8):  # Makes headers all the same size
            self.player_table.header().setSectionResizeMode(i, QHeaderView.Stretch)

        if comunio_session is not None:
            cash = comunio_session.get_cash()
            team_value = comunio_session.get_team_value()
            display_name = comunio_session.get_screen_name()
        else:
            cash = database_manager.get_last_cash_amount()#team_value = database_manager.get_last_team_value_amount()
            display_name = "offline viewing"

        print(cash)

        self.greeting_label.setText(self.greeting_label.text().replace("<username>", display_name))
        self.cash_display.setText("{}".format(cash))


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
