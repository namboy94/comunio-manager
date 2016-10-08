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
import sqlite3
from typing import Dict, List, Tuple


class SqlQueries(object):
    """
    Class that offers method calls to SQL queries.
    """

    # Schema
    @staticmethod
    def apply_sql_schema(database: sqlite3) -> None:
        """
        Applies the database schema to the database in case it is not present

        :param database: the database object to use (obtained by using sqlite3.connect())
        :return:         None
        """

        database.execute("CREATE TABLE IF NOT EXISTS players ("
                         "name TEXT NOT NULL,"
                         "position TEXT NOT NULL,"
                         "value INTEGER NOT NULL,"
                         "points INTEGER NOT NULL,"
                         "date TEXT NOT NULL"
                         ");")

        database.execute("CREATE TABLE IF NOT EXISTS player_info ("
                         "name TEXT NOT NULL,"
                         "buy_value INTEGER NOT NULL,"
                         "sell_value INTEGER"
                         ");")

        database.execute("CREATE TABLE IF NOT EXISTS manager_stats ("
                         "date TEXT NOT NULL,"
                         "cash INTEGER NOT NULL,"
                         "team_value INTEGER NOT NULL"
                         ");")
        database.commit()

    # Inserts
    @staticmethod
    def insert_player_into_players(database: sqlite3, player: Dict[str, str], date: str) -> None:
        """
        Inserts a player into the 'players' table

        :param database The database to be used
        :param player:  A dictionary with the name, value, points and position keys
        :param date:    The date on which this player should be inserted
        :return:        None
        """
        sql = "INSERT INTO players (name, value, points, position, date) VALUES(?, ?, ?, ?, ?)"
        database.execute(sql, (player["name"], player["value"], player["points"], player["position"], date))

    @staticmethod
    def insert_new_manager_stats_entry(database: sqlite3, date: str, cash: int, team_value: int) -> None:
        """
        Inserts a manager stat entry into the manager_stats table

        :param database:   the database into which the entry should be inserted into
        :param date:       the date on which the entry will be inserted
        :param cash:       the cash amount to enter
        :param team_value: the team value amount to enter
        :return:           None
        """
        sql = "INSERT INTO manager_stats (date, cash, team_value) VALUES(?, ?, ?)"
        database.execute(sql, (date, cash, team_value))

    @staticmethod
    def insert_player_info(database: sqlite3, name: str, buy_value: int, sell_value: int or None):
        """
        Inserts a new player into the 'player_info_table'
        :param database:   the database to use
        :param name:       the name of the player
        :param buy_value:  the player's buy value
        :param sell_value: the player's sell value, may be Null
        :return:           None
        """

        database.execute("INSERT INTO player_info (name, buy_value, sell_value) VALUES(?, ?, ?)",
                         (name, buy_value, sell_value))

    # Updates
    @staticmethod
    def update_player_info(database: sqlite3, name: str, buy_value: int or None, sell_value: int or None):
        """
        Updates an entry in the 'player_info' database with a new ell value or buy value.
        Both values may be given as a Null value, in which case they are skipped

        :param database:   The database to use
        :param name:       The name of the player to update
        :param buy_value:  The new buy value of the player, may be None
        :param sell_value: The new sell value of the player, may be None
        :return:           None
        """
        if buy_value is not None:
            database.execute("UPDATE player_info SET buy_value = ? WHERE name = ?", (buy_value, name))
        elif sell_value is not None:
            database.execute("UPDATE player_info SET sell_value = ? WHERE name = ?", (sell_value, name))

    # Getters
    @staticmethod
    def get_player_names_with_null_sell_value(database: sqlite3) -> List[Tuple[str]]:
        """
        Fetches all player names that were not sold yet, i.e. have a sell value of NULL

        :param database: the database to use
        :return:         the players with a NULL value, in this format: [(name1,), (name2,)]
        """
        return database.execute("SELECT name FROM player_info WHERE sell_value IS NULL").fetchall()

    @staticmethod
    def get_buy_value_of_player(database: sqlite3, name: str) -> int:
        """
        Fetches the buy value (initial value) of a player

        :param database: the database to use
        :param name:     the name of the player
        :return:         the buy value of the player
        """
        return database.execute("SELECT buy_value FROM player_info WHERE name = ?", (name,)).fetchall()[0][0]

    @staticmethod
    def get_player_list_on_date(database: sqlite3, date: str) -> List[Tuple[str, str, int, int]]:
        """
        Fetches the list of players on a given date

        :param database: the database to use
        :param date:     the date which is to consider
        :return:         the results of the SELECT query, a list of tuples of player information
                         the results are in this order:
                            - name
                            - position
                            - value
                            - points
                            - date
        """
        return database.execute("SELECT name, position, value, points, date "
                                "FROM players WHERE date = ?", (date,)).fetchall()

    @staticmethod
    def get_player_on_date(database: sqlite3, date: str, name: str) -> Tuple[str, str, int, int]:
        """
        Fetches the player information for a player on a specified date

        :param database: the database to use
        :param date:     the date which is to consider
        :param name:     the name of the player to search for
        :return:         the results of the SELECT query, a list of tuples of player information
                         the results are in this order:
                            - name
                            - position
                            - value
                            - points
                            - date
        """
        return database.execute("SELECT name, position, value, points, date FROM players WHERE date = ? AND name = ?",
                                (date, name)).fetchall()[0]

    @staticmethod
    def get_last_known_assets_values(database: sqlite3) -> Tuple[int, int]:
        """
        Fetches the last known cash and team value amounts entered in the database

        :param database: The database to be used
        :return:         The last recorded cash amount, team_value amount
        """
        assets = database.execute("SELECT cash, team_value, MAX(date) FROM manager_stats").fetchall()[0]
        return assets[0], assets[1]

    @staticmethod
    def get_first_recorded_date_of_player(database: sqlite3, name: str) -> str:
        """
        Fetches the date on which the player has first been recorded in the database

        :param database: the database to be used
        :param name:     the name of the player
        :return:         the first date that the player was recorded in the players table of the database
        """
        return database.execute("SELECT MIN(date) FROM players WHERE NAME = ?", (name, )).fetchall()[0][0]
