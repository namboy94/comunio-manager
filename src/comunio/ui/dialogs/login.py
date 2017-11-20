# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'login.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_LoginDialog(object):
    def setupUi(self, LoginDialog):
        LoginDialog.setObjectName("LoginDialog")
        LoginDialog.resize(392, 169)
        self.username_field = QtWidgets.QLineEdit(LoginDialog)
        self.username_field.setGeometry(QtCore.QRect(20, 10, 171, 41))
        self.username_field.setObjectName("username_field")
        self.password_field = QtWidgets.QLineEdit(LoginDialog)
        self.password_field.setGeometry(QtCore.QRect(200, 10, 171, 41))
        self.password_field.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_field.setObjectName("password_field")
        self.login_button = QtWidgets.QPushButton(LoginDialog)
        self.login_button.setGeometry(QtCore.QRect(290, 130, 79, 24))
        self.login_button.setObjectName("login_button")
        self.cancel_button = QtWidgets.QPushButton(LoginDialog)
        self.cancel_button.setGeometry(QtCore.QRect(200, 130, 79, 24))
        self.cancel_button.setObjectName("cancel_button")
        self.remember_check = QtWidgets.QCheckBox(LoginDialog)
        self.remember_check.setGeometry(QtCore.QRect(20, 60, 121, 19))
        self.remember_check.setObjectName("remember_check")
        self.label = QtWidgets.QLabel(LoginDialog)
        self.label.setGeometry(QtCore.QRect(40, 90, 351, 31))
        self.label.setWordWrap(True)
        self.label.setObjectName("label")

        self.retranslateUi(LoginDialog)
        QtCore.QMetaObject.connectSlotsByName(LoginDialog)

    def retranslateUi(self, LoginDialog):
        _translate = QtCore.QCoreApplication.translate
        LoginDialog.setWindowTitle(_translate("LoginDialog", "Dialog"))
        self.username_field.setText(_translate("LoginDialog", "Username"))
        self.password_field.setText(_translate("LoginDialog", "Password"))
        self.login_button.setText(_translate("LoginDialog", "Login"))
        self.cancel_button.setText(_translate("LoginDialog", "Cancel"))
        self.remember_check.setText(_translate("LoginDialog", "Remember Me"))
        self.label.setText(_translate("LoginDialog", "<html><head/><body><p><span style=\" color:#ef2929;\">Warning: Storing your password locally will enable anyone with access to your PC to read your password</span></p></body></html>"))

