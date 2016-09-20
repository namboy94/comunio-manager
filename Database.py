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
from Comunio import Comunio


def update_db(username, password):

    date = datetime.datetime.utcnow()
    date = "{0}-{1}-{2}".format(date.year, date.month, date.day)

    database = sqlite3.connect("database")
    today_results = database.execute("SELECT * FROM players WHERE date = ?", (date,)).fetchall()

    if len(today_results) != 0:
        return

    comunio = Comunio(username, password)
    print(comunio.money)
    players = comunio.get_own_player_list()

    query = "INSERT INTO players (name, value, points, position, date) VALUES(?, ?, ?, ?, ?)"
    for player in players:
        database.execute(query, (player["name"], player["value"], player["points"], player["position"], date))
    database.commit()

if __name__ == '__main__':


    update_db(sys.argv[0], sys.argv[1])