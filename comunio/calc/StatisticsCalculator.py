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
from comunio.scraper.ComunioSession import ComunioSession
from comunio.database.DatabaseManager import DatabaseManager


class StatisticsCalculator(object):
    """
    Class that calculates various statistics based on the current comunio data and the local database
    """

    def __init__(self, comunio_session: ComunioSession, database_manager: DatabaseManager) -> None:
        """
        Initializes the statistics calculator with a running comunio session and a database manager
        to interface with the local database

        :param comunio_session:  the comunio session
        :param database_manager: the database manager
        """
        self.__comunio_session = comunio_session
        self.__database_manager = database_manager

    def calculate_total_assets_delta(self) -> int:
        """
        Calculates the difference of the player's current assets compared to the beginning of the season.
        The season is started with 40.000.000€ in cash

        :return: the difference between the values
        """
        assets = self.__database_manager.get_last_cash_amount() + self.__database_manager.get_last_team_value_amount()
        return assets - 40000000
