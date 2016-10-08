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
from bs4 import BeautifulSoup
from comunio.scraper.ComunioFetcher import ComunioFetcher
from typing import Dict, List


class ComunioSession:
    """
    The Comunio Web scraping class, which stores the authenticated comunio session
    """

    def __init__(self, username: str, password: str) -> None:
        """
        Constructor that creates the logged in session. If any sort of network or authentication
        error occurs, the session switches into offline mode by unsetting the __connected flag

        :raises ReferenceError:  When the comunio account currently as 5 players for sale, which makes it impossible
                                 to fetch the market values of players not currently on sale. Thanks Comunio.
        :raises PermissionError: When the provided credentials were rejected
        :raises ConnectionError: When the connection failed due to network error
        :param username:         the user's user name for comunio.de
        :param password:         the user's password
        """
        # We don't store the username and password to avoid having this stored in memory,
        # instead, we use a session to stay logged in

        self.__cash = 0
        self.__team_value = 0
        self.__comunio_id = ""
        self.__player_name = username
        self.__screen_name = username

        self.__player_list = None
        self.__today_transfers = None
        self.__recent_news_articles = None

        self.__session = requests.session()

        self.__login(username, password)

        if len(self.__player_list) <= 5:
            raise ReferenceError("5 players on transfer list, impossible to establish market values of other players")

    def __login(self, username: str, password: str) -> None:
        """
        Logs in the user and creates a logged in session object for further queries

        :raises ConnectionError: When the connection failed due to network error
        :raises PermissionError: When the provided credentials were rejected
        :param username:         the user's user name for comunio.de
        :param password:         the user's password
        :return:                 None
        """
        payload = {"login": username,
                   "pass": password,
                   "action": 'login'}

        try:
            self.__session.post("http://www.comunio.de/login.phtml", data=payload)
            self.reload_info()
        except requests.ConnectionError:
            raise ConnectionError("Network Error")
  
    def reload_info(self) -> None:
        """
        Loads the user's most important profile information

        :raises ConnectionError: When the connection failed due to network error
        :raises PermissionError: If incorrect credentials were provided
        :return:                 None
        """
        try:
            html = self.__session.get("http://www.comunio.de/team_news.phtml").text
            soup = BeautifulSoup(html, "html.parser")

            if soup.find("div", {"id": "userid"}) is not None:

                self.__cash = int(soup.find("div", {"id": "manager_money"}).p.text.strip().replace(".", "")[12:-2])
                self.__team_value = int(soup.find("div", {"id": "teamvalue"}).p.text.strip().replace(".", "")[17:-2])
                self.__comunio_id = soup.find("div", {"id": "userid"}).p.text.strip()[6:]

                screen_name_html = self.__session.get("http://www.comunio.de/playerInfo.phtml?pid=" + self.__comunio_id)
                screen_name_soup = BeautifulSoup(screen_name_html.text, "html.parser")
                self.__player_name = screen_name_soup.find("div", {"id": "title"}).h1.text
                self.__screen_name = self.__player_name.split("\xa0")[0]

                self.__player_list = ComunioFetcher.get_own_player_list(self.__session)
                self.__recent_news_articles = ComunioFetcher.get_recent_news_articles(self.__session)
                self.__today_transfers = ComunioFetcher.get_today_transfers(self.__screen_name,
                                                                            self.__recent_news_articles)

            else:
                raise PermissionError("Log In failed, incorrect credentials")

        except requests.ConnectionError:
            raise ConnectionError("Network Error")

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

    def get_screen_name(self) -> str:
        """
        :return: The Comunio Screen Name
        """
        return self.__screen_name

    def get_own_player_list(self) -> List[Dict[str, str or int]]:
        """
        :return:  A list of the user's players as dictionaries
        """
        return self.__player_list

    def get_today_transfers(self) -> List[Dict[str, str or int]]:
        """
        :return: A list of transfer dictionaries, consisting of the following attributes:
                        - name:   the name of the player
                        - amount: the transfer amount
                        - type:   "bought" or "sold" to differentiate between the two transfer types
        """
        return self.__today_transfers

    def get_recent_news_articles(self) -> List[Dict[str, str]]:
        """
        :return: List of article dictionaries with the following attributes:
                    - date:    The article's date
                    - type:    The type of the article, e.g. 'transfers'
                    - content: The article's content
        """

        return self.__recent_news_articles
