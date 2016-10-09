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
import configparser
from typing import Tuple


class CredentialsManager(object):
    """
    Class that manages a user's login credentials
    """

    def __init__(self, credentials: Tuple[str, str]=None) -> None:
        """
        Creates a new CredentialsManager object. It can be passed a username and a password, if they
        are not supplied, it will be attempted to access the local configuration file.

        :param credentials: Tuple consisting of username, password
        """
        config_dir_location = os.path.join(os.path.expanduser("~"), ".comunio")
        self.config_file_location = os.path.join(config_dir_location, "config")

        if not os.path.isdir(config_dir_location):
            os.makedirs(config_dir_location)

        if credentials is None:
            self.get_credentials_from_config()
        else:
            self.username, self.password = credentials

    def get_credentials_from_config(self) -> Tuple[str, str]:
        """
        Parses the local config file for a username and password

        :return: username, password
        """
        try:
            parser = configparser.ConfigParser()
            parser.read(self.config_file_location)
            self.username = parser.get("credentials", "username")
            self.password = parser.get("credentials", "password")
        except (KeyError, configparser.NoSectionError, FileNotFoundError):
            with open(self.config_file_location, 'w') as config:
                config.write("[credentials]\nusername=\npassword=\n")
            self.username = ""
            self.password = ""

    def get_credentials(self) -> Tuple[str, str]:
        """
        :return: the credentials as a tuple of username, password
        """
        return self.username, self.password

    def get_config_file_location(self) -> str:
        """
        :return: the config file's location
        """
        return self.config_file_location

    def set_credentials(self, credentials: Tuple[str, str]) -> None:
        """
        Sets the credentials of the CredentialsManager

        :param credentials: the credentials to store as a tuple of username, password
        :return: None
        """
        self.username, self.password = credentials

    def store_credentials(self) -> None:
        """
        Stores the current credentials in the config file

        :return: None
        """
        with open(self.config_file_location, 'w') as config:
            config.write("[credentials]\nusername=" + self.username + "\npassword=" + self.password + "\n")
