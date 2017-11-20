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
import datetime
from typing import List, Dict
from bs4 import BeautifulSoup


class ComunioFetcher(object):
    """
    A class containing various methods for parsing information from comunio.de
    """

    @staticmethod
    def get_own_player_list(session: requests.session) -> List[Dict[str, str or int]]:
        """
        Creates dictionaries modelling the user's current players and returns them
        in a list.

        The format of these dictionaries is:

        name:     The player's name
        value:    The player's current value
        points:   The player's currently accumulated performance points
        position: The player's position

        :param:   The requests session initialized by the ComunioSession
        :return:  A list of the user's players as dictionaries
        """
        player_list = []

        sell_html = session.get("http://www.comunio.de/putOnExchangemarket.phtml")
        on_sale_html = session.get("http://www.comunio.de/exchangemarket.phtml?takeplayeroff_x=22")
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

    @staticmethod
    def get_today_transfers(screen_name: str, recent_news: List[Dict[str, str]]) \
            -> List[Dict[str, str or int]]:
        """
        Fetches the transfer activity for today from comunio's news section. Only fetches
        transfers related to the logged in player

        :param screen_name:   The user's screen name
        :param recent_news:   The recent news as parsed by get_recent_news_articles()
        :return:              A list of transfer dictionaries, consisting of the following attributes:
                                    - name:   the name of the player
                                    - amount: the transfer amount
                                    - type:   "bought" or "sold" to differentiate between the two transfer types
        """
        date = datetime.datetime.utcnow()
        date = str(date.day).zfill(2) + "." + str(date.month).zfill(2) + "." + str(date.year)[2:4]

        transfers = []
        for article in recent_news:
            if article["type"] == "Transfers" and article["date"] == date:

                transfer_text = article["content"]

                while True:
                    player_name, transfer_text = transfer_text.split(" wechselt für ", 1)
                    amount, transfer_text = transfer_text.split(" von ", 1)
                    seller_name, transfer_text = transfer_text.split(" zu ", 1)
                    buyer_name, transfer_text = transfer_text.split(".", 1)

                    transfer = {"name": player_name,
                                "amount": int(amount.replace(".", ""))}

                    if seller_name == screen_name or buyer_name == screen_name:
                        transfer["type"] = "bought" if buyer_name == screen_name else "sold"
                        transfers.append(transfer)

                    if len(transfer_text) == 0:
                        break

        return transfers

    @staticmethod
    def get_recent_news_articles(session: requests.session) -> List[Dict[str, str]]:
        """
        Fetches the most recent news articles for the logged in player

        :param:  The requests session initialized by the ComunioSession
        :return: List of article dictionaries with the following attributes:
                    - date:    The article's date
                    - type:    The type of the article, e.g. 'transfers'
                    - content: The article's content
        """
        html = session.get("http://www.comunio.de/team_news.phtml").text
        soup = BeautifulSoup(html, "html.parser")

        article_headers = soup.select(".article_header1") + soup.select(".article_header2")
        article_content = soup.select(".article_content1") + soup.select(".article_content2")

        articles = []

        for index in range(0, len(article_headers)):
            header = article_headers[index].text.strip()
            content = article_content[index].text.strip()

            article = {
                "date": header.split(" ", 1)[0],
                "type": header.split(" > ", 1)[1],
                "content": content
            }

            articles.append(article)

        return articles
