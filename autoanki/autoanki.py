from PyQt5              import QtWidgets
from PyQt5              import QtWidgets
from PyQt5.QtCore       import Qt
from mainwindow         import MainWindowGui, STYLESHEET
import sys


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    app.processEvents()
    
    MainWindow = QtWidgets.QDialog()
    MainWindow.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
    MainWindow.setWindowFlag(Qt.WindowMaximizeButtonHint, True) 
    
    gui = MainWindowGui()
    gui.setupUI(MainWindow)
    
    MainWindow.show()
    gui.spawn_tutorial_dialog()
    
    sys.exit(app.exec_())