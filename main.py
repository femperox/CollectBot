from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon

from GUI.mainWindow import Ui_MainWindow
import sys

class mainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(mainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)



def main():
    app = QtWidgets.QApplication(sys.argv)
    window = mainWindow()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()