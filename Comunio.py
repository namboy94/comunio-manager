#!/usr/bin/env python
# -*- coding: utf-8 -*- 

# Copyright 2014 Javier Corbín, 2016 Hermann Krumrey

from bs4 import BeautifulSoup
from datetime import date as dt
import os
import re
import requests
import sys
import time

class Comunio:

    def __init__(self,username,password):
        self.username = username
        self.password = password
        self.session = requests.session()
        self.login()

    def login(self):
        payload = { 'login':self.username,
                    'pass':self.password,
                    'action':'login'}
        
        req = self.session.post('http://www.comunio.de/login.phtml',data=payload).text
        if 'puntos en proceso' in req or 'points in process' in req:
            print('Comunio webpage not available.')
            return

        self.load_info() #Function to load the account information
  
    def load_info(self):
        ''' Get info from logged account '''
        headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain",'Referer': 'http://www.comunio.de/login.phtml',"User-Agent": user_agent}
        req = self.session.get('http://www.comunio.de/team_news.phtml',headers=headers).content
        soup = BeautifulSoup(req, 'html.parser')
        self.title = soup.title.string
        
        estado = soup.find('div',{'id':'content'}).find('div',{'id':'manager'}).string
        if estado:
            print(estado.strip())
            return

        [s.extract() for s in soup('strong')]
        if (soup.find('div',{'id':'userid'}) != None):
            self.myid = soup.find('div',{'id':'userid'}).p.text.strip()[2:]
            self.money = int(soup.find('div',{'id':'manager_money'}).p.text.strip().replace(".","")[:-2])
            self.teamvalue = int(soup.find('div',{'id':'teamvalue'}).p.text.strip().replace(".","")[:-2])
            self.community_id = soup.find('link')['href'][24:]
            self.username = soup.find('div',{'id':'username'}).p.a.text

    def get_money(self):
        '''Get my money'''
        return self.money
    
    def get_team_value(self):
        '''Get my team value'''
        return self.teamvalue    

    def get_own_player_list(self):
        players = []

        sell_html = self.session.get("http://www.comunio.de/putOnExchangemarket.phtml")
        on_sale_html = self.session.get('http://www.comunio.de/exchangemarket.phtml?takeplayeroff_x=22')

        soups = (BeautifulSoup(sell_html.text, "html.parser"), BeautifulSoup(on_sale_html.text, "html.parser"))

        for soup in soups:
            pls = soup.select(".tr1") + soup.select(".tr2")

            for p in pls:
                attrs = p.select("td")

                player = {"name": attrs[0].text.strip(),
                          "value": attrs[2].text.strip().replace(".", ""),
                          "points": attrs[3].text.strip(),
                          "position": attrs[4].text.strip()}

                players.append(player)

        return players
    
if __name__ == "__main__":
    c = Comunio()

    team_value = c.get_team_value()
    cash = c.get_money()

    players = c.get_own_player_list()
    for player in players:
        print(player)