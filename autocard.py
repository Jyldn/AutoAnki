from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QWidget, QTextEdit
from PyQt5.QtCore import Qt
from PyQt5 import QtWebEngineWidgets
from bs4 import BeautifulSoup
import uuid
import string
import stanza
import spacy_stanza
import logging
import requests
import re
import sys
import sys
import os
import pprint
import configparser
import qtvscodestyle as qtvsc
import requests
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor
import queue
import threading
from wiktionaryparser import WiktionaryParser
# from spacy.lang.ja import Japanese


# Logging
# Create logger.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# Configure the handler and formatter for logger.
handler = logging.FileHandler(f"{__name__}.log", mode='w')
formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
# Add formatter to the handler.
handler.setFormatter(formatter)
# Add handler to the logger.
logger.addHandler(handler)

# Highdpi scaling
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True) 
# QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True) 
stylesheet = qtvsc.load_stylesheet(qtvsc.Theme.LIGHT_VS)
stylesheet_drk = qtvsc.load_stylesheet(qtvsc.Theme.DARK_VS)

SHADOW_INTENSITY = 50
SHADOW_BLUR_INTENSITY = 15

HTML_HEADER_DARK = """
        <html>
        <head>
            <style>
                body { 
                    background-color: #1E1E1E; 
                    color: white;
                }
                hr {
                    border: 1px dashed dimgrey !important;
                    color: #1E1E1E !important; 
                }
            </style>
        </head>
        <body>
        """

HTML_HEADER_DARK_CONJ = """
        <html>
        <head>
            <style>
                body { 
                    background-color: #1E1E1E; 
                    color: white;
                }
                table {
                    background: #1E1E1E !important;
                }
                table, 
                table th, 
                table td, 
                table tr, 
                table tbody, 
                table thead, 
                table tfoot {
                    background-color: transparent !important; /* or 'none' */
                    border: 1px dotted #404040; /* Light grey that appears as light white */
                }
            </style>
        </head>
        <body>
        """

HTML_HEADER_LIGHT = """
        <html>
        <head>
            <style>
                body { 
                    background-color: white; 
                    color: black;
                }
                hr {
                    border: 1px dashed lightgrey !important;
                }
            </style>
        </head>
        <body>
        """ 

HTML_FOOTER = """
        </body>
        </html>
        """

LANGS = {
    "1": "Arabic",
    "2": "English",
    "3": "French",
    "4": "German",
    "5": "Japanese",
    "6": "Korean",
    "7": "Latin",
    "8": "Persian",
    "9": "Spanish"
}

NLTK_TAG_REF = {
    "noun" : ("NN", "NNS", "NNP", "NNPS"), 
    "verb" : ("VB", "VBG", "VBD", "VBN", "VBP", "VBZ"), 
    "adjective" : ("JJ", "JJR", "JJS"), 
    "adverb" : ("RB", "RBR", "RBS"), 
    "pronoun" : ("PRP", "PRP$", "WP", "WP$"),
    "preposition" : ("IN",),
    "conjunction" : ("CC",),
    "determiner" : ("DT", "WDT"),
    "modal" : ("MD",),
    "interjection" : ("UH",),
    "particle" : ("RP",),
    "symbol": ("SYM",),
    "numeral" : ("CD",),
    "exclamation" : ("!",),
    "article" : ("DT",)
}

SPACY_TO_NLTK_TAG_MAP = {
    'ADJ': 'JJ', 'ADP': 'IN', 'ADV': 'RB', 'AUX': 'MD', 'CONJ': 'CC',
    'CCONJ': 'CC', 'DET': 'DT', 'INTJ': 'UH', 'NOUN': 'NN', 'NUM': 'CD',
    'PART': 'RP', 'PRON': 'PRP', 'PROPN': 'NNP', 'PUNCT': 'SYM', 
    'SCONJ': 'IN', 'SYM': 'SYM', 'VERB': 'VB', 'X': 'FW', 'SPACE': 'SP'
}

GENDERED_LANGS = ["German", "French", "Spanish", "Latin"]


class MyLineEdit(QTextEdit):
    """Custom Text Edit needed to handle enter key presses.
    
    :param QTextEdit: QTextEdit object.
    :type QTextEdit: PyQT5.QtWidget
    """
    def __init__(self, button, *args, **kwargs):
        super(MyLineEdit, self).__init__(*args, **kwargs)
        self.button = button
    
    def keyPressEvent(self, event):
        # Check if the key is Enter
        if event.key() in [Qt.Key_Return, Qt.Key_Enter]:
            self.button.click()  # Simulate a button click
        else:
            # For all other keys, call the superclass's keyPressEvent
            super().keyPressEvent(event)


class TutorialDialog(QtWidgets.QDialog):
    """Tutorial dialog that opens on startup.
    
    :param QtWidgets: Dialog object.
    :type QtWidgets: QtWidgets.QDialog
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Keep the dialog on top.
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        
    def setupUi(self, Dialog):
        self.window = Dialog
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 350)
        self.frame = QtWidgets.QFrame(Dialog)
        self.frame.setGeometry(QtCore.QRect(20, 10, 361, 320))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.frame)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.radioButton = QtWidgets.QRadioButton(self.frame)
        self.radioButton.setObjectName("radioButton")
        self.gridLayout_2.addWidget(self.radioButton, 0, 0, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(self.frame)
        self.pushButton_2.clicked.connect(self.close)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout_2.addWidget(self.pushButton_2, 0, 1, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_2, 2, 0, 1, 1)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_6 = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 3, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.frame)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 4, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 6, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setUnderline(False)
        font.setWeight(75)
        font.setKerning(True)
        self.label_3.setFont(font)
        self.label_3.setWordWrap(True)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 5, 0, 1, 1)
        
        # Spacer
        spacerItem = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout, 0, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_3.addItem(spacerItem1, 1, 0, 1, 1)
        
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        
        colourMode = self.parent.getColourMode()
        if colourMode == "dark":
            stylesheet = qtvsc.load_stylesheet(qtvsc.Theme.DARK_VS)
        else:
            stylesheet = qtvsc.load_stylesheet(qtvsc.Theme.LIGHT_VS)
        self.window.setStyleSheet(stylesheet)
    
    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Tutorial"))
        self.radioButton.setText(_translate("Dialog", "Don\'t show this again"))
        self.pushButton_2.setText(_translate("Dialog", "close"))
        self.label_6.setText(_translate("Dialog", "Manually Search Wiktionary"))
        self.label_4.setText(_translate("Dialog", "Welcome to AutoAnki. "))
        self.label.setText(_translate("Dialog","To get definitions for a single word (or multiple), type the word(s) into the search box and either press the search button or enter key."))
        self.label_2.setText(_translate("Dialog", "Simply use the navigation bar to the left and click \'AutoAnki\'. Then, click \'open file\' and select a text file that you\'ve created. The program considers each new line in the text file as being an individual Anki card, and each word that is preceeded with an asterisk (*) will be defined and writted to the back side of the anki card. The program then outputs a text file in the AutoAnki directory which you can then import into Anki. Anki will read this file and create the cards."))
        self.label_3.setText(_translate("Dialog", "Tutorial, please read!"))
        self.label_5.setText(_translate("Dialog", "Automate Anki Cards Creation"))
    
    def close(self):
        """Close the tutorial dialog and update the config file to reflect the user's choice.
        """
        if self.radioButton.isChecked():
            self.parent.showTutorial = False
            self.parent.updateConfig()
        self.window.close()


class Gui(QWidget):
    """
    The main user inferface window.
    """
    def __init__(self, parent=None):
        super(Gui, self).__init__()
        
        # Class variables
        self.savedKeywords = False
        self.current_definitions = {}
        self.currentDefsStringified = ""
        self.defaultResolution = [800, 800]
        self.mainWindow = ""
        self.AALayoutSet = False
        self.selectedFileContent = ""
        self.currentInputFilePath = ""
        self.manualSearchMode = "word"
        self.conjugationMode = False
        self.currentOverallMode = "search"
        self.displayingSavable = False
        self.savedSidebarWords = {"English": {}, "French": {}, "German": {}, "Spanish": {}, "Latin": {}}
        self.wordOne = ""
        self.conjWord = ""
        
        # Config variables
        self.showTutorial = "True"
        self.getEtymology = "False"
        self.getUsage = "False"
        self.defInConj = "True"
        self.interfaceLanguage = "English"
        self.currentLanguage = "English"
        self.colourMode = "light"
        self.configColourMode = ""
        self.zoomFactor = 100
        self.htmlContent = ""
        self.htmlContentText = ""
        self.defaultNoteLocation = ""
        self.defaultOutputFolder = ""
        
        # Style values
        self.topOffset = 40
    
    def setupUI(self, MainWindow):
        """Initialise the GUI.

        :param MainWindow: The main window object.
        :type MainWindow: PyQt5.QtWidgets.QMainWindow
        """
        # Main window
        self.mainWindow = MainWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(900, 718)
        self.mainWindowLayout = QtWidgets.QGridLayout(MainWindow)
        self.mainWindowLayout.setObjectName("mainWindowLayout")
        
        # Parent frame
        self.mainFrame = QtWidgets.QFrame(MainWindow)
        self.mainFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.mainFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.mainFrame.setObjectName("mainFrame")
        
        # Parent layout
        self.mainLayout = QtWidgets.QGridLayout(self.mainFrame)
        self.mainLayout.setHorizontalSpacing(12)
        self.mainLayout.setVerticalSpacing(4)
        self.mainLayout.setObjectName("mainLayout")
        
        # Sidebar
        # Frame
        self.sidebarFrame = QtWidgets.QFrame(self.mainFrame)
        self.sidebarFrame.setMaximumSize(QtCore.QSize(410, 16777215))
        self.sidebarFrame.setFrameShape(QtWidgets.QFrame.Box)
        self.sidebarFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.sidebarFrame.setObjectName("sidebarFrame")
        # Layout
        self.sidebarLayout = QtWidgets.QGridLayout(self.sidebarFrame)
        self.sidebarLayout.setContentsMargins(1, -1, 0, -1)
        self.sidebarLayout.setObjectName("sidebarLayout")
        # Bottom frame
        self.sidebarInnerBottomFrame = QtWidgets.QFrame(self.sidebarFrame)
        self.sidebarInnerBottomFrame.setMaximumSize(QtCore.QSize(16777215, 120))
        self.sidebarInnerBottomFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.sidebarInnerBottomFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        # Remove border
        self.sidebarInnerBottomFrame.setObjectName("sidebarInnerBottomFrame")
        # Bottom layout
        self.sidebarBottomLayout = QtWidgets.QGridLayout(self.sidebarInnerBottomFrame)
        self.sidebarBottomLayout.setObjectName("sidebarBottomLayout")
        # Remove the frame
        self.sidebarInnerBottomFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        
        # Colour mode
        self.colourModeBtn = QtWidgets.QPushButton(self.sidebarInnerBottomFrame)
        self.colourModeBtn.setObjectName("colourModeBtn")
        self.colourModeBtn.clicked.connect(self.__toggleColourMode)
        self.sidebarBottomLayout.addWidget(self.colourModeBtn, 0, 0, 1, 1)
                
        # Settings
        self.settingsBtn = QtWidgets.QPushButton(self.sidebarInnerBottomFrame)
        self.settingsBtn.setObjectName("settingsBtn")
        self.settingsBtn.clicked.connect(self.__spawnSettingsDialog)
        self.sidebarBottomLayout.addWidget(self.settingsBtn, 1, 0, 1, 1)
        self.sidebarLayout.addWidget(self.sidebarInnerBottomFrame, 2, 0, 1, 1)
        
        # Contact Button
        self.contactBtn = QtWidgets.QPushButton(self.sidebarInnerBottomFrame)
        self.contactBtn.setObjectName("contactBtn")
        self.contactBtn.clicked.connect(self.__spawnContactDialog)
        self.sidebarBottomLayout.addWidget(self.contactBtn, 3, 0, 1, 1)
        
        # Top frame
        self.layout = QtWidgets.QVBoxLayout(self.sidebarFrame)
        self.sidebarInnerTopFrame = QtWidgets.QFrame(self.sidebarFrame)
        self.sidebarInnerTopFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.sidebarInnerTopFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.sidebarInnerTopFrame.setObjectName("sidebarInnerTopFrame")
        self.sidebarLayout.addWidget(self.sidebarInnerTopFrame, 0, 0)
        # Remove border
        self.sidebarInnerTopFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        # Layout
        self.sidebarTopLayout = QtWidgets.QGridLayout(self.sidebarInnerTopFrame)
        self.sidebarTopLayout.setObjectName("sidebarTopLayout")
        
        # AutoAnki
        self.autoAnkiBtn = QtWidgets.QPushButton(self.sidebarInnerTopFrame)
        self.autoAnkiBtn.setObjectName("autoAnkiBtn")
        self.autoAnkiBtn.clicked.connect(self.__openAutoAnki)
        self.sidebarTopLayout.addWidget(self.autoAnkiBtn, 1, 0, 1, 0)
        
        # Search wiki
        self.line = QtWidgets.QFrame(self.sidebarInnerTopFrame)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.sidebarTopLayout.addWidget(self.line, 2, 0, 1, 1)
        
        # Current lang label
        self.currentLangLabel = QtWidgets.QLabel(self.sidebarInnerTopFrame)
        self.currentLangLabel.setObjectName("currentLangLabel")
        self.sidebarTopLayout.addWidget(self.currentLangLabel, 0, 0, 1, 0)
        font = QtGui.QFont()
        font.setBold(True)
        self.currentLangLabel.setFont(font)
        
        # Change lang
        self.changeLangBtn = QtWidgets.QPushButton(self.sidebarInnerTopFrame)
        self.changeLangBtn.setObjectName("changeLangBtn")
        self.changeLangBtn.clicked.connect(self.__spawnLanguageDialog)
        self.sidebarTopLayout.addWidget(self.changeLangBtn, 2, 0, 1, 0)
        
        # ScrollArea
        self.scrollArea = QtWidgets.QScrollArea(self.sidebarInnerTopFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.scrollAreaLayout = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.sidebarLayout.addWidget(self.sidebarInnerTopFrame, 0, 0, 1, 1)
        self.mainLayout.addWidget(self.sidebarFrame, 0, 0, 2, 1)

        # Saved words
        self.sideLabel = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.sideLabel.setObjectName("sideLabel")
        self.scrollAreaLayout.addWidget(self.sideLabel, 6, 0, 1, 0)
        font = QtGui.QFont()
        font.setBold(True)
        self.sideLabel.setFont(font)
        self.line2 = QtWidgets.QFrame(self.scrollAreaWidgetContents)
        self.line2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line2.setObjectName("line2")
        self.scrollAreaLayout.addWidget(self.line2, 5, 0, 1, 1)
        # Button
        self.saveWord = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.saveWord.setObjectName("saveWord")
        self.saveWord.clicked.connect(self.saveWordToSide)
        self.scrollAreaLayout.addWidget(self.saveWord, 7, 0, 1, 0)

        self.sidebarTopLayout.addWidget(self.scrollArea)
        
        # Search layout
        self.searchInputFrame = QtWidgets.QFrame(self.mainFrame)
        self.searchInputFrame.setMinimumSize(QtCore.QSize(200, 0))
        self.searchInputFrame.setMaximumSize(QtCore.QSize(16777215, 95))
        self.searchInputFrame.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.searchInputFrame.setAutoFillBackground(False)
        self.searchInputFrame.setFrameShape(QtWidgets.QFrame.Box)
        self.searchInputFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.searchInputFrame.setObjectName("searchInputFrame")
        # Add border
        self.searchInputLayout = QtWidgets.QGridLayout(self.searchInputFrame)
        self.searchInputLayout.setObjectName("searchInputLayout")

        # Combo box
        self.searchModeCombo = QtWidgets.QComboBox(self.searchInputFrame)
        self.searchModeCombo.setObjectName("searchModeCombo")
        # Add items
        self.searchModeCombo.addItem("Sentence", "sentence")
        self.searchModeCombo.addItem("Conjugation", "conjugation")
        self.searchModeCombo.addItem("Word", "word")
        self.searchModeCombo.setCurrentIndex(2)  # Assuming "Word" is the default option
        self.searchModeCombo.currentIndexChanged.connect(self.__onSearchModeChange)
        self.searchInputLayout.addWidget(self.searchModeCombo, 0, 0, 1, 1)
        
        # Search button
        self.searchBtn = QtWidgets.QPushButton(self.searchInputFrame)
        self.searchInputEdit = MyLineEdit(self.searchBtn, self)
        self.searchInputEdit.setObjectName("searchInputEdit")
        
        # Search input
        self.searchInputLayout.addWidget(self.searchInputEdit, 0, 1, 2, 1)
        self.searchBtn.setObjectName("searchBtn")
        self.searchBtn.clicked.connect(self.__searchWiki)
        self.searchInputLayout.addWidget(self.searchBtn, 1, 0, 1, 1)
        
        # Output display
        self.mainLayout.addWidget(self.searchInputFrame, 0, 1, 1, 1)
        self.outputFrame = QtWidgets.QFrame(self.mainFrame)
        self.outputFrame.setMinimumSize(QtCore.QSize(0, 0))
        self.outputFrame.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.outputFrame.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.outputFrame.setObjectName("outputFrame")
        self.outputLayout = QtWidgets.QGridLayout(self.outputFrame)
        self.outputLayout.setObjectName("outputLayout")
        # Text
        self.searchOutputBrowser = QtWebEngineWidgets.QWebEngineView(self.outputFrame)
        html_content = self.__constructHtml("")
        self.searchOutputBrowser.setHtml(html_content)
        self.searchOutputBrowser.setZoomFactor(1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)
        sizePolicy.setHeightForWidth(self.searchOutputBrowser.sizePolicy().hasHeightForWidth())
        self.searchOutputBrowser.setSizePolicy(sizePolicy)
        self.searchOutputBrowser.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.searchOutputBrowser.setObjectName("searchOutputBrowser")
        self.outputLayout.addWidget(self.searchOutputBrowser, 0, 0, 1, 1)
        self.mainLayout.addWidget(self.outputFrame, 1, 1, 1, 1)
        self.mainWindowLayout.addWidget(self.mainFrame, 0, 0, 1, 1)
        
        # Border styling        
        self.sidebarInnerBottomFrame.setStyleSheet("QFrame {border: 0px; margin: 0px;}")
        self.sidebarInnerTopFrame.setStyleSheet("QFrame {border: 0px; margin: 0px;}")
        self.searchInputFrame.setStyleSheet("QFrame {border: 1px solid lightgrey;}")
        self.outputFrame.setStyleSheet("QFrame {border: 1px solid lightgrey;}")
        
        # Retranslate
        self.__retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.searchOutputBrowser, self.changeLangBtn)
        
        # Config
        configVars = config_check()
        self.__applyConfig(configVars)
        
        # More styling
        self.sidebarFrame.setMaximumSize(QtCore.QSize(148, 16777215))
        self.sidebarFrame.setMinimumSize(QtCore.QSize(148, 16777215))
        self.sidebarInnerTopFrame.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.scrollAreaWidgetContents.setLayout(self.scrollAreaLayout)
        self.scrollAreaLayout.setAlignment(QtCore.Qt.AlignTop)
        
        # Drop shadows
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(SHADOW_BLUR_INTENSITY)   
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, SHADOW_INTENSITY))  
        shadow1 = QGraphicsDropShadowEffect()
        shadow1.setBlurRadius(SHADOW_BLUR_INTENSITY)
        shadow1.setXOffset(0)
        shadow1.setYOffset(0)
        shadow1.setColor(QColor(0, 0, 0, SHADOW_INTENSITY))  
        shadow2 = QGraphicsDropShadowEffect()
        shadow2.setBlurRadius(SHADOW_BLUR_INTENSITY)
        shadow2.setXOffset(0)
        shadow2.setYOffset(0)
        shadow2.setColor(QColor(0, 0, 0, SHADOW_INTENSITY))  
        # self.outputFrame.setGraphicsEffect(shadow2)
        self.sidebarFrame.setGraphicsEffect(shadow)
        self.searchInputFrame.setGraphicsEffect(shadow1)

        # Apply colour mode on startup
        if self.colourMode == "dark":
            self.__activateDarkmode()
            self.__updateHtmlView()
        else:
            self.__activateLightmode()
        
        # Save button should be disabled at startup
        self.verifySaveBtnStatus()
        
        # Load saves words
        rawSavedWords = self.__readSavedWordsFile()
        savedWordsDict = self.__parseSavedWords(rawSavedWords)
        print(savedWordsDict)
        for count, id_word_pair in enumerate(savedWordsDict[self.currentLanguage].items()):
            self.__genSavedWords(id_word_pair, count)
    
    def __retranslateUi(self, MainWindow):
        """Retranslate the GUI.
        
        :param MainWindow: The main window object.
        :type MainWindow: PyQt5.QtWidgets.QMainWindow
        """
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "AutoAnki"))
        # Buttons
        self.saveWord.setText(_translate("MainWindow", "Add"))
        self.colourModeBtn.setText(_translate("MainWindow", "Dark Mode"))
        self.settingsBtn.setText(_translate("MainWindow", "Settings"))
        self.autoAnkiBtn.setText(_translate("MainWindow", "AutoAnki"))
        # self.searchWikBtn.setText(_translate("MainWindow", "Search Wiktionary"))
        self.changeLangBtn.setText(_translate("MainWindow", "Change Language"))
        self.searchBtn.setText(_translate("MainWindow", "Search"))
        self.contactBtn.setText(_translate("MainWindow", "Contact"))
        # Labels
        self.sideLabel.setText(_translate("MainWindow", "Saved Words"))
        self.sideLabel.setAlignment(Qt.AlignCenter)
        self.updateLangLabel(self.currentLanguage)
        self.currentLangLabel.setAlignment(Qt.AlignCenter)
            
    def setMyStyleLight(self):
        """Apply custom light mode styling.
        """
        self.sidebarFrame.setStyleSheet("""
            QFrame {
                border: 0px solid lightgrey;
                border-radius: 10px;
                background-color: #FAFAFA;
                    }
            """)
        self.searchInputFrame.setStyleSheet("""
            QFrame#searchInputFrame {
                border: 0px solid lightgrey;
                border-radius: 10px;
                background-color: #FAFAFA;
                    }
            """)
        self.outputFrame.setStyleSheet("""
            QFrame {
                border: 0px solid lightgrey;
                border-radius: 10px;
                    }
            """)  
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollAreaLayout.setObjectName("scrollAreaLayout")
        self.scrollAreaWidgetContents.setStyleSheet("""
            QWidget#scrollAreaWidgetContents, QLabel {
                background-color: #FAFAFA;
            }
        """)   
        self.searchInputEdit.setStyleSheet("""
            QTextEdit {
                border: 1px solid lightgrey;
                border-radius: 5px;
                    }
            """)  
        self.mainFrame.setStyleSheet("""
            QPushButton {
                border-radius: 3px;
            }
            QComboBox {
                border-radius: 3px;
            }
            QFrame {
                border: 0px; margin: 0px;
            }
        """)
        self.saveWord.setStyleSheet("QPushButton {border-radius: 3px;}")
        
    def setMyStyleDark(self):
        """Apply custom dark mode styling.
        """
        self.sidebarFrame.setStyleSheet("""
            QFrame {
                border: 0px solid lightgrey;
                border-radius: 10px;
                background-color: #292929;
                    }
            """)
        self.searchInputFrame.setStyleSheet("""
            QFrame#searchInputFrame {
                border: 0px solid lightgrey;
                border-radius: 10px;
                background-color: #292929;
                    }
            """)
        self.outputFrame.setStyleSheet("""
            QFrame {
                border: 0px solid lightgrey;
                border-radius: 10px;
                    }
            """)  
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollAreaLayout.setObjectName("scrollAreaLayout")
        self.scrollAreaWidgetContents.setStyleSheet("""
            QWidget#scrollAreaWidgetContents, QLabel {
                background-color: #292929;
            }
        """)   
        self.searchInputEdit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #171717;
                border-radius: 5px;
                    }
            """)  
        self.mainFrame.setStyleSheet("""
            QPushButton {
                border-radius: 3px;
            }
            QComboBox {
                border-radius: 3px;
            }
            QFrame {
                border: 0px; margin: 0px;
            }
        """)
        self.saveWord.setStyleSheet("QPushButton {border-radius: 3px;}")
    
    def __onSearchModeChange(self, index):
        """Updates the class when search mode is changed.

        :param index: The index of the search mode combo box.
        :type index: int
        """
        mode = self.searchModeCombo.itemData(index)
        if mode == "sentence":
            self.manualSearchMode = "sentence"
            self.conjugationMode = False
        elif mode == "conjugation":
            self.conjugationMode = True
        elif mode == "word":
            self.manualSearchMode = "word"
            self.conjugationMode = False
    
    def verifySaveBtnStatus(self):
        """Toggle the save button on/off.
        """
        if self.displayingSavable is True:
            self.saveWord.setEnabled(True)
        else:
            self.saveWord.setEnabled(False)
    
    def __activateLightmode(self):
        """Apply light mode.
        """
        stylesheet = qtvsc.load_stylesheet(qtvsc.Theme.LIGHT_VS)
        self.mainWindow.setStyleSheet(stylesheet)
        self.colourMode = "light"
        self.__reapplyBorderColours()
        self.setMyStyleLight()
        self.colourModeBtn.setText("Dark Mode")
    
    def __activateDarkmode(self):
        """Apply dark mode.
        """
        stylesheet = qtvsc.load_stylesheet(qtvsc.Theme.DARK_VS)
        self.mainWindow.setStyleSheet(stylesheet)
        self.colourMode = "dark"
        self.__reapplyBorderColours()
        self.setMyStyleDark()
        self.colourModeBtn.setText("Light Mode")
    
    def __toggleColourMode(self):
        """Toggle dark/light modes when user presses the colour mode button.
        """
        if self.colourMode == "light":
            self.__activateDarkmode()
        else:
            self.__activateLightmode()
        self.__updateHtmlView()
        self.updateLangLabel(self.currentLanguage)
    
    def __reapplyBorderColours(self):
        """When the theme changes, the colour of the border frames resets. These colours need to
        be reapplied.
        """
        if self.colourMode == "dark":
            self.sidebarFrame.setStyleSheet("QFrame {border: 1px solid dimgrey;}")
            self.searchInputFrame.setStyleSheet("QFrame {border: 1px solid dimgrey;}")
            self.outputFrame.setStyleSheet("QFrame {border: 1px solid dimgrey;margin-top: 5px;}")
            if self.AALayoutSet is True:
                self.autoAnkiTopFrame.setStyleSheet("QFrame {border: 1px solid dimgrey;}")
                self.outputFrameAA.setStyleSheet("QFrame {border: 1px solid dimgrey;}")
        else:
            self.sidebarFrame.setStyleSheet("QFrame {border: 1px solid lightgrey;}")
            self.searchInputFrame.setStyleSheet("QFrame {border: 1px solid lightgrey;}")
            self.outputFrame.setStyleSheet("QFrame {border: 1px solid lightgrey;margin-top: 5px;}")
            if self.AALayoutSet is True:
                self.autoAnkiTopFrame.setStyleSheet("QFrame {border: 1px solid lightgrey;}")
                self.outputFrameAA.setStyleSheet("QFrame {border: 1px solid lightgrey;}")
    
    def updateLangLabel(self, lang):
        """Add an emoji to the language label.

        :param lang: Currently selected language.
        :type lang: str
        """
        if lang == "French":
            emoji = "🥖"
        elif lang == "German":
            emoji = "🥨"
        elif lang == "Spanish":
            emoji = "💃"
        elif lang == "Latin": 
            emoji = "🏺"
        elif lang == "English":
            emoji = "💂"
        self.currentLangLabel.setText(f"{lang} {emoji}")
    
    def updateConfig(self):
        """Updates the config file with new variables.
        """
        config = configparser.ConfigParser()
        config['LanguagePreferences'] = {'InterfaceLanauge': self.interfaceLanguage, 'SearchLanguage': self.currentLanguage}
        config['Interface'] = {'ColourMode': self.configColourMode, 'ZoomLevel': int(self.zoomFactor * 100)}
        config['Behaviour'] = {'ShowTutorial': self.showTutorial}
        config['SearchSettings'] = {'GetEtymology': self.getEtymology, 'GetUsage': self.getUsage, 'defInConj': self.defInConj}
        config['DefaultLocations'] = {'defaultNotesFile': self.defaultNoteLocation, 'defaultOutputFolder': self.defaultOutputFolder}
        
        with open("config.ini", 'w') as configfile:
            config.write(configfile)
            
        logger.info("New config file generated.")
        
        # Apply config changes
        self.updateLangLabel(self.currentLanguage)
    
    def __applyConfig(self, configVars):
        """Apply config variables.

        :param configVars: A list of config variables.
        :type configVars: list
        """
        self.interfaceLanguage = configVars[0]
        self.currentLanguage = configVars[1]
        self.colourMode = configVars[2]
        self.configColourMode = configVars[2]
        self.zoomFactor = configVars[3]
        self.showTutorial = configVars[4]
        # Search settings
        self.getEtymology = configVars[5]
        self.getUsage = configVars[6]
        self.defInConj = configVars[7]
        self.defaultNoteLocation = configVars[8]
        self.defaultOutputFolder = configVars[9]
        # Apply config
        self.__applyZoomLvl(self.zoomFactor)
        self.updateLangLabel(self.currentLanguage)
        
    def applySettings(self, newZoomFactor, newColourMode):
        """Apply settings from the settings dialog.

        :param newZoomFactor: The new zoom factor.
        :type newZoomFactor: int
        :param newColourMode: The new colour mode.
        :type newColourMode: str
        """
        # Zoom factor needs a decimal, but the input here is a float, so divide.
        self.__applyZoomLvl(newZoomFactor)
        self.configColourMode = newColourMode
        
    def __applyZoomLvl(self, newZoomFactor):
        """Apply the zoom level.

        :param newZoomFactor: The new zoom factor.
        :type newZoomFactor: int
        """
        newZoomFactor = int(newZoomFactor) / 100
        self.zoomFactor = newZoomFactor
        self.searchOutputBrowser.setZoomFactor(newZoomFactor)
    
    def getZoomFactor(self):
        """Get the current zoom factor.
        
        :return: The current zoom factor.
        :rtype: int
        """
        return self.zoomFactor        
    
    def __callAPI(self, keyword):
        """Call the Wiktionary API and get the definition for a specific word.

        :param keyword: The word to search for.
        :type keyword: str
        :return: A dictionary of definitions.
        :rtype: dict
        """
        return grab_wik(keyword, self.currentLanguage, self.getEtymology, self.getUsage, self.defInConj)
    
    def __searchWiki(self):
        """Search Wiktionary for a specific word.
        """        
        # Get search term from input box.
        text = self.searchInputEdit.toPlainText()
        text = text.strip()
        
        # Check number of words
        if self.manualSearchMode == "word" or self.conjugationMode == True:
            keywords = text.split()
            if not keywords:
                self.searchOutputBrowser.setHtml("<p>No input. Please enter a word to get its definition.</p>")
                logger.warning("User has not entered a word.")
                return
        elif self.manualSearchMode == "sentence":
            keywords = [text]
        
        # Send search term to API caller and update class dictionary.
        defsDictsArray = []
        if self.conjugationMode == True:
            # Conjugation table search
            logger.info("Doing conjugation table search.")
            for keyword in keywords:
                self.conjWord = keyword
                conjs = f"<h3>{keyword}</h3>"
                conjs += grab_wik_conjtable(keyword, self.currentLanguage)
                # Remove links
                conjs = strip_bs4_links(conjs)
                
                if self.defInConj == "True":
                    defsDictsArray.append(self.__callAPI(keyword))
                    self.wordOne = keyword
                    # conjs += f"<h3>{keyword}</h3>"
                    conjs += f"<h3></h3>"
                    definitionsString = self.__stringifyDefDict(defsDictsArray[0])
                    conjs += definitionsString
                
                self.htmlContentText = conjs
                self.__updateHtmlView()
                self.displayingSavable = True
                self.verifySaveBtnStatus()
                return
        else:
            # Definitions search
            for keyword in keywords:
                defsDictsArray.append(self.__callAPI(keyword))
            # Stringify definitions dictionary.
            definitions = ""
            print(defsDictsArray)
            for count, defsDict in enumerate(defsDictsArray):
                if count > 0:
                    definitions += "<hr>"
                if count == 0:
                    self.wordOne = keywords[count]
                definitions += f"<h3>{keywords[count]}</h3>"
                definitionsString = self.__stringifyDefDict(defsDict)
                definitions += definitionsString
            # Update class string defs variable.
            self.__updateDefsString(definitions)
            self.__displayDefinitions()
            self.__updatCurrentDefinitions(defsDictsArray)
            self.displayingSavable = True
            self.verifySaveBtnStatus()
    
    def __stringifyDefDict(self, defsDict):
        """Takes a definitions dictionary and converts it to HTML.

        :param defsDict: A dictionary of definitions.
        :type defsDict: dict
        :return: The definitions in HTML format.
        :rtype: str
        """
        defs_string = ""
        if defsDict:
            for tag, definition in defsDict.items():
                if definition:
                    
                    if tag != "etymology" and tag != "usage":
                        defs_string += f"{tag.capitalize()}"
                        for line_no, string in enumerate(definition):
                            if line_no == 0:
                                split_def = string.split()
                                split_def = " ".join(split_def[1:])
                                defs_string += f" <i>{split_def}</i>"
                            elif line_no == 1:
                                defs_string += "<ol>"
                                defs_string += f"<li>{string}</li>"
                            else:
                                defs_string += f"<li>{string}</li>"
                        defs_string += "</ol>"
                        defs_string += "<br>"
                    
                    elif tag == "etymology" or tag == "usage":
                        defs_string += f"<span style='color:grey;font-size:0.85em;'>{tag.capitalize()}</span>"
                        defs_string += f"<span style='color:grey;font-size:0.85em;'><ul><li>{definition[0]}</li></ul><br></span>"
                    else:
                        defs_string += f"{tag.capitalize()}"
                        defs_string += "<ol>"
                        for line_no, string in enumerate(definition):
                            defs_string += f"<li>{string}</li>"
                        defs_string += "</ol>"
                        defs_string += "<br>"
        
        return defs_string
    
    def __updateDefsString(self, defsString):
        """Update the definitions variable.

        :param defsString: The definitions in HTML format.
        :type defsString: str
        """
        self.currentDefsStringified = defsString
    
    def __updatCurrentDefinitions(self, new_definition_dict):
        """Update the definitions variable.

        :param new_definition_dict: The definitions in HTML format.
        :type new_definition_dict: dict
        """
        self.current_definitions = new_definition_dict
    
    def __displayDefinitions(self):
        """Clear the search output display and update it with the currently saved definitions.
        """
        self.htmlContentText = self.currentDefsStringified
        self.__updateHtmlView()
    
    def __constructHtml(self, content):
        """Construct HTML for the search output display.

        :param content: The content to be displayed.
        :type content: str
        :return: The HTML content.
        :rtype: str
        """
        html = ""
        isTable = False
        
        # Determine if it's a conjugation table.
        if "<table" in content:
            isTable = True
            
        if self.colourMode == "dark":
            if self.conjugationMode or isTable == True:
                html = HTML_HEADER_DARK_CONJ + content + HTML_FOOTER
            else:
                html = HTML_HEADER_DARK + content + HTML_FOOTER
        else:
            html = HTML_HEADER_LIGHT + content + HTML_FOOTER
        self.htmlContent = html
        return html
        
    def __updateHtmlView(self):
        """Update the search output display.
        """
        self.__constructHtml(self.htmlContentText)
        self.searchOutputBrowser.setHtml(self.htmlContent)
    
    def makeCards(self, deckName, messageQueue, saveFolder):
        """Make cards from the current definitions.

        :param deckName: The name of the deck to add the cards to.
        :type deckName: str
        :param messageQueue: The message queue to send messages to the loading screen thread.
        :type messageQueue: multiprocessing.Queue
        """
        make_cards(self.currentInputFilePath, self.currentLanguage, deckName, messageQueue, saveFolder)
    
    def __spawnSettingsDialog(self):
        """Bring up the settings dialog.
        """
        self.settingsDlg = QtWidgets.QDialog()
        self.UISettings = GuiSettingsDialog(self)
        self.UISettings.setupUi(self.settingsDlg)
        
        # Colour mode styling
        if self.colourMode == "dark":
            self.settingsDlg.setStyleSheet(stylesheet_drk)
        else:
            self.settingsDlg.setStyleSheet(stylesheet)
        
        self.settingsDlg.show()

    def __spawnLanguageDialog(self):
        """Bring up the language selector dialog.
        """
        self.windowLangs = QtWidgets.QDialog()
        self.UILangs = GuiChangeLangWindow(self)
        self.UILangs.setupUi(self.windowLangs)
        
        # Colour mode styling
        if self.colourMode == "dark":
            self.windowLangs.setStyleSheet(stylesheet_drk)
        else:
            self.windowLangs.setStyleSheet(stylesheet)
        
        self.windowLangs.show()
        
    def __spawnContactDialog(self):
        """Bring up the contact dialog.
        """
        self.windowContact = QtWidgets.QDialog()
        self.UIContact = GuiContactDialog()
        self.UIContact.setupUi(self.windowContact)
        
        # Colour mode styling
        if self.colourMode == "dark":
            self.windowContact.setStyleSheet(stylesheet_drk)
        else:
            self.windowContact.setStyleSheet(stylesheet)
        
        self.windowContact.show()
        
    def __openAutoAnki(self):
        """Bring up the AutoAnki dialog.
        """
        self.windowAa = QtWidgets.QDialog()
        self.UIAa = GuiAA(self)
        self.UIAa.setupUi(self.windowAa)
        
        # Colour mode styling
        if self.colourMode == "dark":
            self.windowAa.setStyleSheet(stylesheet_drk)
        else:
            self.windowAa.setStyleSheet(stylesheet)
        
        self.windowAa.show()
        
    def spawnTutorial(self):
        """Bring up the language selector dialog.
        """
        if self.showTutorial == "True":
            self.windowTute = QtWidgets.QDialog()
            self.UITute = TutorialDialog(self)
            self.UITute.setupUi(self.windowTute)
            self.windowTute.show()
        else:
            logger.info("Tutorial has been disabled.")
    
    def addFile(self):
        """Opens a file explorer.
        """
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)
        
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            logger.info(f"File(s) selected for card generation input: {filenames}")
            self.currentInputFilePath = filenames[0]
            
            f = open(filenames[0], 'r', encoding="utf-8")
            with f:
                data = f.read()
                self.selectedFileContent = data
    
    def getCurrentLang(self):
        """Get the current language.
        
        :return: The currently selected search language.
        :rtype: str
        """
        return self.currentLanguage
    
    def changeLanguage(self, newLang):
        """Update the language variable.

        :param newLang: The new language.
        :type newLang: str
        """
        print("CHANGE LANG CALLED")
        # Remove all buttons from the scroll area
        for uid in self.savedSidebarWords[self.currentLanguage].keys():
            word_btn = self.sidebarInnerTopFrame.findChild(QtWidgets.QPushButton, f"sideButton{uid}")
            remove_btn = self.sidebarInnerTopFrame.findChild(QtWidgets.QPushButton, f"sideButtonRmv{uid}")
            self.scrollAreaLayout.removeWidget(word_btn)
            self.scrollAreaLayout.removeWidget(remove_btn)
        
        self.currentLanguage = newLang
        logger.info("Current lang saved as " + newLang) 
        
        # rawSavedWords = self.__readSavedWordsFile()
        # savedWordsDict = self.__parseSavedWords(rawSavedWords)
        # print(f"DICT::: {self.savedSidebarWords}")
        for count, id_word_pair in enumerate(self.savedSidebarWords[self.currentLanguage].items()):
            print("MAKING CARD BTN")
            self.__genSavedWords(id_word_pair, count)
        
        self.updateConfig()
        return
    
    def getColourMode(self):
        """Get the current colour mode.

        :return: The current colour mode.
        :rtype: str
        """
        return self.colourMode
    
    def saveWordToSide(self):
        """Saves a word to the sidebar.
        """
        # Save the word content and associate with a unique ID
        unique_id = str(uuid.uuid1(node=None, clock_seq=None))
        self.savedSidebarWords[self.currentLanguage][unique_id] = self.htmlContentText
        
        if self.conjugationMode:
            # Shorten word used for the display
            word = self.conjWord
            if len(word) > 9:
                word = word[:7] + ".."
            # Create a new button for the sidebar
            newWordBtn = QtWidgets.QPushButton(self.sidebarInnerTopFrame)
            number = len(self.savedSidebarWords[self.currentLanguage])
            newWordBtn.setObjectName(f"sideButton{unique_id}")
            self.scrollAreaLayout.addWidget(newWordBtn, 7+number, 0, 1, 1)
            newWordBtn.setText(f"{word}")
        
        else:            
            # Shorten word used for the display
            word = self.wordOne
            if len(word) > 9:
                    word = word[:7] + ".."
            # Create a new button for the sidebar.
            newWordBtn = QtWidgets.QPushButton(self.sidebarInnerTopFrame)
            number = len(self.savedSidebarWords[self.currentLanguage])
            newWordBtn.setObjectName(f"sideButton{unique_id}")
            self.scrollAreaLayout.addWidget(newWordBtn, 7+number, 0, 1, 1)
            newWordBtn.setText(f"{word}")
            
        newWordBtn.clicked.connect(lambda: self.loadSavedWord(self.savedSidebarWords[self.currentLanguage][unique_id]))
        # Create remove button
        newWordBtnRmv = QtWidgets.QPushButton(self.sidebarInnerTopFrame)
        newWordBtnRmv.setObjectName(f"sideButtonRmv{unique_id}")
        self.scrollAreaLayout.addWidget(newWordBtnRmv, 7+number, 1, 1, 1)
        newWordBtnRmv.setText("-")
        newWordBtnRmv.clicked.connect(lambda: self.__removeSavedWord(unique_id))
        # Save word content to file (just the HTML content, not the formatted HTML string used for display)
        self.saveWordToFile(self.htmlContentText)
    
    def __readSavedWordsFile(self):
        """Read the saved words file and return the contents.
        """
        for language in self.savedSidebarWords.keys():
            with open(f"{language}_words.txt", "r", encoding="utf-8") as f:
                content = f.read()
                f.close()
                self.savedSidebarWords[language]["raw"] = content
        
        return self.savedSidebarWords
    
    def __parseSavedWords(self, savedWordsDict):
        """Parse the saved words file and return a list of words.
        
        :param content: String containing HTML content for words separated by a line of equals signs.
        :type content: str
        :return: Dictionary of word HTML content.
        :rtype: dict
        """
        for language, langDict in savedWordsDict.items():
            content = langDict["raw"]
            content = content.split("\n====================================\n")
            # Remove the last entry (it is empty).
            content.pop()
            # Save the retrieved words to the class variable.
            for item in content:
                unique_id = str(uuid.uuid1(node=None, clock_seq=None))
                self.savedSidebarWords[language][unique_id] = item
            langDict.pop("raw")
        return self.savedSidebarWords
    
    def __genSavedWords(self, id_word_pair, count):
        """Generate the saved words buttons on startup.
        """        
        # Create a new button for the sidebar.
        newWordBtn = QtWidgets.QPushButton(self.sidebarInnerTopFrame)
        newWordBtn.setObjectName(f"sideButton{id_word_pair[0]}")
        self.scrollAreaLayout.addWidget(newWordBtn, 8+count, 0, 1, 1)
        
        # Create remove button
        newWordBtnRmv = QtWidgets.QPushButton(self.sidebarInnerTopFrame)
        newWordBtnRmv.setObjectName(f"sideButtonRmv{id_word_pair[0]}")
        self.scrollAreaLayout.addWidget(newWordBtnRmv, 8+count, 1, 1, 1)
        newWordBtnRmv.setText("-")
        newWordBtnRmv.setMaximumSize(QtCore.QSize(25, 16777215))
        newWordBtnRmv.clicked.connect(lambda: self.__removeSavedWord(id_word_pair[0]))
        
        # Regex expression that finds the first header in the string and extracts the word.
        match = re.search(r"<h3>(\w+)</h3>", id_word_pair[1])
        
        # Get the word, needed for the button
        word = match.group(1)
        if len(word) > 9:
                word = word[:7] + ".."     
        newWordBtn.setText(f"{word}")
        
        # Determine if it's a conjugation table.
        if "<table" in id_word_pair[1]:
            if len(word) > 9:
                word = word[:7] + ".."
            newWordBtn.setText(f"{word}") 
        
        # Align text on buttons to the left.
        # newWordBtn.setStyleSheet("QPushButton { text-align: left; }")
        
        # Dynamically connect button to function.
        newWordBtn.clicked.connect(lambda: self.loadSavedWord(self.savedSidebarWords[self.currentLanguage][id_word_pair[0]]))
    
    def __removeSavedWord(self, unique_id):
        """Remove a saved word from the sidebar.
        """
        # Remove the button.
        word_btn = self.sidebarInnerTopFrame.findChild(QtWidgets.QPushButton, f"sideButton{unique_id}")
        remove_btn = self.sidebarInnerTopFrame.findChild(QtWidgets.QPushButton, f"sideButtonRmv{unique_id}")
        self.scrollAreaLayout.removeWidget(word_btn)
        self.scrollAreaLayout.removeWidget(remove_btn)

        # Remove the word from the dict.
        print(f"Deleting saved word at key {unique_id}")
        self.savedSidebarWords[self.currentLanguage].pop(unique_id)
        # Update the saved words file.
        self.__updateSavedWordsFile()
    
    def __updateSavedWordsFile(self):
        """Update the saved words file with the new list of saved words.
        """
        with open(f"{self.currentLanguage}_words.txt", "w", encoding="utf-8") as f:
            for content in self.savedSidebarWords[self.currentLanguage].values():
                f.write(content)
                f.write("\n====================================\n")
            f.close()
    
    def loadSavedWord(self, content):
        """Load a saved word from the sidebar.
        """
        self.htmlContentText = content
        self.__constructHtml(content)
        self.searchOutputBrowser.setHtml(self.htmlContent)
    
    def saveWordToFile(self, content):
        """Save (append) a word to the saved words file.
        """
        with open(f"{self.currentLanguage}_words.txt", "a", encoding="utf-8") as f:
            f.write(content)
            f.write("\n====================================\n")
            f.close()


class GuiAA(object):
    """The AutoAnki dialog.
    """
    def __init__(self, parent):
        self.parent = parent
        self.explorerUsed = False
    
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(351, 205)
        self.widget = QtWidgets.QWidget(Dialog)
        self.widget.setGeometry(QtCore.QRect(20, 20, 311, 140))
        self.widget.setObjectName("widget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.widget)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.headerLbl = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.headerLbl.setFont(font)
        self.headerLbl.setTextFormat(QtCore.Qt.MarkdownText)
        self.headerLbl.setAlignment(QtCore.Qt.AlignCenter)
        self.headerLbl.setObjectName("headerLbl")
        self.gridLayout_2.addWidget(self.headerLbl, 0, 0, 1, 1)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtWidgets.QLabel(self.widget)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.widget)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.gridLayout.addWidget(self.lineEdit_2, 1, 1, 1, 1)
        self.pushButton = QtWidgets.QPushButton(self.widget)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.__openFile)
        self.gridLayout.addWidget(self.pushButton, 0, 0, 1, 1)
        self.lineEdit = QtWidgets.QLineEdit(self.widget)
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setReadOnly(True)
        self.gridLayout.addWidget(self.lineEdit, 0, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 2, 0, 1, 1)
        # Customize the button box
        self.buttonBox = QtWidgets.QDialogButtonBox(self.widget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        # Remove the existing buttons
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.NoButton)
        # Create custom buttons and add them to the button box
        self.makeCardsButton = self.buttonBox.addButton("Make Cards", QtWidgets.QDialogButtonBox.AcceptRole)
        self.cancelButton = self.buttonBox.addButton("Cancel", QtWidgets.QDialogButtonBox.RejectRole)
        self.gridLayout_2.addWidget(self.buttonBox, 3, 0, 1, 1)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        # Connect the custom buttons to their respective slots
        self.makeCardsButton.clicked.connect(self.__makeCards)
        self.cancelButton.clicked.connect(Dialog.reject)
        self.retranslateUi(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "AutoAnki Card Generator"))
        self.headerLbl.setText(_translate("Dialog", "🀄 AutoAnki Card Generator 🀄"))
        self.label_2.setText(_translate("Dialog", "Deck name"))
        self.pushButton.setText(_translate("Dialog", "Open"))
        self.lineEdit.setText(self.parent.defaultNoteLocation)

    def __openFile(self):
        """Opens a file explorer.
        """
        self.parent.addFile()
        self.lineEdit.setText(self.parent.currentInputFilePath)
        self.explorerUsed = True
        
    def __makeCards(self):
        """Start the card-making process.
        """
        if self.explorerUsed is False:
            self.__openFileDefault()
        
        deckName = self.lineEdit_2.text()
        if deckName == "":
            deckName = "unnamed_deck"
            
        # Create a queue for inter-thread communication
        self.messageQueue = queue.Queue()
        
        # Loading screen overlay
        self.overlay = QtWidgets.QWidget(self.widget)
        self.overlay.setGeometry(self.widget.rect())
        self.consoleDisplay = QtWidgets.QPlainTextEdit(self.overlay)
        self.consoleDisplay.setGeometry(0, 0, self.overlay.width(), self.overlay.height())
        # Styling
        default_font = QtWidgets.QApplication.font()
        default_font.setPointSize(8) 
        self.consoleDisplay.setFont(default_font)
        
        # Start the card-making process in a new thread
        thread = threading.Thread(target=self.parent.makeCards, args=(deckName, self.messageQueue, self.parent.defaultOutputFolder))
        thread.daemon = True
        thread.start()
        
        # Start a timer to periodically check the queue and update the console display
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.checkQueue)
        self.timer.start(100)  # Check every 100 ms

        self.overlay.show()
        
    def __openFileDefault(self):
        filename = self.parent.defaultNoteLocation
        logger.info(f"File(s) selected for card generation input: {filename}")
        self.parent.currentInputFilePath = filename
        
        f = open(filename, 'r', encoding="utf-8")
        with f:
            data = f.read()
            self.parent.selectedFileContent = data
            
    def append_to_console_display(self, text):
        """Append text to the console display.

        :param text: Text sent from the card making thread.
        :type text: str
        """
        self.consoleDisplay.moveCursor(QtGui.QTextCursor.End)
        self.consoleDisplay.insertPlainText(text + '\n')
        self.consoleDisplay.moveCursor(QtGui.QTextCursor.End)
        
    def checkQueue(self):
        """Check the message queue for new messages.
        """
        while not self.messageQueue.empty():
            message = self.messageQueue.get()
            self.append_to_console_display(message)


class GuiContactDialog(object):
    """The contact dialog.
    """
    
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(311, 249)
        self.widget = QtWidgets.QWidget(Dialog)
        self.widget.setGeometry(QtCore.QRect(20, 20, 271, 211))
        self.widget.setObjectName("widget")
        self.gridLayout = QtWidgets.QGridLayout(self.widget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(self.widget)
        self.label.setTextFormat(QtCore.Qt.MarkdownText)
        self.label.setWordWrap(True)
        self.label.setOpenExternalLinks(True)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.widget)
        self.label_2.setTextFormat(QtCore.Qt.MarkdownText)
        self.label_2.setWordWrap(True)
        self.label_2.setOpenExternalLinks(True)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.widget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setContentsMargins(0, 10, 0, 0)
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.widget)
        self.label_3.setTextFormat(QtCore.Qt.MarkdownText)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept) # type: ignore
        self.buttonBox.rejected.connect(Dialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Contact"))
        self.label.setText(_translate("Dialog", "If you find any **bugs**, have any **suggestions**, or would just like to say hi, feel free to contact me at: <a href='mailto:jdayn@protonmail.com'><span style='color:#2e8fff'>jdayn@protonmail.com</span></a>\n\n\nYou can also make changes and submit a pull request:\n<a href='https://github.com/Jyldn/AutoAnki'><span style='color:#2e8fff'>github.com/Jyldn/AutoAnki</span></a>"))
        self.label_2.setText(_translate("Dialog", "If you find this useful and would like to give me a tip: <a href='www.ko-fi.com/jyldn'><span style='color:#2e8fff'>www.ko-fi.com/jyldn</span></a>"
""))
        self.label_3.setText(_translate("Dialog", "✨ **Contact Me** ✨"))


class GuiChangeLangWindow(object):
    """The change language dialog.
    """
    def __init__(self, parent):
        self.parent = parent
        self.tempLang = ""
        self.window = ""
    
    def setupUi(self, changeLangWindow):
        self.window = changeLangWindow
        changeLangWindow.setObjectName("changeLangWindow")
        changeLangWindow.resize(100, 185)
        self.gridLayout_4 = QtWidgets.QGridLayout(changeLangWindow)
        self.gridLayout_4.setObjectName("gridLayout_4")
        
        # Change lang W frame
        self.changeLangWFrame = QtWidgets.QFrame(changeLangWindow)
        self.changeLangWFrame.setMaximumSize(QtCore.QSize(100, 200))
        self.changeLangWFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.changeLangWFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.changeLangWFrame.setObjectName("changeLangWFrame")
        self.changeLangWFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.changeLangWFrame.setStyleSheet("QFrame#changeLangWFrame { border: 0px solid black; }")
        self.changeLangWFrame.setStyleSheet("QFrame {border: 0px; margin: 0px;}")
        
        # Grid layout 3
        self.gridLayout_3 = QtWidgets.QGridLayout(self.changeLangWFrame)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setSpacing(0)
        
        self.changeLangConf = QtWidgets.QDialogButtonBox(self.changeLangWFrame)
        self.changeLangConf.setOrientation(QtCore.Qt.Horizontal)
        self.changeLangConf.setStandardButtons(QtWidgets.QDialogButtonBox.Apply)
        self.changeLangConf.clicked.connect(self.__handleApply)
        self.changeLangConf.setCenterButtons(True)
        self.changeLangConf.setObjectName("changeLangConf")

        # Change language list
        self.langsList = QtWidgets.QListWidget(self.changeLangWFrame)
        self.langsList.setMaximumSize(QtCore.QSize(74, 16777215))
        self.langsList.setObjectName("langsList")
        item = QtWidgets.QListWidgetItem()
        self.langsList.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.langsList.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.langsList.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.langsList.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.langsList.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.langsList.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.langsList.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.langsList.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.langsList.addItem(item)
        # Add border
        self.langsList.setStyleSheet("QFrame {border: 0px solid lightgrey;}")
        self.gridLayout_3.addWidget(self.langsList, 0, 0, 1, 1)
        self.gridLayout_4.addWidget(self.changeLangWFrame, 0, 0, 1, 1)
        self.gridLayout_4.addWidget(self.changeLangConf, 1, 0, 1, 1)
        
        self.__retranslateUi(changeLangWindow)
        QtCore.QMetaObject.connectSlotsByName(changeLangWindow)
    
    def __retranslateUi(self, changeLangWindow):
        _translate = QtCore.QCoreApplication.translate
        changeLangWindow.setWindowTitle(_translate("changeLangWindow", "Language Settings"))
        __sortingEnabled = self.langsList.isSortingEnabled()
        
        self.langsList.setSortingEnabled(False)
        item1 = self.langsList.item(0)
        item1.setText(_translate("changeLangWindow", "Arabic"))
        item2 = self.langsList.item(1)
        item2.setText(_translate("changeLangWindow", "English"))
        item3 = self.langsList.item(2)
        item3.setText(_translate("changeLangWindow", "French"))
        item4 = self.langsList.item(3)
        item4.setText(_translate("changeLangWindow", "German"))
        item5 = self.langsList.item(4)
        item5.setText(_translate("changeLangWindow", "Japanese"))
        item6 = self.langsList.item(5)
        item6.setText(_translate("changeLangWindow", "Korean"))
        item7 = self.langsList.item(6)
        item7.setText(_translate("changeLangWindow", "Latin"))
        item8 = self.langsList.item(7)
        item8.setText(_translate("changeLangWindow", "Persian"))
        item9 = self.langsList.item(8)
        item9.setText(_translate("changeLangWindow", "Spanish"))
        self.langsList.setSortingEnabled(__sortingEnabled)
        self.langsList.clicked.connect(self.__updateSelection)
        item1.setHidden(True)
        item5.setHidden(True)
        item6.setHidden(True)
        item8.setHidden(True)

        # Check what the currently saved language is in the parent GUI object and apply that visually to the selection 
        # list.
        langIndex = self.__indexLang()
        if langIndex == 1:
            langItem =  item1
        elif langIndex == 2:
            langItem =  item2
        elif langIndex == 3:
            langItem =  item3
        elif langIndex == 4:
            langItem =  item4
        elif langIndex == 5:
            langItem =  item5
        elif langIndex == 6:
            langItem =  item6
        elif langIndex == 7:
            langItem =  item7
        elif langIndex == 8:
            langItem =  item8
        elif langIndex == 9:
            langItem =  item9
        else:
            langItem = None  # or some default value
        self.__highlightCurrentLang(langItem)
    
    def __handleApply(self):
        """Applies the selected language by updating the main window language variable.
        """
        if self.tempLang:
            self.parent.changeLanguage(self.tempLang)
        self.window.close()
    
    def __highlightCurrentLang(self, item):
        """Highlight the currently selected language on the selection list.

        :param item: The currently selected language.
        :type item: QtWidgets.QListWidgetItem
        """
        self.langsList.setCurrentItem(item)
        self.langsList.setFocus()
    
    def __updateTempLangVar(self, lang):
        """Updates the language var used to save, temporarily, when a user clicks on a language list object, but is yet 
        to save that as their selection.

        :param lang: The language to be saved.
        :type lang: str
        """
        self.tempLang = lang
    
    def __getCurrentLangSelection(self):
        """Get the currently selected language from the list of languages GUI element.

        :return: The currently selected language.
        :rtype: str
        """
        selection = self.langsList.currentRow()
        selection += 1
        selection = LANGS[str(selection)]
        return selection
    
    def __updateSelection(self):
        """Update the program with the currently selected (temporary, not yet applied) language selection from the list.
        """
        selection = self.__getCurrentLangSelection()
        self.__updateTempLangVar(selection)
    
    def __indexLang(self):
        """Determine which list element a language corresponds with.

        :return: The index of the language.
        :rtype: int
        """
        lang = self.parent.getCurrentLang()
        # print(lang)
        if lang == "Arabic":
            return 1
        elif lang == "English":
            return 2
        elif lang == "French":
            return 3
        elif lang == "German":
            return 4
        elif lang == "Japanese":
            return 5
        elif lang == "Korean":
            return 6
        elif lang == "Latin":
            return 7
        elif lang == "Persian":
            return 8
        elif lang == "Spanish":
            return 9
        else:
            return None  # or some default value
        

class GuiSettingsDialog(object):
    """The settings dialog.
    """
    def __init__(self, parent):
        self.parent = parent
    
    def setupUi(self, settingsDialog):
        self.window = settingsDialog
        settingsDialog.setObjectName("settingsDialog")
        settingsDialog.resize(308, 143)
        self.gridLayout_2 = QtWidgets.QGridLayout(settingsDialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.settingsFrame = QtWidgets.QFrame(settingsDialog)
        self.settingsFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.settingsFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.settingsFrame.setObjectName("settingsFrame")
        self.gridLayout = QtWidgets.QGridLayout(self.settingsFrame)
        self.gridLayout.setObjectName("gridLayout")
        
        # Header preset
        headerFont = QtGui.QFont()
        headerFont.setBold(True)
        
        # First header
        self.generalSettingsLbl = QtWidgets.QLabel(self.settingsFrame)
        self.generalSettingsLbl.setObjectName("generalSettingsLbl")
        self.generalSettingsLbl.setContentsMargins(0, 0, 0, 0)
        self.generalSettingsLbl.setFont(headerFont)
        self.gridLayout.addWidget(self.generalSettingsLbl, 0, 0, 1, 1)
        
        # Interface language
        self.settingsLangLbl = QtWidgets.QLabel(self.settingsFrame)
        self.settingsLangLbl.setObjectName("settingsLangLbl")
        self.gridLayout.addWidget(self.settingsLangLbl, 1, 0, 1, 1)
        self.interfaceLangCB = QtWidgets.QComboBox(self.settingsFrame)
        self.interfaceLangCB.setMaximumSize(QtCore.QSize(130, 16777215))
        self.interfaceLangCB.setObjectName("interfaceLangCB")
        self.interfaceLangCB.addItem("")
        self.gridLayout.addWidget(self.interfaceLangCB, 1, 1, 1, 1)
        
        # Colour mode
        self.settingsColMdLbl = QtWidgets.QLabel(self.settingsFrame)
        self.settingsColMdLbl.setObjectName("settingsColMdLbl")
        self.gridLayout.addWidget(self.settingsColMdLbl, 2, 0, 1, 1)
        self.defaultColourModeCB = QtWidgets.QComboBox(self.settingsFrame)
        self.defaultColourModeCB.setMaximumSize(QtCore.QSize(130, 16777215))
        self.defaultColourModeCB.setObjectName("defaultColourModeCB")
        self.defaultColourModeCB.addItem("")
        self.defaultColourModeCB.addItem("")
        self.gridLayout.addWidget(self.defaultColourModeCB, 2, 1, 1, 1)
        
        # Font size
        self.fontSizeSelectLbl = QtWidgets.QLabel(self.settingsFrame)
        self.fontSizeSelectLbl.setObjectName("fontSizeSelectLbl")
        self.gridLayout.addWidget(self.fontSizeSelectLbl, 3, 0, 1, 1)
        self.fontSizeSelect = QtWidgets.QSpinBox(self.settingsFrame)
        self.fontSizeSelect.setMinimum(25)
        self.fontSizeSelect.setMaximum(500)
        self.fontSizeSelect.setMaximumSize(QtCore.QSize(130, 16777215))
        self.fontSizeSelect.setObjectName("fontSizeSelect")
        
        # Handle zoom factor
        zoomFactor = self.parent.getZoomFactor()
        zoomFactor = self.convertZoomLevel(zoomFactor)
        self.fontSizeSelect.setValue(zoomFactor)
        self.gridLayout.addWidget(self.fontSizeSelect, 3, 1, 1, 1)
        
        # Default load location
        self.defaultLoadLbl = QtWidgets.QLabel(self.settingsFrame)
        self.defaultLoadLbl.setObjectName("defaultLoadLbl")
        self.gridLayout.addWidget(self.defaultLoadLbl, 4, 0, 1, 1)
        self.defaultLoadEdit = QtWidgets.QLineEdit(self.settingsFrame)
        self.gridLayout.addWidget(self.defaultLoadEdit, 4, 1, 1, 1)
        
        # Default save location 
        self.defaultSaveLbl = QtWidgets.QLabel(self.settingsFrame)
        self.defaultSaveLbl.setObjectName("defaultSaveLbl")
        self.gridLayout.addWidget(self.defaultSaveLbl, 5, 0, 1, 1)
        self.defaultSaveEdit = QtWidgets.QLineEdit(self.settingsFrame)
        self.gridLayout.addWidget(self.defaultSaveEdit, 5, 1, 1, 1)
        
        # Tutorial settings
        self.tutorialLbl = QtWidgets.QLabel(self.settingsFrame)
        self.tutorialLbl.setObjectName("tutorialLbl")
        self.gridLayout.addWidget(self.tutorialLbl, 6, 0, 1, 1)
        self.tutorialRadio = QtWidgets.QCheckBox(self.settingsFrame)
        self.gridLayout.addWidget(self.tutorialRadio, 6, 1, 1, 1)
        
        # Additional search settings
        self.searchSettingsLbl = QtWidgets.QLabel(self.settingsFrame)
        self.searchSettingsLbl.setObjectName("searchSettingsLbl")
        self.searchSettingsLbl.setContentsMargins(0, 20, 0, 0)
        self.searchSettingsLbl.setFont(headerFont)
        self.gridLayout.addWidget(self.searchSettingsLbl, 7, 0, 1, 1)
        
        # Etymology
        self.getEtymLbl = QtWidgets.QLabel(self.settingsFrame)
        self.getEtymLbl.setObjectName("getEtymLbl")
        self.gridLayout.addWidget(self.getEtymLbl, 8, 0, 1, 1)
        self.etymRadio = QtWidgets.QCheckBox(self.settingsFrame)
        self.gridLayout.addWidget(self.etymRadio, 8, 1, 1, 1)
        
        # Usage notes
        self.getUsageLbl = QtWidgets.QLabel(self.settingsFrame)
        self.getUsageLbl.setObjectName("getUsageLbl")
        self.gridLayout.addWidget(self.getUsageLbl, 9, 0, 1, 1)
        self.usageRadio = QtWidgets.QCheckBox(self.settingsFrame)
        self.gridLayout.addWidget(self.usageRadio, 9, 1, 1, 1)
        
        # Bold key term in definition
        self.defInConjLbl = QtWidgets.QLabel(self.settingsFrame)
        self.defInConjLbl.setObjectName("defInConjLbl")
        self.gridLayout.addWidget(self.defInConjLbl, 10, 0, 1, 1)
        self.defInConjRadio = QtWidgets.QCheckBox(self.settingsFrame)
        self.gridLayout.addWidget(self.defInConjRadio, 10, 1, 1, 1)
        
        # Apply layout
        self.gridLayout_2.addWidget(self.settingsFrame, 0, 0, 1, 1)
        
        # Confirmation buttons
        self.settingsBox = QtWidgets.QDialogButtonBox(settingsDialog)
        self.settingsBox.setOrientation(QtCore.Qt.Horizontal)
        self.settingsBox.setStandardButtons(QtWidgets.QDialogButtonBox.Apply)
        self.settingsBox.clicked.connect(self.__handleApplySettings)
        
        self.settingsBox.setObjectName("settingsBox")
        self.gridLayout_2.addWidget(self.settingsBox, 1, 0, 1, 1)
        
        self.retranslateUi(settingsDialog)
        self.settingsBox.accepted.connect(settingsDialog.accept) # type: ignore
        self.settingsBox.rejected.connect(settingsDialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(settingsDialog)
        
        colourMode = self.parent.getColourMode()
        if colourMode == "dark":
            stylesheet = qtvsc.load_stylesheet(qtvsc.Theme.DARK_VS)
        else:
            stylesheet = qtvsc.load_stylesheet(qtvsc.Theme.LIGHT_VS)
        
        self.window.setStyleSheet(stylesheet)
        self.settingsFrame.setStyleSheet("QFrame {border: 0px solid dimgrey;}")    
    
    def retranslateUi(self, settingsDialog):
        _translate = QtCore.QCoreApplication.translate
        settingsDialog.setWindowTitle(_translate("settingsDialog", "Settings"))
        # Interface language select
        self.settingsLangLbl.setText(_translate("settingsDialog", "Interface Language"))
        self.interfaceLangCB.setItemText(0, _translate("settingsDialog", "English"))
        # Colour mode
        self.settingsColMdLbl.setText(_translate("settingsDialog", "Default Colour Mode"))
        self.defaultColourModeCB.setItemText(0, _translate("settingsDialog", "Light"))
        self.defaultColourModeCB.setItemText(1, _translate("settingsDialog", "Dark"))
        
        # Set colour mode selection to current config value
        if self.parent.configColourMode == "dark":
            self.defaultColourModeCB.setCurrentIndex(1)
        else:
            self.defaultColourModeCB.setCurrentIndex(0)
        
        # Font size
        self.fontSizeSelectLbl.setText(_translate("settingsDialog", "Zoom percentage"))
        # Tutorial
        self.tutorialLbl.setText(_translate("tutorialSetting", "Show tutorial"))
        self.checkBoxes()
        self.__getLocations()
        
        self.getEtymLbl.setText(_translate("getEtymLbl", "Show etymology"))
        self.getUsageLbl.setText(_translate("getUsageLbl", "Show usage notes"))
        self.searchSettingsLbl.setText(_translate("searchSettingsLbl", "Manual search settings"))
        self.generalSettingsLbl.setText(_translate("generalSettingsLbl", "General settings"))
        self.defInConjLbl.setText(_translate("defInConjLbl", "Definition + conjugation"))
        self.defaultLoadLbl.setText(_translate("defaultLoadLbl", "Default notes file"))
        self.defaultSaveLbl.setText(_translate("defaultSaveLbl", "Default output folder"))
        
    def convertZoomLevel(self, zoomLevel):
        """Converts the zoom level from a flaot to an int.
        
        :param zoomLevel: The zoom level, as a float.
        :type zoomLevel: float
        :return: The zoom level as an int.
        :rtype: int
        """
        zoomLevel = int(zoomLevel* 100)
        return zoomLevel
    
    def __handleApplySettings(self):
        """Applies the selected language by updating the GUI language variable and then closes the dialog.
        """
        # Get settings variables
        newZoomFactor = self.fontSizeSelect.value()
        newColourSelect = self.defaultColourModeCB.currentText()
        newColourSelect = newColourSelect.lower()
        
        self.__applyChecks()
        self.__applyLocations()
        self.parent.applySettings(newZoomFactor, newColourSelect)
        self.parent.updateConfig()
        self.window.close()
    
    def checkBoxes(self):
        """Check the tutorial setting.
        """
        if self.parent.showTutorial == "True":
            self.tutorialRadio.setChecked(True)
        else:
            self.tutorialRadio.setChecked(False)
        
        if self.parent.getEtymology == "True":
            self.etymRadio.setChecked(True)
        else:
            self.etymRadio.setChecked(False)
        
        if self.parent.getUsage == "True":
            self.usageRadio.setChecked(True)
        else:
            self.usageRadio.setChecked(False)
            
        if self.parent.defInConj == "True":
            self.defInConjRadio.setChecked(True)
        else:
            self.defInConjRadio.setChecked(False)
    
    def __applyChecks(self):
        """Apply the tutorial setting.
        """
        if self.tutorialRadio.isChecked():
            self.parent.showTutorial = "True"
        else:
            self.parent.showTutorial = "False"
            
        if self.etymRadio.isChecked():
            self.parent.getEtymology = "True"
        else:
            self.parent.getEtymology = "False"
            
        if self.usageRadio.isChecked():
            self.parent.getUsage = "True"
        else:
            self.parent.getUsage = "False"
            
        if self.defInConjRadio.isChecked():
            self.parent.defInConj = "True"
        else:
            self.parent.defInConj = "False"
    
    def __applyLocations(self):
        self.parent.defaultNoteLocation = self.defaultLoadEdit.text()
        self.parent.defaultOutputFolder = self.defaultSaveEdit.text()
        
    def __getLocations(self):
        self.defaultLoadEdit.setText(self.parent.defaultNoteLocation)
        self.defaultSaveEdit.setText(self.parent.defaultOutputFolder)
        

def config_check():
    """Checks if a config file exists. If not, creates one.
    
    :return: A list of config variables.
    :rtype: list
    """
    if os.path.exists("config.ini"):
        logger.info("Config file found.")
    else:
        logger.info("No config file found. Creating a new one.")
        setup_config()
    config_vars = get_configs()
    return config_vars


def setup_config():
    """Creates a new config file with default values.
    """
    config = configparser.ConfigParser()
    config['LanguagePreferences'] = {'InterfaceLanauge': 'English', 'SearchLanguage': 'English'}
    config['Interface'] = {'ColourMode': 'light', 'ZoomLevel': 100}
    config['Behaviour'] = {'ShowTutorial': True}
    config['ManualSearch'] = {'Etymology': False, 'UsageNotes': False, 'defInConj': False}
    config['DefaultLocations'] = {'defaultNotesFile': False, 'defaultOutputFolder': False}
    
    with open("config.ini", 'w') as configfile:
        config.write(configfile)
    
    logger.info("New config file generated.")


def get_configs():
    """Gets the config variables from the config file.
    
    :return: List of config variables.
    :rtype: list
    """
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    # Get the config variables
    interface_language = config['LanguagePreferences']['InterfaceLanauge']
    search_language = config['LanguagePreferences']['SearchLanguage']
    colour_mode = config['Interface']['ColourMode']
    zoom_level = int(config['Interface']['ZoomLevel'])
    show_tutorial = config['Behaviour']['ShowTutorial']
    get_etymology = config['SearchSettings']['GetEtymology']
    get_usage_notes = config['SearchSettings']['GetUsage']
    bold_key = config['SearchSettings']['defInConj']
    default_note_location = config['DefaultLocations']['defaultNotesFile']
    default_output_folder = config['DefaultLocations']['defaultOutputFolder']
    
    config_vars = [interface_language, search_language, colour_mode, zoom_level, show_tutorial, get_etymology, get_usage_notes, bold_key, default_note_location, default_output_folder]
    return config_vars  


def is_phrase(word):
    """Checks if a word is a phrase.
    
    :param word: The word to be checked.
    :type word: str
    :return: True if the word is a phrase, False otherwise.
    :rtype: bool
    """
    if word.count(" ") > 0:
        return True
    else:
        return False


def find_keywords(dict_array):
    """Finds keywords in the text submitted by the user.
    Keywords are designated by adding an * before the keyword.
    Keyphrases are wrapped in hashtags (#).
    
    :param dict_array: The array of dictionaries being used to create Anki cards. Each dictionary represents a card.
    :type dict_array: list
    :return: The array of dictionaries, now with added keyword entries.
    :rtype: list
    """
    pattern_word = r"\*(\w+)"
    pattern_phrase = r"#(.*?)#"

    for dictionary in dict_array:
        text = dictionary.get("text")
        words = re.findall(pattern_word, text)
        phrases = re.findall(pattern_phrase, text)
        dictionary["words"] = words + phrases
    
    return dict_array


def get_tags(dict_array, language, nlp):
    """Gets the grammatical tags for the user's marked words.
    
    :param dict_array: Array of dictionaries, each dictionary representing an Anki card.
    :type dict_array: list
    :param language: Language being used.
    :type language: str
    :param nlp: The SpaCy nlp object.
    :type nlp: spacy.lang
    :return: The array of dictionaries, now with added tags entries.
    :rtype: list
    """
    for count, dictionary in enumerate(dict_array):
        print(f">>> {dict_array}")
        words_and_nltk_tags = determine_grammar(dictionary["words"], dictionary["text"], language, nlp)
        dict_array[count]["tags"] = words_and_nltk_tags
    return dict_array


def determine_grammar(words: list, text, lang, nlp):
    """Determine the grammatical tags for each word in the text.
    
    :param words: The words to be tagged.
    :type words: list
    :param text: The text that contains the target words.
    :type text: str
    :param lang: The language being used.
    :type lang: str
    :param nlp: The SpaCy nlp object.
    :type nlp: spacy.lang
    :return: The words and their tags.
    :rtype: list
    """
    nltk_tags = []
    # Remove punctuation
    text = strip_punctuation(text)
    # Process the text using SpaCy
    doc = nlp(text)
    
    # Convert each token to NLTK tag if the token text is in the words list    
    for word in words:
        if is_phrase(word):
            word.replace("#", "")
            nltk_tags.append([word, 'Phrase'])
        else:
            for w_count, token in enumerate(doc):
                if token.text == word:
                    # Find the equivalent NLTK tag for the SpaCy tag from the mapping
                    nltk_tag = SPACY_TO_NLTK_TAG_MAP.get(token.pos_, 'NN')  # Default to 'NN' if not found        
                    # Because spacy seems to be identifying German nouns as proper nouns (due to capitalisation),
                    # all NNPs need to be converted to NNs, despite this being inaccurate.
                    if nltk_tag == 'NNP':
                        nltk_tag = 'NN'
                    nltk_tags.append([token.text, nltk_tag])
                    logger.info(f"Tagged {token.text} as {nltk_tag}")
    return nltk_tags


def strip_punctuation(text):
    """Remove punctuation from a string.
    
    :param text: The text to be stripped of punctuation.
    :type text: str
    :return: The text with punctuation removed.
    :rtype: str
    """
    # Remove apostrophes in the middle of words, but ensure a space is put in their place. 
    # Iterate over each character in the text string.
    new_text = ''
    for i in range(len(text)):
        if text[i] == "'":
            if i > 0 and i < len(text) - 1:
                # Check if the character is surrounded by alphabetical characters.
                if text[i-1].isalpha() and text[i+1].isalpha():
                    new_text += ' '
                    continue
        new_text += text[i]

    # Remove other punctuation
    exclude = set(string.punctuation) - {"'"}
    for ch in exclude:
        new_text = new_text.replace(ch, '')

    # Split the text into words and rejoin to remove extra spaces
    return ' '.join(new_text.split())


def match_tags(dict_array):
    """Match the nltk grammar tags with more general (and comprehensible) tags.
    
    :param dict_array: The array of dictionaries being used to create Anki cards. Each dictionary represents a card.
    :type dict_array: list
    :return: The array of dictionaries, now with more general and readable tags.
    :rtype: list
    """
    for dict_index, dictionary in enumerate(dict_array):
        for tags_index, tags in enumerate(dictionary["tags"]):
            # print(f"><><>< {dict_array}")
            for tag_index, tag in enumerate(tags):
                logger.info(f"Match tags function: tag < {tag} > found in dictionary tags array.")
                for readable_tag, nltk_tags in NLTK_TAG_REF.items():
                    for nltk_tag in nltk_tags:
                        if nltk_tag == tag:
                            new_tag = readable_tag
                            this_word = dict_array[dict_index]["tags"][tags_index][tag_index][0]
                            dict_array[dict_index]["tags"][tags_index] = [this_word, new_tag]
                            logger.info(f"Changed < {tag} > to > {new_tag} <")	
    return dict_array


def grab_wik(text, language, get_etymology, get_usage_notes, bold_key):
    """Grab the Wiktionary definitions for a single word.
    """
    page_content = get_wiktionary_definition(text)
    if page_content:
        parsed_definitions_dict = parse_page(page_content, language, "manualsearch", get_etymology, get_usage_notes, text)
        if parsed_definitions_dict:
            cleaned_definitions = clean_wikitext_mansearch(parsed_definitions_dict, bold_key)
            return cleaned_definitions
        else:
            logger.warning(f"Failed to parse page for < {text} >.")
            return False
    else:
        logger.warning(f"Failed to get definition for < {text} >.")
        return False


def get_wiktionary_url(word):
    """Get the URL for a word on Wiktionary.
    
    :param word: The word to be looked up.
    :type word: str
    :return: The URL for the word on Wiktionary.
    :rtype: str
    """
    base_url = "https://en.wiktionary.org/wiki/"
    # Construct the URL by appending the word to the base URL
    url = f"{base_url}{word}"
    return url


def grab_wik_conjtable(text, language):
    """Grab the Wiktionary conjugation table for a single word.
    
    :param text: The text provided by the user.
    :type text: str
    :param language: The language being used.
    :type language: str
    :return: The conjugation table.
    :rtype: str
    """
    logger.info(f"Getting conjugation table for {text}")
    # Get the URL
    wik_url = get_wiktionary_url(text)
    # Send a request to the URL
    response = requests.get(wik_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Find the language section
    lang_section = soup.find('span', {"class": "mw-headline", "id": f"{language}"})
    
    if lang_section:
        # Navigate to the parent of the span, which should be h2, then to subsequent content
        content = lang_section.parent
        
        # Now find the conjugation header within the English section
        conjugation_header = content.find_next('span', id='Conjugation')
        if not conjugation_header:
            conjugation_header = content.find_next('span', id='Conjugation_2')
        if not conjugation_header:
            conjugation_header = content.find_next('span', id='Conjugation_3')
        if not conjugation_header:
            conjugation_header = content.find_next('span', id='Conjugation_4')
        
        if conjugation_header:
            table = conjugation_header.find_next('table')
            if table:
                return str(table)
            else:
                return "Could not find conjugation table."
        else:
            return "Could not find conjugation header"
    else:
        return "Language section not found."


def strip_bs4_links(html_content):
    """Remove all links from HTML content.
    
    :param html_content: The HTML content to be modified.
    :type html_content: str
    :return: Cleaned HTML content.
    :rtype: str
    """
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    # Find all <a> tags and replace them with their text content
    for link in soup.find_all('a'):
        link.replace_with(link.text)
    return str(soup)


def get_wiktionary_conjugations(word):
    """Get the conjugations for a word from Wiktionary.
    
    :param word: The word to be looked up.
    :type word: str
    :return: The conjugations for the word.
    :rtype: str
    """
    endpoint = "https://en.wiktionary.org/w/api.php"
    params = {
        "action": "parse",
        "page": word,
        "format": "json",
        "prop": "text",
        "redirects": True,
    }
    
    # Make the request to the MediaWiki API
    response = requests.get(endpoint, params=params)
    data = response.json()
    
    # Extract the HTML content from the response
    html_content = data["parse"]["text"]["*"]
    
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Assuming the conjugation table is in a section with a certain class or id
    # This might vary and needs to be adjusted based on actual page structure
    # Adjust the selector as needed
    conj_section = soup.find(class_='conjugation')
    
    return conj_section


def get_wiktionary_definition(word):
    """Get the definition of a word from wiktionary.
    
    :param word: The word to be looked up.
    :type word: str
    :return: The definition of the word.
    :rtype: _type_
    """
    url = "https://en.wiktionary.org/w/api.php"
    params = {
        "action": "query",
        "titles": word,
        "prop": "revisions",
        "rvprop": "content",
        "format": "json",
        "rvslots": "*"
    }
    
    # Make the API request
    response = requests.get(url, params=params)
    
    # Check for a successful response
    if response.status_code == 200:
        data = response.json()
        pages = data['query']['pages']
        
        # Extract the page
        page = next(iter(pages.values()))
        
        # Check if page exists
        if "revisions" in page:
            content = page['revisions'][0]['slots']['main']['*']
            return content 
        else:
            logger.warning(f"No definition found for < {word} >.")
            return False
    else:
        logger.warning(f"Failed to retrieve data from Wiktionary for < {word} >.")
        return False


def parse_page(page_content, language, mode, get_etymology, get_usage_notes, word):
    """Parse the page so that the content from relevant sections can be extracted.
    """
    parser = WiktionaryParser()
    wik_parser_result = parser.fetch(word, language)
    
    definitions = {}
    
    # if wik_parser_result[0]["definitions"][0]["partOfSpeech"] == "noun":
    for definition in wik_parser_result:
        for part_of_speech in definition["definitions"]:
            if part_of_speech["partOfSpeech"] == "noun":
                definitions["noun"] = part_of_speech["text"]
            if part_of_speech["partOfSpeech"] == "verb":
                definitions["verb"] = part_of_speech["text"]
            if part_of_speech["partOfSpeech"] == "adjective":
                definitions["adjective"] = part_of_speech["text"]
            if part_of_speech["partOfSpeech"] == "adverb":
                definitions["adverb"] = part_of_speech["text"]
            if part_of_speech["partOfSpeech"] == "pronoun":
                definitions["pronoun"] = part_of_speech["text"]
            if part_of_speech["partOfSpeech"] == "preposition":
                definitions["preposition"] = part_of_speech["text"]
            if part_of_speech["partOfSpeech"] == "particle":
                definitions["particle"] = part_of_speech["text"]
            if part_of_speech["partOfSpeech"] == "conjunction":
                definitions["conjunction"] = part_of_speech["text"]
            if part_of_speech["partOfSpeech"] == "article":
                definitions["article"] = part_of_speech["text"]
            if part_of_speech["partOfSpeech"] == "numeral":
                definitions["numeral"] = part_of_speech["text"]
            if part_of_speech["partOfSpeech"] == "interjection":
                definitions["interjection"] = part_of_speech["text"]
            if part_of_speech["partOfSpeech"] == "exclamation":
                definitions["exclamation"] = part_of_speech["text"]
            if part_of_speech["partOfSpeech"] == "determiner":
                definitions["determiner"] = part_of_speech["text"]
        
        if mode == "manualsearch":
            if get_etymology == "True":
                if wik_parser_result[0]["etymology"] != "":
                    definitions["etymology"] = [wik_parser_result[0]["etymology"]]
            
            if get_usage_notes == "True":
                r_lang = "==" + language + "=="
                try:
                    lang_section = re.search(rf'{r_lang}\n(.*?)(?=\n==[^=]|$)', page_content, re.DOTALL)
                    lang_content = lang_section.group(1)
                except:
                    logger.warning(f"No relevant << {language} >> definitions found in >>\n{page_content}\n<<")
                usage_section = re.findall(r'===Usage notes===\n(.*?)(\n==|\n===|$|$)', lang_content, re.DOTALL)
                if not usage_section:
                    usage_section = re.findall(r'====Usage notes====\n(.*?)(\n==|\n===|$)', lang_content, re.DOTALL)
                try:
                    definitions["usage"] = usage_section[0]
                except:
                    pass
            
        if any(definitions.values()):
            print(f"\nReturning: {definitions}\n")
            return definitions
        else:
            logger.warning(f"No definitions found in >>\n{page_content}\n If you see definitions here, that means there is either a problem with the code, or the part of speech is not being considered by the program. If you think this is an oversight and that this particular part of speech should be added, please contact me via the contact form, or if you'd like to fix it yourself, submit a pull request on GitHub.")
            return False
        
    else:
        logger.warning(f"No definitions found in >>\n{page_content}\n If you see definitions here, that means there is either a problem with the code, or the part of speech is not being considered by the program. If you think this is an oversight and that this particular part of speech should be added, please contact me via the contact form, or if you'd like to fix it yourself, submit a pull request on GitHub.")
        return False


def clean_wikitext_mansearch(parsed_definitions_dict, bold_o):
    """Cleans the definitions pulled from Wiktionary so that they are legible.
    
    :param parsed_definitions_dict: The definitions pulled from Wiktionary.
    :type parsed_definitions_dict: dict
    :return: The cleaned definitions.
    :rtype: dict
    """
    clean_definitions = {
        "noun": [],
        "verb": [],
        "adjective": [],
        "adverb": [],
        "pronoun": [],
        "preposition": [],
        "particle": [],
        "conjunction": [],
        "article": [],
        "numeral": [],
        "interjection": [],
        "exclamation": [],
        "determiner": [],
        "etymology": [],
        "usage": []
    }
    
    for word_type, definitions in parsed_definitions_dict.items():
        for count, definition in enumerate(definitions):
            temp_cleaned_definition = definition    
            temp_cleaned_definition = temp_cleaned_definition.replace("(", "<span style='color:grey;font-size:0.85em;'>")
            temp_cleaned_definition = temp_cleaned_definition.replace(")", "</span>")
            temp_cleaned_definition = temp_cleaned_definition.replace("[", "<span style='color:grey;font-size:0.85em;'>")
            temp_cleaned_definition = temp_cleaned_definition.replace("]", "</span>")
            if count == 0:
                temp_cleaned_definition = temp_cleaned_definition.replace("plural ", "plural: ")
                temp_cleaned_definition = temp_cleaned_definition.replace("diminutive ", "diminutive: ")
                temp_cleaned_definition = temp_cleaned_definition.replace("genitive ", "genitive: ")
                temp_cleaned_definition = temp_cleaned_definition.replace("feminine ", "feminine: ")
                temp_cleaned_definition = temp_cleaned_definition.replace("masculine ", "masculine: ")
                temp_cleaned_definition = temp_cleaned_definition.replace("feminine: plural", "feminine plural")
                temp_cleaned_definition = temp_cleaned_definition.replace("masculine: plural", "masculine plural")
                temp_cleaned_definition = temp_cleaned_definition.replace("masculine: singular", "masculine singular:")
                temp_cleaned_definition = temp_cleaned_definition.replace("comparative ", "comparative: ")
                temp_cleaned_definition = temp_cleaned_definition.replace("superlative ", "superlative: ")
                temp_cleaned_definition = temp_cleaned_definition.replace("singular present", "singular present:")
                temp_cleaned_definition = temp_cleaned_definition.replace("past tense", "past tense:")
                temp_cleaned_definition = temp_cleaned_definition.replace("past participle", "past participle:")
                temp_cleaned_definition = temp_cleaned_definition.replace("past subjunctive", "past subjunctive:")
                temp_cleaned_definition = temp_cleaned_definition.replace("auxiliary", "auxiliary:")
                # temp_cleaned_definition = temp_cleaned_definition.replace("past tense", "past tense:")
                # temp_cleaned_definition = temp_cleaned_definition.replace("past tense", "past tense:")
                # temp_cleaned_definition = temp_cleaned_definition.replace("past tense", "past tense:")
                
                
                
                
                

            clean_definitions[word_type].append(temp_cleaned_definition)
            
    return clean_definitions


def clean_wikitext_card(definitions):
    """Cleans the definitions pulled from Wiktionary so that they are legible.
    
    :param definitions: The definitions pulled from Wiktionary.
    :type definitions: list
    :return: The cleaned definitions.
    :rtype: list
    """
    clean_definitions = []
    
    for definition in definitions:
        logger.info(f"Cleaning definition: {definition}")
        clean_definition_lines_list = []
        for count, line in enumerate(definition):
            temp_cleaned_definition_line = line
            temp_cleaned_definition_line = temp_cleaned_definition_line.replace(")", "</span>")
            temp_cleaned_definition_line = temp_cleaned_definition_line.replace("(", "<span style='color:grey;font-size:0.85em;'>")
            temp_cleaned_definition_line = temp_cleaned_definition_line.replace("]", "</span>")
            temp_cleaned_definition_line = temp_cleaned_definition_line.replace("[", "<span style='color:grey;font-size:0.85em;'>")
            if count == 0:
                temp_cleaned_definition_line = temp_cleaned_definition_line.replace("plural ", "plural: ")
                temp_cleaned_definition_line = temp_cleaned_definition_line.replace("diminutive ", "diminutive: ")
                temp_cleaned_definition_line = temp_cleaned_definition_line.replace("genitive ", "genitive: ")
                temp_cleaned_definition_line = temp_cleaned_definition_line.replace("feminine ", "feminine: ")
                temp_cleaned_definition_line = temp_cleaned_definition_line.replace("masculine ", "masculine: ")
                temp_cleaned_definition_line = temp_cleaned_definition_line.replace("feminine: plural", "feminine plural")
                temp_cleaned_definition_line = temp_cleaned_definition_line.replace("masculine: plural", "masculine plural")
                temp_cleaned_definition_line = temp_cleaned_definition_line.replace("masculine: singular", "masculine singular:")
                temp_cleaned_definition_line = temp_cleaned_definition_line.replace("comparative ", "comparative: ")
                temp_cleaned_definition_line = temp_cleaned_definition_line.replace("superlative ", "superlative: ")
                temp_cleaned_definition_line = temp_cleaned_definition_line.replace("singular present", "singular present:")
                temp_cleaned_definition_line = temp_cleaned_definition_line.replace("past tense", "past tense:")
                temp_cleaned_definition_line = temp_cleaned_definition_line.replace("past participle", "past participle:")
                temp_cleaned_definition_line = temp_cleaned_definition_line.replace("past subjunctive", "past subjunctive:")
                temp_cleaned_definition_line = temp_cleaned_definition_line.replace("auxiliary", "auxiliary:")
            clean_definition_lines_list.append(temp_cleaned_definition_line)

        clean_definitions.append(clean_definition_lines_list)
    
    logger.info(f"Cleaned definitions: {clean_definitions}")
        
    return clean_definitions


def stringify_def_dict(defs_dict):
    """Stirngy the definition for a single word as used by the single-word Wiktionary search function.
    
    :param defs_dict: Dictionary of definitions pulled from Wiktionary.
    :type defs_dict: dict
    :return: String of definitions
    :rtype: str
    """
    defs_string = ""
    for tag, definition in defs_dict.items():
        if definition:
            defs_string += f"{tag.capitalize()}\n"
            for line_no, string in enumerate(definition):
                defs_string += f"    {line_no}. {string}\n"
            defs_string += "\n"
    return defs_string


def remove_irrelevant_defs(dict_array):
    """Removes the definitions for the grammatical use of a word if that grammatical definition was not used in the 
    user's input text. The grammatical context is found in the card's dictionary 'tag' key.
    
    :param dict_array: The array of dictionaries being used to create Anki cards. Each dictionary represents a card.
    :type dict_array: list
    :return: The array of dictionaries, now with only the relevant definitions.
    :rtype: list
    """
    for dict_index, dictionary in enumerate(dict_array):
        # Individual Anki card
        new_card_definitions = []
        
        for word_index, word_definitions_dict in enumerate(dictionary["definitions"]):
            # Only do so if the target is a word, not a phrase.
            # Find a space in the word, if there is one, then it's a phrase.
            # Individual word definitions
            appropriate_word_def_found = False
            
            try:
                for grammar_key, definition in word_definitions_dict.items():
                    # Individual definitions for a word
                    
                    if definition and not appropriate_word_def_found:
                        try:
                            nltk_tag = dictionary["tags"][word_index][1]
                            if grammar_key == nltk_tag:
                                relevant_def = definition
                                if relevant_def:
                                    new_card_definitions.append(relevant_def)
                                    appropriate_word_def_found = True
                        except:
                            logger.warning(f"No tag found at index {word_index} in dictionary: >>\n{dictionary}\n<<")   
            except:
                logger.warning(f"No definition item at index in dictionary: >>\n{dictionary}\n<<")
            if appropriate_word_def_found:
                logger.info(f"Removing old dictionary for {dictionary['words']} and adding new one.")
            else:
                if dictionary["definitions"][word_index]:
                    # If the relevant definition is empty, use the longest definition available.
                    print(dictionary["definitions"][word_index].values())
                    word_definitions = dictionary["definitions"][word_index].values()
                    # Find the longest list item.
                    longest = max(word_definitions, key=len)
                    if is_phrase(dictionary["words"][word_index]) == False:
                        longest.append(f"Note: specific definition for the {dictionary['tags'][word_index][1]} form not found.")
                    new_card_definitions.append(longest) 
                    logger.warning(f"Couldn't find relevant definition for < {dictionary['words'][word_index]} >, using: \n{longest}") 
                else:
                    logger.warning(f"No user-marked words for < {dictionary['words'][word_index]} >, so no definition being used.") 
                    new_card_definitions.append(["No Definition not found. You might have made a typo, the word might not be in Wiktionary, or the language processor may have made a mistake."])            
    
        dict_array[dict_index]["definitions"] = new_card_definitions
    return dict_array


def read_sentence_file(text_file):
    """Read the text from the selected text file.
    
    :param text_file: The path to the text file.
    :type text_file: str
    :return: The text from the file.
    :rtype: str
    """
    try:
        with open(text_file, 'r', encoding="utf-8") as file:
            text = file.read()
    except:
        logger.error(f"Error reading user input file for AutoAnki process.")
        return False
    return text


def format_card(content, defs, words, tags, deck_name, lang):
    """Takes the information from a card dictionary and formats it so that it is readable by anki
    """
    logger.info(f"Formatting card for < {words} >")
    # Remove the "*" keyword marker(s) and bold them with html tags
    pattern = r"\*\w+"
    bolded_text = re.sub(pattern, lambda x: f"<b>{x.group()[1:]}</b>", content)
    pattern_phrase = r"#(.*?)#"
    bolded_text = re.sub(pattern_phrase, lambda x: f"<b>{x.group()[1:]}</b>", bolded_text)
    bolded_text = bolded_text.replace("#", "")
    
    # Column 1 - Original text
    ankified_text = bolded_text + ";\""
    
    # Column 2 - Definitions
    for count, definition in enumerate(defs):
        if count > 0:
            ankified_text += "<hr style='border: 1px dotted dimgrey;'>"
        
        tag = tags[count][1]
        ankified_text += f"<h3>{words[count]}</h3>{tag}, "

        for line_no, string in enumerate(definition):
            if line_no == 0:
                split_def = string.split()
                split_def = " ".join(split_def[1:])
                ankified_text += f"<i>{split_def}</i>"
            elif line_no == 1:
                ankified_text += "<ol>"
                ankified_text += f"<li>{string}</li>"
            else:
                ankified_text += f"<li>{string}</li>"
        ankified_text += "</ol>"
        
    ankified_text += "\";"
    
    # Column 3 - Deck
    ankified_text += f"deck:{deck_name}"
    ankified_text = ankified_text.replace("\n", "<br>")
    ankified_text = ankified_text.replace("</h3><br><br>", "</h3>")
    ankified_text = ankified_text.replace("(", "<span style='font-size:0.75em;'><i>")
    ankified_text = ankified_text.replace(")", "</i></span>")
        
    return ankified_text


def get_nlp(language):
    """Get the relevant SpaCy nlp object for the language being used.

    :param language: The language being used.
    :type language: str
    :return: The SpaCy nlp object.
    :rtype: spacy.lang
    """
    if language == "Arabic":
        stanza.download("ar")
        nlp = spacy_stanza.load_pipeline("ar", package="padt", processors='tokenize,mwt,pos,lemma', use_gpu=True)
    # English
    if language == "English":
        stanza.download("en")
        nlp = spacy_stanza.load_pipeline("en", package="partut", processors='tokenize,mwt,pos,lemma', use_gpu=True)
    # French
    elif language == "French":
        stanza.download("fr")
        nlp = spacy_stanza.load_pipeline("fr", package="partut", processors='tokenize,mwt,pos,lemma', use_gpu=True)
    # German
    if language == "German":
        stanza.download("de")
        nlp = spacy_stanza.load_pipeline("de", package="hdt", processors='tokenize,mwt,pos,lemma', use_gpu=True)
    # Japanese
    if language == "Japanese":
        stanza.download("ja")
        nlp = spacy_stanza.load_pipeline("ja", package="gsd", use_gpu=True)
    # Korean
    if language == "Korean":
        stanza.download("ko")
        nlp = spacy_stanza.load_pipeline("ko", package="kaist", processors='tokenize,mwt,pos,lemma', use_gpu=True)
    # Latin
    if language == "Latin":
        stanza.download("la")
        nlp = spacy_stanza.load_pipeline("la", package="llct", processors='tokenize,mwt,pos,lemma', use_gpu=True)
    # Persian
    if language == "Persina":
        stanza.download("fa")
        nlp = spacy_stanza.load_pipeline("fa", package="seraji", processors='tokenize,mwt,pos,lemma', use_gpu=True)
    # Spanish
    if language == "Spanish":
        stanza.download("es")
        nlp = spacy_stanza.load_pipeline("es", package="ancora", processors='tokenize,mwt,pos,lemma', use_gpu=True)
    return nlp


def make_cards(text_file, language, deck_name, messageQueue, saveFolder): 
    """Makes Anki cards from the text file.

    :param text_file: The path to the text file.
    :type text_file: str
    :param language: The language being used.
    :type language: str
    :param deck_name: The name of the deck to be used.
    :type deck_name: str
    :param messageQueue: The queue used to send messages to the GUI.
    :type messageQueue: queue.Queue
    :return: The Anki cards.
    :rtype: str
    """
    messageQueue.put("AutoAnki Started.")

    text = read_sentence_file(text_file)
    if text == False:
        logger.error(f"Error reading user input file for AutoAnki process. Perhaps the text file is empty, corrupted, or incorrectly formatted. File content: >>\n{text}\n<<")
        return False
    
    # Split lines. This assumes the user submitted their input using independent lines for each card.
    split_text = text.splitlines()
    
    dict_array = [
            {
                "text" : "",
                "words" : "",
                "tags" : "",
                "definitions" : []
            } for k in range(len(split_text))
        ]
    
    # Add each line of text to its own dictionary.
    for count, line in enumerate(split_text):
        dict_array[count]["text"] = line

    # Find the keywords. Should be designated with an asterisk before the word.
    messageQueue.put(f"Finding keywords.")
    dict_array = find_keywords(dict_array)
    
    # Get the relevant language package.
    messageQueue.put(f"Preparing language processor. This may take a moment, please wait.")
    nlp = get_nlp(language)
    
    # Get grammar tags for each word via nltk natural language processing.
    messageQueue.put(f"Getting grammar tags.")
    dict_array = get_tags(dict_array, language, nlp)
    # Match nltk tags to wiktionary tag types. This does nothing other than change the definitions of the tags being 
    # used in the dictionaries.
    dict_array = match_tags(dict_array)
    
    # Get definitions from Wiktionary.
    messageQueue.put(f"Making {str(len(dict_array))} cards.")
    for count, dictionary in enumerate(dict_array):
        messageQueue.put(f"Getting Wikti data for card {str(count+1)}/{str(len(dict_array))}...")
        for w_count, word in enumerate(dictionary.get("words")):
            if dictionary["tags"][w_count][1] in ["adjective", "verb", "noun"]:
                
                this_tag = dictionary["tags"][w_count][1]
                this_context = dictionary["text"]
                
                # Save the possibly declined version of the word.
                declined_word = word
                # Get lemma
                word = get_lemma(word, this_context, nlp)
                
                # Determine whether the word should be capitalised or not (Spacy returns lower case words).
                if language == "German":
                    if should_word_be_capitalised(declined_word) and this_tag == "noun":
                        word = word.capitalize()
                    else:
                        # If the word shouldn't be capitalised, make sure it's all lower case.
                        word = word.lower()
                    
                # Replace the word in the dictionary with the undeclined version.
                dict_array[count]["words"][w_count] = word
            if word:
                if language != "German":
                    word = word.lower()
                page_content = get_wiktionary_definition(word)
                parsed_definitions_dict = parse_page(page_content, language, "autoanki", False, False, word)
                dict_array[count]["definitions"].append(parsed_definitions_dict)
    
    # Remove irrelevent definitions.
    messageQueue.put(f"Processing cards.")
    dict_array = remove_irrelevant_defs(dict_array)
    
    # Clean definitions so that they're readable (remove HTML tags, etc.).
    messageQueue.put(f"Cleaning cards.")
    for count, dictionary in enumerate(dict_array):
        cleaned_defs = clean_wikitext_card(dictionary["definitions"])
        dict_array[count]["definitions"] = cleaned_defs
        
    # The text file which will be output and imported into Anki.
    anki_file = ""
    
    # The dictionaries are now ready to be used to create cards. They must be formatted so that Anki can read them and 
    # convert them.
    messageQueue.put(f"Formatting cards.")
    for count, dictionary in enumerate(dict_array):
        if count > 0:
            anki_file += "\n"
        anki_file += format_card(dictionary["text"], dictionary["definitions"], dictionary["words"], dictionary["tags"], deck_name, language)
    logger.info(f"Done.")
    
    # Save the cards to a single file for importing to Anki.
    if saveFolder == "":
        save_filename = f"{deck_name}_cards.txt"
        desktop_path = "D:\projects\software_dev\\autodict"
        full_file_path = f"D:\projects\software_dev\\autodict\{deck_name}_cards.txt"
    else:
        save_filename = f"{deck_name}_cards.txt"
        desktop_path = saveFolder
        full_file_path = f"{saveFolder}\{deck_name}_cards.txt"

    save_result = export_cards(save_filename, desktop_path, anki_file)
    if save_result:
        messageQueue.put(f"File saved to {full_file_path}")
    else:
        messageQueue.put(f"Error saving file to {full_file_path}")
    messageQueue.put(f"You can now close this window.")


def should_word_be_capitalised(word):
    """When Spacy undeclines a word, it returns that undeclined version of the word in all lower case. German nouns,
    however, are capitalised. This function determines whether a word should be capitalised or not so that
    capitalisation can be reinforced if necessary.
    
    :param word: The word being checked for its need for capitalisation.
    :type word: str
    :return: Boolean indicating whether the word should be capitalised or not.
    :rtype: bool
    """
    if word[0].isupper():
        return True
    else:
        return False


def export_cards(file_name, folder_path, anki_file):
    """Exports the Anki-formatted text file containing all generated Anki cards.
    
    :param file_name: The name of the file to be saved.
    :type file_name: str
    :param folder_path: The path to the save folder.
    :type folder_path: str
    :param anki_file: The Anki-formatted text file containing all generated Anki cards.
    :type anki_file: str
    :return: Whether the file was saved successfully.
    :rtype: bool
    """
    # Create the full file path
    full_file_path = os.path.join(folder_path, file_name)
    
    # Open the file at the specified location in write mode
    try:
        with open(full_file_path, 'w', encoding="utf-8") as file:
            file.write(anki_file)
        return True
    except Exception as e:
        print(e)


def get_lemma(target_word, context, nlp):
    """Returns the undeclined form of a delcined German word.
    
    :param target_word: The word to be undeclined.
    :type target_word: str
    :param context: The context in which the word is being used.
    :type context: str
    :param nlp: The SpaCy nlp object.
    :type nlp: spacy.lang
    :return: The undeclined form of the word.
    :rtype: str
    """
    # Strip punctuation from the context and target word.
    context = strip_punctuation(context)
    target_word = strip_punctuation(target_word)
    # Process the word using SpaCy
    lemmas = {}
    text = nlp(context)
    
    # Get all lemmas in text.
    for token in text:
        lemmas[token.text]  = token.lemma_
    
    # Get the lemma of the target word.
    lemma = lemmas[target_word]
        
    return lemma


if __name__ == "__main__":
    logger.info(f"Starting application.")
    
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(stylesheet)
    app.processEvents()
    MainWindow = QtWidgets.QDialog()
    MainWindow.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
    MainWindow.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
    
    gui = Gui()
    gui.setupUI(MainWindow)
    MainWindow.show()
    gui.spawnTutorial()
    sys.exit(app.exec_())