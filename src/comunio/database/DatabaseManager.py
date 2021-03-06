"""
LICENSE:
Copyright 2016 Hermann Krumrey

This file is part of comunio-manager.

    comunio-manager is a program that allows a user to track his/her comunio.de
    profile

    comunio-manager is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
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
import os
import sqlite3
import datetime
from typing import Dict, List
from comunio.database.SqlQueries import SqlQueries
from comunio.scraper.ComunioSession import ComunioSession


class DatabaseManager(object):
    """
    Class that manages the local comunio database
    """

    def __init__(self, comunio_session: ComunioSession, database_location_override: str = "") -> None:
        """
        Initializes the DatabaseManager object using a previously established comunio session

        :param comunio_session:             A previously established comunio session
                                            The database won't be able to update in offline mode
        :param database_location_override:  Overrules the standard database location. Useful for testing
        """
        self.__date = self.__create_sqlite_date(0)

        if not database_location_override:
            comunio_dir = os.path.join(os.path.expanduser("~"), ".comunio")
            database_path = os.path.join(comunio_dir, "history.db")

            if not os.path.isdir(comunio_dir):
                os.makedirs(comunio_dir)

        else:
            database_path = database_location_override

        self.__comunio_session = comunio_session
        self.__database = sqlite3.connect(database_path)
        SqlQueries.apply_sql_schema(self.__database)

        self.update_database()

    # noinspection PyMethodMayBeStatic
    def __create_sqlite_date(self, day: int = 0) -> str:
        """
        Creates a date string in the format YYYY-MM-DD for a given day:

        0 is today, 1 is tomorrow, -1 is yesterday

        :param day: the day to format
        :return: the formatted date
        """
        date = datetime.datetime.utcnow()

        if day > 0:
            date += datetime.timedelta(days=day)
        elif day < 0:
            date -= datetime.timedelta(days=-(1 * day))

        return str(date.year).zfill(4) + "-" + str(date.month).zfill(2) + "-" + str(date.day).zfill(2)

    def __update_players_table(self) -> None:
        """
        Updates the 'players' table

        :raises
        :return: None
        """
        players = self.__comunio_session.get_own_player_list()
        for player in players:
            SqlQueries.insert_player_into_players(self.__database, player, self.__date)

    def __update_manager_stats_table(self) -> None:
        """
        Updates the 'manager_stats' table
        :return: None
        """
        SqlQueries.insert_new_manager_stats_entry(self.__database,
                                                  self.__date,
                                                  self.__comunio_session.get_cash(),
                                                  self.__comunio_session.get_team_value())

    def __update_transfers_from_news(self) -> None:
        """
        Updates transfers based on today's comunio news articles. Most accurate way of updating a transfer

        :return: None
        """
        transfers = self.__comunio_session.get_today_transfers()
        for transfer in transfers:
            if transfer["type"] == "bought":
                SqlQueries.insert_player_info(self.__database, transfer["name"], transfer["amount"], None)
            else:
                SqlQueries.update_player_info(self.__database, transfer["name"], None, transfer["amount"])

    def __update_transfers_from_unregistered_player(self) -> None:
        """
        Updates the transfers based on unregistered players, i.e. a player that appears in today's
        comunio team but not in the player_info table.

        Data loss occurs with this method, since the market value is registered as the buy_value instead
        of the actual price

        :return: None
        """

        player_infos = SqlQueries.get_player_names_with_null_sell_value(self.__database)

        for player in self.get_players_on_day(0):
            if (player["name"],) not in player_infos:
                SqlQueries.insert_player_info(self.__database, player["name"], player["value"], None)

    def __update_transfers_from_missing_player(self) -> None:
        """
        Updates transfers based on players that appear in the player_info and do not have a non-NULL sell_value
        but do not appear in today's list of players.

        This method is prone to loss of information, since the new sell_value is determined by using the last known
        market value. If an appropriate previous market value was not found in the last 15 entries, the
        initial buy_value is used.

        :return: None
        """
        player_infos = SqlQueries.get_player_names_with_null_sell_value(self.__database)

        for player in player_infos:

            is_still_in_team = False
            for today_player in self.get_players_on_day(0):
                if today_player["name"] == player[0]:
                    is_still_in_team = True
                    break

            if not is_still_in_team:

                market_value = None
                day_counter = -1

                while market_value is None:
                    for older_player in self.get_players_on_day(day_counter):
                        if older_player["name"] == player:
                            market_value = older_player["value"]
                            break

                    day_counter -= 1

                    if day_counter < 15:
                        market_value = SqlQueries.get_buy_value_of_player(self.__database, player[0])

                SqlQueries.update_player_info(self.__database, player[0], None, market_value[0])

    def update_database(self) -> None:
        """
        Updates the local database with current information from comunio

        :return: None
        """
        today_results = SqlQueries.get_player_list_on_date(self.__database, self.__date)
        if len(today_results) == 0:  # Check if today's data has already been entered

            self.__update_players_table()
            self.__update_manager_stats_table()
            self.__update_transfers_from_news()
            self.__update_transfers_from_missing_player()
            self.__update_transfers_from_unregistered_player()
            self.__database.commit()

    def get_players_on_day(self, day: int = 0) -> List[Dict[str, str or int]]:
        """
        Fetches a list of player dictionaries from the local database on the given day relative
        to the current day.

        The format of these dictionaries is:

        name:     The player's name
        value:    The player's current value
        points:   The player's currently accumulated performance points
        position: The player's position
        date:     The associated date as a formatted string

        :param day:         The requested day, relative to the current date.
                                Example: day = -1 returns the list for yesterday
        :raises ValueError: If a day larger than one is given, since we're not fortune tellers
        :return:            The list of player dictionaries
        """
        if day > 0:
            raise ValueError("Day must be 0 or negative")

        date = self.__create_sqlite_date(day)
        players = []
        database_results = SqlQueries.get_player_list_on_date(self.__database, date)

        for result in database_results:
            player = {
                "name": result[0],
                "position": result[1],
                "value": result[2],
                "points": result[3],
                "date": result[4]
            }
            players.append(player)

        return players

    def get_player_on_day(self, name: str, day: int = 0) -> Dict[str, str or int] or None:
        """
        Fetches the current information for a single player specified by name. The information is
        returned as a dictionary in the following format:

        name:     The player's name
        value:    The player's current value
        points:   The player's currently accumulated performance points
        position: The player's position
        date:     The date associated with this data point

        :param name: the name of the player
        :param day:  the requested day
        :return:     Dictionary containing the player's information, if no entry was found however, return None
        """
        date = self.__create_sqlite_date(day)
        try:
            player_info = SqlQueries.get_player_on_date(self.__database, date, name)
            return {
                "name": player_info[0],
                "position": player_info[1],
                "value": player_info[2],
                "points": player_info[3],
                "date": player_info[4]
            }
        except IndexError:
            return None

    def get_player_buy_values(self) -> Dict[str, int]:
        """
        Fetches all player's buy values, i.e. the price for which they were bought
        Players that were already sold are ignored

        :return: the player buy values as a dictionary with the player names as key and the values as content
        """
        buy_values = {}
        players = SqlQueries.get_player_names_with_null_sell_value(self.__database)

        for player in players:
            buy_values[player[0]] = player[1]
        return buy_values

    def get_player_buy_value(self, name: str) -> int:
        """
        Fetches a single player's buy value

        :param name: the name of the player
        :return: the buy value
        """
        return SqlQueries.get_buy_value_of_player(self.__database, name)

    def get_last_cash_amount(self) -> int:
        """
        :return: The last recorded cash amount
        """
        return SqlQueries.get_last_known_assets_values(self.__database)[0]

    def get_last_team_value_amount(self) -> int:
        """
        :return: The last recorded team value
        """
        return SqlQueries.get_last_known_assets_values(self.__database)[1]

    def get_historic_data_for_player(self, player: str) -> List[Dict[str, str or int]]:
        """
        Retrieves the data of a player over time as a list of reversely-chronologically sorted values

        :param player: The player for which the history should be retrieved
        :return:       The list of values, reversely chronologically sorted, as dictionaries with player information
        """
        values = []

        day = 0
        while True:
            player_on_day = self.get_player_on_day(player, day)
            if player_on_day is not None:
                values.append(player_on_day)
            else:
                date = self.__create_sqlite_date(day)
                lowest_date = SqlQueries.get_first_recorded_date_of_player(self.__database, player)
                if date < lowest_date:
                    break

            day -= 1

        return values
