from PyQt5              import QtWidgets
from PyQt5              import QtWidgets
from PyQt5.QtCore       import Qt
from mainwindow_gui     import MainWindowGui, STYLESHEET
import sys


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    app.processEvents()
    MainWindow = QtWidgets.QDialog()
    MainWindow.setWindowFlag(Qt.WindowMinimizeButtonHint, True)   # Despite the Pylance error, this works (?)
    MainWindow.setWindowFlag(Qt.WindowMaximizeButtonHint, True) 
    gui = MainWindowGui()
    gui.setupUI(MainWindow)
    MainWindow.show()
    gui.spawnTutorial()
    sys.exit(app.exec_())