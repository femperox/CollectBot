from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon, QImage, QPalette, QBrush


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):

        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(800, 600)

        MainWindow.setWindowTitle("Hideout Collect")
        MainWindow.setWindowIcon(QIcon(r'GUI/sources/icon.png'))

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.widgetLayout = QtWidgets.QWidget(self.centralwidget)
        self.widgetLayout.setGeometry(QtCore.QRect(0, 0, 91, 601))
        self.widgetLayout.setObjectName("widget")
        self.widgetLayout.setStyleSheet(" background-image: url(GUI/sources/left_bg.png);")

        self.verticalLayoutWidget = QtWidgets.QWidget(self.widgetLayout)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 91, 601))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")


        self.layoutBtn = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.layoutBtn.setContentsMargins(0, 0, 0, 0)
        self.layoutBtn.setObjectName("layoutBtn")


        self.widgetAdd = QtWidgets.QWidget(self.centralwidget)
        self.widgetAdd.setGeometry(QtCore.QRect(90, 0, 711, 601))
        self.widgetAdd.setObjectName("widgetAdd")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Hideout Collect"))
