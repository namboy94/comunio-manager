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

import sys
import datetime
import sqlite3
from typing import Dict
from Comunio import Comunio


class ComunioDb(object):

    def __init__(self, username: str, password: str) -> None:
        self.comunio = Comunio(username, password)
        self.database = sqlite3.connect("database_test")
        self.update_db()

    def update_db(self) -> None:

        date = datetime.datetime.utcnow()
        date = str(date.year).zfill(4) + "-" + str(date.month).zfill(2) + "-" + str(date.day).zfill(2)

        today_results = self.database.execute("SELECT * FROM players WHERE date = ?", (date,)).fetchall()

        if len(today_results) == 0:

            players = self.comunio.get_own_player_list()
            cash = self.comunio.money
            teamvalue = self.comunio.teamvalue

            sql = "INSERT INTO players (name, value, points, position, date) VALUES(?, ?, ?, ?, ?)"
            for player in players:
                self.database.execute(sql, (player["name"], player["value"], player["points"], player["position"], date))

            sql = "INSERT INTO assets (date, cash, teamvalue) VALUES(?, ?, ?)"
            self.database.execute(sql, (date, cash, teamvalue))

            print(self.database.execute("SELECT * FROM player_info").fetchall())

            self.database.commit()

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

if __name__ == '__main__':

    db = ComunioDb(sys.argv[1], sys.argv[2])
    print("Cash:        {:,}".format(db.comunio.money))
    print("Team Value:  {:,}".format(db.comunio.teamvalue))
    print("Total Delta: {:,}\n".format(db.get_total_delta()))

    exit()

    print("Player Deltas:")
    player_deltas = db.get_player_deltas()
    for player in player_deltas:
        print((player + ": ").ljust(20) + "{:,}".format(player_deltas[player]))

    print("Player Tendencies:")
    player_tends = db.get_player_tendencies()
    for player in player_tends:
        print((player + ": ").ljust(20) + "{:,}".format(player_tends[player]))
