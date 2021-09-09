from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon, QImage, QPalette, QBrush, QPixmap
from PyQt5.QtCore import Qt
from GUI.CustomBtn import PicButton


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):

        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(800, 600)

        MainWindow.setWindowTitle("Hideout Collect")
        MainWindow.setWindowIcon(QIcon(r'GUI/sources/icon.png'))

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.widgetLayout = QtWidgets.QWidget(self.centralwidget)
        self.widgetLayout.setGeometry(QtCore.QRect(0, 0, 150, 601))
        self.widgetLayout.setObjectName("widget")
        self.widgetLayout.setStyleSheet(" background-image: url(GUI/sources/left_bg.png);")

        self.verticalLayoutWidget = QtWidgets.QWidget(self.widgetLayout)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 150, 601))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")


        self.layoutBtn = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.layoutBtn.setContentsMargins(0, 0, 0, 0)
        self.layoutBtn.setObjectName("layoutBtn")


        self.widgetAdd = QtWidgets.QWidget(self.centralwidget)
        self.widgetAdd.setGeometry(QtCore.QRect(90, 0, 711, 601))
        self.widgetAdd.setObjectName("widgetAdd")
        MainWindow.setCentralWidget(self.centralwidget)

        self.gridLayoutWidgetAdd = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidgetAdd.setVisible(False)
        self.gridLayoutWidgetAdd.setGeometry(QtCore.QRect(90, 0, 711, 601))
        self.gridLayoutWidgetAdd.setObjectName("gridLayoutWidget")
        self.gridLayoutAdd = QtWidgets.QGridLayout(self.gridLayoutWidgetAdd)
        self.gridLayoutAdd.setContentsMargins(90, 0, 0, 0)
        self.gridLayoutAdd.setObjectName("gridLayout")


        self.checkBoxTable = QtWidgets.QCheckBox('Таблица')
        self.gridLayoutAdd.addWidget(self.checkBoxTable, 0, 0, Qt.AlignLeft)


        self.comboBoxSpAdd = QtWidgets.QComboBox()
        self.gridLayoutAdd.addWidget(self.comboBoxSpAdd, 0, 1, Qt.AlignLeft)



        self.addButton = PicButton(QPixmap(r'GUI/sources/add.png'), QPixmap(r'GUI/sources/add_hover.png'), QPixmap(r'GUI/sources/add_pressed.png'))
        self.addButton.setObjectName("Add")

        self.layoutBtn.addWidget(self.addButton)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Hideout Collect"))
