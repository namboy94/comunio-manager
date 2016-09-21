"""
LICENSE:
Copyright 2014 Javier Corbín, 2016 Hermann Krumrey

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


class Comunio:
    """
    The Comunio Web scraping class
    """

    def __init__(self, username: str, password: str) -> None:
        """
        Constructor that creates the logged in session

        :param username: the user's user name for comunio.de
        :param password: the user's password
        """
        self.username = username
        self.password = password

        self.money = 0
        self.teamvalue = 0

        self.session = requests.session()
        self.login()

    def login(self):
        """
        Logs in the user

        :return: None
        """
        payload = {'login': self.username,
                   'pass': self.password,
                   'action': 'login'}
        
        self.session.post('http://www.comunio.de/login.phtml', data=payload)
        self.load_info()
  
    def load_info(self):
        """
        Loads the user's important information

        :return: None
        """
        html = self.session.get('http://www.comunio.de/team_news.phtml').content
        soup = BeautifulSoup(html, 'html.parser')

        if soup.find('div', {'id': 'userid'}) is not None:
            self.money = int(soup.find('div', {'id': 'manager_money'}).p.text.strip().replace(".", "")[12:-2])
            self.teamvalue = int(soup.find('div', {'id': 'teamvalue'}).p.text.strip().replace(".", "")[17:-2])

    def get_own_player_list(self):
        """
        :return: A list of the user's players as a dictionary
        """
        player_list = []

        sell_html = self.session.get("http://www.comunio.de/putOnExchangemarket.phtml")
        on_sale_html = self.session.get('http://www.comunio.de/exchangemarket.phtml?takeplayeroff_x=22')
        soups = (BeautifulSoup(sell_html.text, "html.parser"), BeautifulSoup(on_sale_html.text, "html.parser"))

        for i, soup in enumerate(soups):
            players = soup.select(".tr1") + soup.select(".tr2")

            for player in players:

                attrs = player.select("td")
                if i == 0:
                    player_info = {"name": attrs[0].text.strip(),
                                   "value": attrs[2].text.strip().replace(".", ""),
                                   "points": attrs[3].text.strip(),
                                   "position": attrs[4].text.strip()}
                elif i == 1:
                    player_info = {"name": attrs[1].text.strip(),
                                   "value": attrs[4].text.strip().replace(".", ""),
                                   "points": attrs[5].text.strip(),
                                   "position": attrs[7].text.strip()}
                else:
                    player_info = {}
                player_list.append(player_info)

        return player_list
