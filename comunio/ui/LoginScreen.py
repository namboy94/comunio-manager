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
import sys
from comunio.ui.dialogs.login import Ui_LoginDialog
from comunio.scraper.ComunioSession import ComunioSession
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox
from comunio.credentials.CredentialsManager import CredentialsManager


class LoginScreen(QDialog, Ui_LoginDialog):
    """
    The Login Dialogue that allows the user to log in.
    """

    def __init__(self, credentials: CredentialsManager) -> None:
        """
        Initializes a new Login Dialog with a configurable default username and password

        :param credentials: The CredentialsManager holding the default username and password
        """
        super().__init__()
        self.setupUi(self)

        self.comunio_session = None
        self.credentials = credentials

        self.username_field.setText(credentials.get_credentials()[0])
        self.password_field.setText(credentials.get_credentials()[1])
        self.cancel_button.clicked.connect(self.close)
        self.login_button.clicked.connect(self.login)

    def get_comunio_session(self) -> ComunioSession:
        """
        :return: the internal comunio session after a login.
        """
        return self.comunio_session

    def login(self):
        """
        Tries to Log in the user, and handles failures by showing message dialogs

        :return: None
        """
        try:
            username = self.username_field.text()
            password = self.password_field.text()

            self.comunio_session = ComunioSession(username, password)
            if self.remember_check.checkState():
                self.credentials.set_credentials((username, password))
                self.credentials.store_credentials()
            self.accept()
        except ConnectionError:
            self.show_error_dialog("Login Failed", "Network Error", "The Comunio Servers could not be reached. "
                                                                    "Check if your internet connection is working.")
        except PermissionError:
            self.show_error_dialog("Login Failed", "Authentication Error", "Your credentials were not accepted by the "
                                                                           "Comunio servers. This may be due to a bad "
                                                                           "username/password combination, or due to "
                                                                           "the Comunio servers currently only "
                                                                           "allowing logins from Pro players")
        except ReferenceError:
            self.show_error_dialog("Login Failed", "5 players on transfer list", "Your comunio information could not "
                                                                                 "be loaded due to 5 players being on "
                                                                                 "the transfer list currently. Remove "
                                                                                 "a player from the transfer list to "
                                                                                 "log in.")

    @staticmethod
    def show_error_dialog(title: str, message: str, secondary_text: str) -> None:
        """
        Shows an error Dialog

        :param title:          The title of the dialog
        :param message:        The primary message of the dialog
        :param secondary_text: The secondary message of the dialog
        :return:               None
        """

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setInformativeText(secondary_text)
        msg.setWindowTitle(title)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()


def start(credentials: CredentialsManager) -> ComunioSession:
    """
    Starts the Login Dialog

    :param credentials: the credentials to be used on startup
    :return:            a logged in comunio session
    """

    app =QApplication(sys.argv)
    form = LoginScreen(credentials)
    return form.get_comunio_session() if form.exec_() else None
