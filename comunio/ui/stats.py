# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'stats.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_StatisticsWindow(object):
    def setupUi(self, StatisticsWindow):
        StatisticsWindow.setObjectName("StatisticsWindow")
        StatisticsWindow.resize(1010, 489)
        self.centralwidget = QtWidgets.QWidget(StatisticsWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.greeting_label = QtWidgets.QLabel(self.centralwidget)
        self.greeting_label.setObjectName("greeting_label")
        self.gridLayout.addWidget(self.greeting_label, 0, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 2, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 3, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 0, 1, 2)
        self.team_value_display = QtWidgets.QLabel(self.centralwidget)
        self.team_value_display.setObjectName("team_value_display")
        self.gridLayout.addWidget(self.team_value_display, 1, 3, 1, 1)
        self.cash_display = QtWidgets.QLabel(self.centralwidget)
        self.cash_display.setObjectName("cash_display")
        self.gridLayout.addWidget(self.cash_display, 1, 2, 1, 1)
        self.player_table = QtWidgets.QTreeWidget(self.centralwidget)
        self.player_table.setMinimumSize(QtCore.QSize(878, 0))
        self.player_table.setObjectName("player_table")
        self.gridLayout.addWidget(self.player_table, 2, 0, 1, 4)
        StatisticsWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(StatisticsWindow)
        self.statusbar.setObjectName("statusbar")
        StatisticsWindow.setStatusBar(self.statusbar)

        self.retranslateUi(StatisticsWindow)
        QtCore.QMetaObject.connectSlotsByName(StatisticsWindow)

    def retranslateUi(self, StatisticsWindow):
        _translate = QtCore.QCoreApplication.translate
        StatisticsWindow.setWindowTitle(_translate("StatisticsWindow", "MainWindow"))
        self.greeting_label.setText(_translate("StatisticsWindow", "Comunio Statistics for <username>"))
        self.label_3.setText(_translate("StatisticsWindow", "Cash"))
        self.label_2.setText(_translate("StatisticsWindow", "Team Value"))
        self.team_value_display.setText(_translate("StatisticsWindow", "0€"))
        self.cash_display.setText(_translate("StatisticsWindow", "0€"))
        self.player_table.headerItem().setText(0, _translate("StatisticsWindow", "Position"))
        self.player_table.headerItem().setText(1, _translate("StatisticsWindow", "Player"))
        self.player_table.headerItem().setText(2, _translate("StatisticsWindow", "Points"))
        self.player_table.headerItem().setText(3, _translate("StatisticsWindow", "Initial Value"))
        self.player_table.headerItem().setText(4, _translate("StatisticsWindow", "Yesterday\'s Value"))
        self.player_table.headerItem().setText(5, _translate("StatisticsWindow", "Today\'s Value"))
        self.player_table.headerItem().setText(6, _translate("StatisticsWindow", "Total Value Change"))
        self.player_table.headerItem().setText(7, _translate("StatisticsWindow", "Value Tendency"))

