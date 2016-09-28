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
import os
import sqlite3
import datetime
from typing import Dict, List
from comunio.scraper.ComunioSession import ComunioSession


class DatabaseManager(object):
    """
    Class that manages the local comunio database
    """

    def __init__(self, comunio_session: ComunioSession) -> None:
        """
        Initializes the DatabaseManager object using a previously established comunio session

        :param comunio_session: A previously established comunio session
        """
        date = datetime.datetime.utcnow()
        self.__date = str(date.year).zfill(4) + "-" + str(date.month).zfill(2) + "-" + str(date.day).zfill(2)

        comunio_dir = os.path.join(os.path.expanduser("~"), ".comunio")
        database_path = os.path.join(comunio_dir, "history.db")

        if not os.path.isdir(comunio_dir):
            os.makedirs(comunio_dir)

        self.__comunio_session = comunio_session
        self.__database = sqlite3.connect(database_path)
        self.__apply_schema()
        self.update_database()

    def __apply_schema(self) -> None:
        """
        Ensures that the correct schema is present in the connected database file

        :return: None
        """
        player_table = "CREATE TABLE IF NOT EXISTS players (" \
                       "name TEXT NOT NULL," \
                       "position TEXT NOT NULL," \
                       "value INTEGER NOT NULL," \
                       "points INTEGER NOT NULL," \
                       "date TEXT NOT NULL" \
                       ");"

        player_info_table = "CREATE TABLE IF NOT EXISTS player_info (" \
                            "name TEXT NOT NULL," \
                            "buy_value INTEGER NOT NULL," \
                            "sell_value INTEGER" \
                            ");"

        manager_stats_table = "CREATE TABLE IF NOT EXISTS manager_stats (" \
                              "date TEXT NOT NULL," \
                              "cash INTEGER NOT NULL," \
                              "team_value INTEGER NOT NULL" \
                              ");"

        self.__database.execute(player_table)
        self.__database.execute(player_info_table)
        self.__database.execute(manager_stats_table)
        self.__database.commit()

    def __update_players_table(self) -> None:
        """
        Updates the 'players' table

        :return: None
        """
        players = self.__comunio_session.get_own_player_list()

        sql = "INSERT INTO players (name, value, points, position, date) VALUES(?, ?, ?, ?, ?)"
        for player in players:
            self.__database.execute(sql, (player["name"],
                                          player["value"],
                                          player["points"],
                                          player["position"],
                                          self.__date))
        self.__database.commit()

    def __update_manager_stats_table(self) -> None:
        """
        Updates the 'manager_stats' table
        :return: None
        """
        sql = "INSERT INTO manager_stats (date, cash, team_value) VALUES(?, ?, ?)"
        self.__database.execute(sql, (self.__date,
                                      self.__comunio_session.get_cash(),
                                      self.__comunio_session.get_team_value()))
        self.__database.commit()

    def __update_transfers(self) -> None:
        """
        Updates transfers from the comunio website and adds them into the database

        :return: None
        """
        # TODO split up method into individual methods

        # Check for Transfers using Comunio's news section for today
        transfers = self.__comunio_session.get_today_transfers()
        for transfer in transfers:
            if transfer["type"] == "bought":
                self.__database.execute("INSERT INTO player_info (name, buy_value, sell_value) VALUES(?, ?, NULL)",
                                        (transfer["name"], transfer["value"]))
            else:
                self.__database.execute("UPDATE player_info SET sell_value = ? WHERE name = ?",
                                        (transfer["value"], transfer["name"]))

        player_infos = self.__database.execute("SELECT name FROM player_info WHERE sell_value = NULL").fetchall()

        # Insert any missing players wit today's market value
        for player in self.get_players_on_day(0):
            if player["name"] not in player_infos:
                self.__database.execute("INSERT INTO player_info (name, buy_value, sell_value) VALUES(?, ?, NULL)",
                                        (player["name"], player["value"]))

        # Mark every player that is no longer in the team as sold using the last known market value
        for player in player_infos:

            is_still_in_team = False
            for today_player in self.get_players_on_day(0):
                if today_player["name"] == player:
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
                        market_value = self.__database.execute("SELECT buy_value FROM player_info WHERE name = ?",
                                                               (player,)).fetchall()[0]

                self.__database.execute("UPDATE player_info SET sell_value = ? WHERE name = ?",
                                        (market_value, player))

        self.__database.commit()

    def update_database(self) -> None:
        """
        Updates the local database with current information from comunio

        :return: None
        """
        today_results = self.__database.execute("SELECT * FROM players WHERE date = ?", (self.__date,)).fetchall()

        if len(today_results) == 0:  # Check if today's data has already been entered

            self.__update_players_table()
            self.__update_manager_stats_table()
            self.__update_transfers()

    def get_players_on_day(self, day: int = 0) -> List[Dict[str, str or int]]:
        """
        Fetches a list of player dictionaries from the local database on the given day relative
        to the current day.

        The format of these dictionaries is:

        name:     The player's name
        value:    The player's current value
        points:   The player's currently accumulated performance points
        position: The player's position

        :param day:         The requested day, relative to the current date.
                                Example: day = -1 returns the list for yesterday
        :raises ValueError: If a day larger than one is given, since we're not fortune tellers
        :return:            The list of player dictionaries
        """
        if day > 0:
            raise ValueError("Day must be 0 or negative")

        date = datetime.datetime.utcnow() - datetime.timedelta(days=(day * -1))
        date = str(date.year).zfill(4) + "-" + str(date.month).zfill(2) + "-" + str(date.day).zfill(2)

        players = []
        database_results = self.__database.execute("SELECT * FROM players WHERE date = ?", (date, )).fetchall()

        for result in database_results:
            player = {
                "name": result[0],
                "position": result[1],
                "value": result[2],
                "points": result[3]
            }
            players.append(player)

        return players

    def get_player_buy_values(self) -> Dict[str, int]:
        """
        Fetches all player's buy values, i.e. the price for which they were bought
        Players that were already sold are ignored

        :return: the player buy values as a dictionary with the player names as key and the values as content
        """
        buy_values = {}
        players = self.__database.execute("SELECT * FROM player_info WHERE sell_value IS NULL").fetchall()

        for player in players:
            buy_values[player[0]] = player[1]
        return buy_values
