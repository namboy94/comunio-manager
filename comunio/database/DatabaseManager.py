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
import datetime
import sqlite3
from typing import Dict
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

        manager_stats = "CREATE TABLE IF NOT EXISTS manager_stats (" \
                        "date TEXT NOT NULL," \
                        "cash INTEGER NOT NULL," \
                        "team_value INTEGER NOT NULL" \
                        ");"

        self.__database.execute(player_table + player_info_table + manager_stats)
        self.__database.commit()

    def update_database(self) -> None:
        """
        Updates the local database with current information from comunio

        :return: None
        """

        date = datetime.datetime.utcnow()
        date = str(date.year).zfill(4) + "-" + str(date.month).zfill(2) + "-" + str(date.day).zfill(2)

        today_results = self.database.execute("SELECT * FROM players WHERE date = ?", (date,)).fetchall()

        if len(today_results) == 0:  # Check if today's data has already been entered

            players = self.comunio_session.get_own_player_list()
            cash = self.comunio_session.get_cash()
            teamvalue = self.comunio_session.get_team_value()

            sql = "INSERT INTO players (name, value, points, position, date) VALUES(?, ?, ?, ?, ?)"
            for player in players:
                self.database.execute(sql, (player["name"],
                                            player["value"],
                                            player["points"],
                                            player["position"],
                                            date))

            sql = "INSERT INTO assets (date, cash, teamvalue) VALUES(?, ?, ?)"
            self.database.execute(sql, (date, cash, teamvalue))

            print(self.database.execute("SELECT * FROM player_info").fetchall())

            self.database.commit()

    def


    def get_total_delta(self) -> int:
        return self.comunio.money + self.comunio.teamvalue - 40000000

    def get_player_deltas(self) -> Dict[str, str]:

        players = self.comunio.get_own_player_list()

        player_deltas = {}
        for player in players:

            name = player["name"]
            current_value = int(player["value"])

            sql = "SELECT buy_value FROM player_info WHERE name = ?"
            buy_value = int(self.database.execute(sql, (name,)).fetchall()[0][0])

            player_deltas[name] = current_value - buy_value

        return player_deltas

    def get_player_tendencies(self) -> Dict[str, str]:

        players = self.comunio.get_own_player_list()

        player_tends = {}
        for player in players:

            try:
                name = player["name"]
                current_value = int(player["value"])

                yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)
                yesterday = str(yesterday.year).zfill(4) + "-" + str(yesterday.month).zfill(2) + "-" + str(yesterday.day).zfill(2)

                sql = "SELECT value FROM players WHERE name = ? AND DATE = ?"
                yesterday_value = int(self.database.execute(sql, (name, yesterday)).fetchall())
                print(yesterday_value)

                player_tends[name] = current_value - yesterday_value
            except:
                pass

        return player_tends
