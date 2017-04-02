# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'graphwidget.ui'
#
# Created by: PyQt5 UI code generator 5.8
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_GraphLayout(object):
    def setupUi(self, GraphLayout):
        GraphLayout.setObjectName("GraphLayout")
        GraphLayout.resize(981, 303)
        self.verticalLayout = QtWidgets.QVBoxLayout(GraphLayout)
        self.verticalLayout.setContentsMargins(1, 1, 1, 1)
        self.verticalLayout.setSpacing(1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.graph = QtWidgets.QWidget(GraphLayout)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graph.sizePolicy().hasHeightForWidth())
        self.graph.setSizePolicy(sizePolicy)
        self.graph.setObjectName("graph")
        self.verticalLayout.addWidget(self.graph)
        self.menu = QtWidgets.QWidget(GraphLayout)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.menu.sizePolicy().hasHeightForWidth())
        self.menu.setSizePolicy(sizePolicy)
        self.menu.setMinimumSize(QtCore.QSize(400, 40))
        self.menu.setObjectName("menu")
        self.verticalLayout.addWidget(self.menu)

        self.retranslateUi(GraphLayout)
        QtCore.QMetaObject.connectSlotsByName(GraphLayout)

    def retranslateUi(self, GraphLayout):
        _translate = QtCore.QCoreApplication.translate
        GraphLayout.setWindowTitle(_translate("GraphLayout", "Form"))

