"""
LICENSE:
Copyright 2014 Javier Corbín (MIT License), 2016 Hermann Krumrey

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
import requests
from typing import Dict
from bs4 import BeautifulSoup


class ComunioSession:
    """
    The Comunio Web scraping class, which stores the authenticated comunio session
    """

    def __init__(self, username: str, password: str) -> None:
        """
        Constructor that creates the logged in session

        :param username:         the user's user name for comunio.de
        :param password:         the user's password
        :raises ConnectionError: When the log in process failed. Exception message contains the
                                 details of the cause of the exception
        """
        # We don't store the username and password to avoid having this stored in memory,
        # instead, we use a session to stay logged in

        self.__cash = 0
        self.__team_value = 0
        self.__comunio_id = ""
        self.__player_name = ""
        self.__screen_name = ""

        self.__session = requests.session()

        # Can raise Exception on wrong credentials, unexpected network state
        # and whenever comunio.de blocks the site for any non-pro users
        try:
            self.__login(username, password)
        except requests.exceptions.ConnectionError:
            raise ConnectionError("Network Error")

    def __login(self, username: str, password: str) -> None:
        """
        Logs in the user and creates a logged in session object for further queries

        :param username: the user's user name for comunio.de
        :param password: the user's password
        :return:         None
        """
        payload = {"login": username,
                   "pass": password,
                   "action": 'login'}
        
        self.__session.post("http://www.comunio.de/login.phtml", data=payload)
        self.__load_info()
  
    def __load_info(self) -> None:
        """
        Loads the user's most important profile information

        :raises ConnectionError: if the log in process failed
        :return:                 None
        """
        html = self.__session.get("http://www.comunio.de/team_news.phtml").text
        soup = BeautifulSoup(html, "html.parser")

        if soup.find("div", {"id": "userid"}) is not None:

            self.__cash = int(soup.find("div", {"id": "manager_money"}).p.text.strip().replace(".", "")[12:-2])
            self.__team_value = int(soup.find("div", {"id": "teamvalue"}).p.text.strip().replace(".", "")[17:-2])
            self.__comunio_id = soup.find("div", {"id": "userid"}).p.text.strip()[6:]

            screen_name_html = self.__session.get(
                "http://www.comunio.de/playerInfo.phtml?pid=" + self.__comunio_id).text
            screen_name_soup = BeautifulSoup(screen_name_html, "html.parser")

            self.__player_name = screen_name_soup.find("div", {"id": "title"}).h1.text
            self.__screen_name = self.__player_name.split("\xa0")[0]

        else:
            raise ConnectionError("Log In failed, incorrect credentials?")

    def get_cash(self) -> int:
        """
        :return: The player's current amount of liquid assets
        """
        return self.__cash

    def get_team_value(self) -> int:
        """
        :return: The player's team's current market value on comunio
        """
        return self.__team_value

    def get_own_player_list(self) -> Dict[str, str or int]:
        """
        Creates dictionaries modelling the user's current players and returns them
        in a list.

        The format of these dictionaries is:

        name:     The player's name
        value:    The player's current value
        points:   The player's currently accumulated performance points
        position: The player's position

        :return:  A list of the user's players as dictionaries
        """
        player_list = []

        sell_html = self.__session.get("http://www.comunio.de/putOnExchangemarket.phtml")
        on_sale_html = self.__session.get("http://www.comunio.de/exchangemarket.phtml?takeplayeroff_x=22")
        soups = (BeautifulSoup(sell_html.text, "html.parser"), BeautifulSoup(on_sale_html.text, "html.parser"))

        for i, soup in enumerate(soups):
            players = soup.select(".tr1") + soup.select(".tr2")

            for player in players:

                attrs = player.select("td")
                if i == 0:
                    player_info = {"name": attrs[0].text.strip(),
                                   "value": int(attrs[2].text.strip().replace(".", "")),
                                   "points": int(attrs[3].text.strip()),
                                   "position": attrs[4].text.strip()}
                elif i == 1:
                    player_info = {"name": attrs[1].text.strip(),
                                   "value": int(attrs[4].text.strip().replace(".", "")),
                                   "points": int(attrs[5].text.strip()),
                                   "position": attrs[7].text.strip()}
                else:
                    player_info = {}
                player_list.append(player_info)

        return player_list
