from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import QtWidgets, QtCore, QtGui
import PyQt5
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QTextEdit
from PyQt5.QtCore import Qt
from PyQt5 import QtWebEngineWidgets
from bs4 import BeautifulSoup
import uuid
import string
import stanza
import spacy_stanza
from spacy.lang.ja import Japanese
import logging
import requests
import re
import sys
import sys
import nltk
import os
import pprint
import configparser
import qtvscodestyle as qtvsc
import requests


# Logging
# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# configure the handler and formatter for logger2
handler = logging.FileHandler(f"{__name__}.log", mode='w')
formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
# add formatter to the handler
handler.setFormatter(formatter)
# add handler to the logger
logger.addHandler(handler)

QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True) #enable highdpi scaling
#QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True) #use highdpi icons
custom_colours = {"textLink.foreground": "#58a6ff"}
stylesheet = qtvsc.load_stylesheet(qtvsc.Theme.LIGHT_VS, custom_colours)
stylesheet_drk = qtvsc.load_stylesheet(qtvsc.Theme.DARK_VS, custom_colours)

html_header_dark = """
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

html_header_dark_conj = """
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

html_header_light = """
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

html_footer = """
        </body>
        </html>
        """

langs = {
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

nltk_tag_ref = {
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
    """Actually a Text Edit. Custom class needed to handle enter key presses. When user presses enter when using the
    text edit, the wiki search fuction is triggered.
    
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
    """The tutorial dialog that opens on startup. Whether this opens or not is determined my the config file.
    
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
            stylesheet = qtvsc.load_stylesheet(qtvsc.Theme.DARK_VS, custom_colours)
        else:
            stylesheet = qtvsc.load_stylesheet(qtvsc.Theme.LIGHT_VS, custom_colours)
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
    
    :param object: Nothing
    """
    def __init__(self, parent=None):
        super(Gui, self).__init__()
        
        # Variables
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
        self.savedSidebarWords = {}
        self.wordOne = ""
        self.conjWord = ""
        
        # Config variables
        self.showTutorial = True
        self.interfaceLanguage = "English"
        self.currentLanguage = "English"
        self.colourMode = "light"
        self.configColourMode = ""
        self.zoomFactor = 100
        self.htmlContent = ""
        self.htmlContentText = ""
        
        # Style values
        self.topOffset = 40
    
    def setupUI(self, MainWindow):
        """
        Set up the user interface of the main window. This is by deault the "search" layout. The card creator layout is
        by default not initialised. To initialilse it, it must be called by a separate function, which is done on a
        button click.
        
        :param MainWindow: The window object.
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
        
        ## Sidebar
        # Frame
        self.sidebarFrame = QtWidgets.QFrame(self.mainFrame)
        self.sidebarFrame.setMaximumSize(QtCore.QSize(500, 16777215))
        self.sidebarFrame.setFrameShape(QtWidgets.QFrame.Box)
        self.sidebarFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.sidebarFrame.setObjectName("sidebarFrame")
        # Add border
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
        
        ## Top frame
        self.sidebarInnerTopFrame = QtWidgets.QFrame(self.sidebarFrame)
        self.sidebarInnerTopFrame.setMaximumSize(QtCore.QSize(16777215, 160))
        self.sidebarInnerTopFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.sidebarInnerTopFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.sidebarInnerTopFrame.setObjectName("sidebarInnerTopFrame")
        # Remove border
        self.sidebarInnerTopFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        
        # Layout
        self.sidebarTopLayout = QtWidgets.QGridLayout(self.sidebarInnerTopFrame)
        self.sidebarTopLayout.setObjectName("sidebarTopLayout")
        
        # AutoAnki
        self.autoAnkiBtn = QtWidgets.QPushButton(self.sidebarInnerTopFrame)
        self.autoAnkiBtn.setObjectName("autoAnkiBtn")
        self.autoAnkiBtn.clicked.connect(self.__switchToAutoAnki)
        self.sidebarTopLayout.addWidget(self.autoAnkiBtn, 0, 0, 1, 0)
        
        # Search wiki
        self.searchWikBtn = QtWidgets.QPushButton(self.sidebarInnerTopFrame)
        self.searchWikBtn.setObjectName("searchWikBtn")
        self.searchWikBtn.clicked.connect(self.__switchToSearch)
        self.sidebarTopLayout.addWidget(self.searchWikBtn, 1, 0, 1, 0)
        self.line = QtWidgets.QFrame(self.sidebarInnerTopFrame)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.sidebarTopLayout.addWidget(self.line, 2, 0, 1, 1)
        
        # Current lang label
        self.currentLangLabel = QtWidgets.QLabel(self.sidebarInnerTopFrame)
        self.currentLangLabel.setObjectName("currentLangLabel")
        self.sidebarTopLayout.addWidget(self.currentLangLabel, 3, 0, 1, 0)
        
        # Change lang
        self.changeLangBtn = QtWidgets.QPushButton(self.sidebarInnerTopFrame)
        self.changeLangBtn.setObjectName("changeLangBtn")
        self.changeLangBtn.clicked.connect(self.__spawnLanguageDialog)
        self.sidebarTopLayout.addWidget(self.changeLangBtn, 4, 0, 1, 0)
        self.sidebarLayout.addWidget(self.sidebarInnerTopFrame, 0, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.sidebarLayout.addItem(spacerItem, 1, 0, 1, 1)
        self.mainLayout.addWidget(self.sidebarFrame, 0, 0, 2, 1)
        
        # Saved words
        self.sideLabel = QtWidgets.QLabel(self.sidebarInnerTopFrame)
        self.sideLabel.setObjectName("sideLabel")
        self.sidebarTopLayout.addWidget(self.sideLabel, 6, 0, 1, 0)
        self.line2 = QtWidgets.QFrame(self.sidebarInnerTopFrame)
        self.line2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line2.setObjectName("line2")
        self.sidebarTopLayout.addWidget(self.line2, 5, 0, 1, 1)
        # Button
        self.saveWord = QtWidgets.QPushButton(self.sidebarInnerTopFrame)
        self.saveWord.setObjectName("saveWord")
        self.saveWord.clicked.connect(self.saveWordToSide)
        self.sidebarTopLayout.addWidget(self.saveWord, 7, 0, 1, 0)
        
        ## Search layout
        self.searchInputFrame = QtWidgets.QFrame(self.mainFrame)
        self.searchInputFrame.setMinimumSize(QtCore.QSize(700, 0))
        self.searchInputFrame.setMaximumSize(QtCore.QSize(16777215, 150))
        self.searchInputFrame.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.searchInputFrame.setAutoFillBackground(False)
        self.searchInputFrame.setFrameShape(QtWidgets.QFrame.Box)
        self.searchInputFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.searchInputFrame.setObjectName("searchInputFrame")
        # Add border
        self.searchInputLayout = QtWidgets.QGridLayout(self.searchInputFrame)
        self.searchInputLayout.setObjectName("searchInputLayout")
        
        # Sentence radio
        self.sentenceRadio = QtWidgets.QRadioButton(self.searchInputFrame)
        self.sentenceRadio.setObjectName("sentenceRadio")
        self.sentenceRadio.clicked.connect(self.__activateSentenceMode)
        self.searchInputLayout.addWidget(self.sentenceRadio, 0, 0, 1, 1)
        
        # Conjugation radio
        self.conjugationRadio = QtWidgets.QRadioButton(self.searchInputFrame)
        self.conjugationRadio.setObjectName("conjugationRadio")
        self.conjugationRadio.clicked.connect(self.__activateConjugationMode)
        self.searchInputLayout.addWidget(self.conjugationRadio, 1, 0, 1, 1)
        
        # Word radio
        self.wordRadio = QtWidgets.QRadioButton(self.searchInputFrame)
        self.wordRadio.setObjectName("wordRadio")
        self.wordRadio.clicked.connect(self.__activateWordMode)
        self.searchInputLayout.addWidget(self.wordRadio, 2, 0, 1, 1)
        self.wordRadio.setChecked(True)
        
        # Search button
        self.searchBtn = QtWidgets.QPushButton(self.searchInputFrame)
        self.searchInputEdit = MyLineEdit(self.searchBtn, self)
        self.searchInputEdit.setObjectName("searchInputEdit")
        
        # Search input
        self.searchInputLayout.addWidget(self.searchInputEdit, 0, 1, 4, 1)
        self.searchBtn.setObjectName("searchBtn")
        self.searchBtn.clicked.connect(self.__searchWiki)
        self.searchInputLayout.addWidget(self.searchBtn, 3, 0, 1, 1)
        
        # Output display
        self.mainLayout.addWidget(self.searchInputFrame, 0, 1, 1, 1)
        self.outputFrame = QtWidgets.QFrame(self.mainFrame)
        self.outputFrame.setMinimumSize(QtCore.QSize(0, 0))
        self.outputFrame.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.outputFrame.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.outputFrame.setFrameShape(QtWidgets.QFrame.Box)
        self.outputFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.outputFrame.setObjectName("outputFrame")
        self.outputLayout = QtWidgets.QGridLayout(self.outputFrame)
        self.outputLayout.setObjectName("outputLayout")
        
        # Text display
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
        self.mainFrame.setStyleSheet("QFrame {border: 0px; margin: 0px;}")
        self.sidebarFrame.setStyleSheet("QFrame {border: 1px solid lightgrey;}")
        self.sidebarInnerBottomFrame.setStyleSheet("QFrame {border: 0px; margin: 0px;}")
        self.sidebarInnerTopFrame.setStyleSheet("QFrame {border: 0px; margin: 0px;}")
        self.searchInputFrame.setStyleSheet("QFrame {border: 1px solid lightgrey;}")
        self.outputFrame.setStyleSheet("QFrame {border: 1px solid lightgrey;}")
        
        self.__retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.searchBtn, self.sentenceRadio)
        MainWindow.setTabOrder(self.sentenceRadio, self.searchOutputBrowser)
        MainWindow.setTabOrder(self.searchOutputBrowser, self.changeLangBtn)
        MainWindow.setTabOrder(self.changeLangBtn, self.searchWikBtn)
        MainWindow.setTabOrder(self.searchWikBtn, self.autoAnkiBtn)
        MainWindow.setTabOrder(self.autoAnkiBtn, self.settingsBtn)
        MainWindow.setTabOrder(self.settingsBtn, self.colourModeBtn)
        MainWindow.setTabOrder(self.colourModeBtn, self.searchInputEdit)
        
        configVars = config_check()
        self.__applyConfig(configVars)
        
        # Expand sidebar
        self.sidebarFrame.setMaximumSize(QtCore.QSize(160, 16777215))
        self.sidebarInnerTopFrame.setMaximumSize(QtCore.QSize(16777215, 16777215))
        
        if self.colourMode == "dark":
            self.__activateDarkmode()
            self.__updateHtmlView()
        else:
            self.__activateLightmode()
        
        self.verifySaveBtnStatus()
        
        # Load the saved words.
        rawSavedWords = self.__readSavedWordsFile()
        # Parse the saved words.
        savedWordsDict = self.__parseSavedWords(rawSavedWords)
        # Generate buttons
        for count, id_word_pair in enumerate(savedWordsDict.items()):
            self.__genSavedWordsStartup(id_word_pair, count)
    
    def __setupAutoAnkiLayout(self):
        """
        Initialise the card creator layout. This is not a separate window, it is within the main window. It is an
        alternative layout to the "search" layout.
        """
        ## Search layout
        # Top frame and layout
        self.autoAnkiTopFrame = QtWidgets.QFrame(self.mainFrame)
        self.autoAnkiTopFrame.setMinimumSize(QtCore.QSize(700, 0))
        self.autoAnkiTopFrame.setMaximumSize(QtCore.QSize(16777215, 100))
        self.autoAnkiTopFrame.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.autoAnkiTopFrame.setAutoFillBackground(False)
        self.autoAnkiTopFrame.setFrameShape(QtWidgets.QFrame.Box)
        self.autoAnkiTopFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.autoAnkiTopFrame.setObjectName("autoAnkiFrame")
        self.autoAnkiLayout = QtWidgets.QGridLayout(self.autoAnkiTopFrame)
        self.autoAnkiLayout.setObjectName("autoAnkiSetupLayout")
        
        # Make cards button
        self.createCardsBtn = QtWidgets.QPushButton(self.autoAnkiTopFrame)
        self.createCardsBtn.setObjectName("createCardsBtn")
        self.createCardsBtn.clicked.connect(self.__makeCards)
        self.autoAnkiLayout.addWidget(self.createCardsBtn, 0, 0, 1, 1)
        
        # Filepath display
        self.filepathDisp = QtWidgets.QTextBrowser(self.autoAnkiTopFrame)
        self.filepathDisp.setObjectName("filepath")
        self.autoAnkiLayout.addWidget(self.filepathDisp, 0, 1, 2, 1)
        
        # Add file button
        self.addFileBtn = QtWidgets.QPushButton(self.autoAnkiTopFrame)
        self.addFileBtn.setObjectName("addFileBtn")
        self.addFileBtn.clicked.connect(self.__addFile)
        self.autoAnkiLayout.addWidget(self.addFileBtn, 1, 0, 1, 1)
        
        # Output display
        self.mainLayout.addWidget(self.autoAnkiTopFrame, 0, 1, 1, 1)
        self.outputFrameAA = QtWidgets.QFrame(self.mainFrame)
        self.outputFrameAA.setMinimumSize(QtCore.QSize(0, 0))
        self.outputFrameAA.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.outputFrameAA.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.outputFrameAA.setFrameShape(QtWidgets.QFrame.Box)
        self.outputFrameAA.setFrameShadow(QtWidgets.QFrame.Raised)
        self.outputFrameAA.setObjectName("outputFrameAA")
        self.outputLayoutAA = QtWidgets.QGridLayout(self.outputFrameAA)
        self.outputLayoutAA.setObjectName("outputLayoutAA")
        self.AAOutputBrowser = QtWidgets.QTextBrowser(self.outputFrameAA)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)
        sizePolicy.setHeightForWidth(self.AAOutputBrowser.sizePolicy().hasHeightForWidth())
        self.AAOutputBrowser.setSizePolicy(sizePolicy)
        self.AAOutputBrowser.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.AAOutputBrowser.setObjectName("searchOutputBrowser")
        self.outputLayoutAA.addWidget(self.AAOutputBrowser, 0, 0, 1, 1)
        self.mainLayout.addWidget(self.outputFrameAA, 1, 1, 1, 1)
        self.mainWindowLayout.addWidget(self.mainFrame, 0, 0, 1, 1)
        
        # Set borders
        self.autoAnkiTopFrame.setStyleSheet("QFrame {border: 1px solid lightgrey;}")
        self.outputFrameAA.setStyleSheet("QFrame {border: 1px solid lightgrey;}")
        self.AAOutputBrowser.setStyleSheet("QFrame {border: 0px; margin: 0px;}")
        
        QtCore.QMetaObject.connectSlotsByName(self.mainWindow)
        self.__retranslateUiAA(self.mainWindow)
        
        self.AALayoutSet = True
    
    def __retranslateUi(self, MainWindow):
        """Sets the labels for the default main window, called by the UI setup function.
        
        :param MainWindow: The main window GUI object.
        """
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "AutoAnki"))
        # Buttons
        self.saveWord.setText(_translate("MainWindow", "+ Add +"))
        self.colourModeBtn.setText(_translate("MainWindow", "Dark Mode"))
        self.settingsBtn.setText(_translate("MainWindow", "Settings"))
        self.autoAnkiBtn.setText(_translate("MainWindow", "AutoAnki"))
        self.searchWikBtn.setText(_translate("MainWindow", "Search Wiktionary"))
        self.changeLangBtn.setText(_translate("MainWindow", "Change Language"))
        self.searchBtn.setText(_translate("MainWindow", "Search"))
        self.contactBtn.setText(_translate("MainWindow", "Contact"))
        # Radios
        self.sentenceRadio.setText(_translate("MainWindow", "Phrase"))
        self.conjugationRadio.setText(_translate("MainWindow", "Conjugation table"))
        self.wordRadio.setText(_translate("MainWindow", "Search words"))
        # Labels
        self.sideLabel.setText(_translate("MainWindow", "Saved Words"))
        self.sideLabel.setAlignment(Qt.AlignCenter)
        self.updateLangLabel(self.currentLanguage)
        self.currentLangLabel.setAlignment(Qt.AlignCenter)

    def __retranslateUiAA(self, MainWindow):
        """Sets the labels for the card creation UI layout.
        
        :param MainWindow: The main window GUI object.
        """
        _translate = QtCore.QCoreApplication.translate
        self.addFileBtn.setText(_translate("MainWindow", "Add File"))
        self.createCardsBtn.setText(_translate("MainWindow", "Make cards"))
    
    def verifySaveBtnStatus(self):
        """Toggle the save button on/off.
        """
        if self.displayingSavable is True:
            self.saveWord.setEnabled(True)
        else:
            self.saveWord.setEnabled(False)
    
    def __switchToAutoAnki(self):
        """Switch the main window's layout to the card creator layout.
        """
        # Do nothing if the current mode is already AutoAnki.
        if self.currentOverallMode == "autoanki":
            logger.debug("Already in AutoAnki mode.")
            return
        else:
            self.searchInputFrame.hide()
            self.outputFrame.hide()
            if self.AALayoutSet is False:
                self.__setupAutoAnkiLayout()
            else:
                self.autoAnkiTopFrame.show()
                self.outputFrameAA.show()
            self.currentOverallMode = "autoanki"
            self.__reapplyBorderColours()
        self.displayingSavable = False
        self.verifySaveBtnStatus()

    def __switchToSearch(self):
        """Switch the main window's layout to the Wiktionary search layout.
        """
        # Do nothing if the current mode is already search.
        if self.currentOverallMode == "search":
            logger.debug("Already in search mode.")
            return
        else:
            self.autoAnkiTopFrame.hide()
            self.outputFrameAA.hide()
            self.searchInputFrame.show()
            self.outputFrame.show()
            self.currentOverallMode = "search"
        
        self.__reapplyBorderColours()
    
    def __activateConjugationMode(self):
        """Toggle the conjugation mode.
        """
        self.conjugationMode = True
        self.manualSearchMode = "word"
        logger.info("Conj set True")
    
    def __activateWordMode(self):
        """Toggle the conjugation mode.
        """
        self.manualSearchMode = "word"
        self.conjugationMode = False
        logger.info("Using words search.")
    
    def __activateSentenceMode(self):
        self.manualSearchMode = "sentence"
        self.conjugationMode = False
        logger.info("Using sentence search.")
    
    def __activateLightmode(self):
        """Apply the light mode for the GUI.
        """
        stylesheet = qtvsc.load_stylesheet(qtvsc.Theme.LIGHT_VS, custom_colours)
        self.mainWindow.setStyleSheet(stylesheet)
        self.colourMode = "light"
        self.__reapplyBorderColours()
    
    def __activateDarkmode(self):
        """Apply the dark mode for the GUI.
        """
        stylesheet = qtvsc.load_stylesheet(qtvsc.Theme.DARK_VS, custom_colours)
        self.mainWindow.setStyleSheet(stylesheet)
        self.colourMode = "dark"
        self.__reapplyBorderColours()
    
    def __toggleColourMode(self):
        """When the user presses the light/dark mode button, toggle on light mode if dark mode is currently applied and
        vice-versa.
        """
        if self.colourMode == "light":
            self.__activateDarkmode()
        else:
            self.__activateLightmode()
        self.__updateHtmlView()
        # self.updateConfig()
    
    def __reapplyBorderColours(self):
        """When the theme changes, the colour of the border frames resets to something default. These colours need to
        be reapplied whenever the theme changes.
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
    
    def updateConfig(self):
        """Updates the config file with new variables.
        """
        config = configparser.ConfigParser()
        config['LanguagePreferences'] = {'InterfaceLanauge': self.interfaceLanguage, 'SearchLanguage': self.currentLanguage}
        config['Interface'] = {'ColourMode': self.configColourMode, 'ZoomLevel': int(self.zoomFactor * 100)}
        config['Behaviour'] = {'ShowTutorial': self.showTutorial}
        
        with open("config.ini", 'w') as configfile:
            config.write(configfile)
            
        logger.info("New config file generated.")
        
        # Apply config changes
        self.updateLangLabel(self.currentLanguage)
    
    def updateLangLabel(self, lang):
        if lang == "French":
            emoji = "🥖"
        elif lang == "German":
            emoji = "🥨"
        elif lang == "Spanish":
            emoji = "🌮"
        elif lang == "Latin": 
            emoji = "🏺"
        elif lang == "English":
            emoji = "💂"
        self.currentLangLabel.setText(f"Current: {lang} {emoji}")
    
    def __applyConfig(self, configVars):
        """Apply the config variables to the GUI.
        
        :param configVars: A list of config variables.
        """
        ## Save config variables
        # Get interface language
        self.interfaceLanguage = configVars[0]
        # Get search language
        self.currentLanguage = configVars[1]
        # Get colour mode
        self.colourMode = configVars[2]
        self.configColourMode = configVars[2]
        # Get zoom level
        self.zoomFactor = configVars[3]
        # Get tutorial setting
        self.showTutorial = configVars[4]
        
        # Apply config
        self.__applyZoomLvl(self.zoomFactor)
        self.updateLangLabel(self.currentLanguage)
        
    def applySettings(self, newZoomFactor, newColourMode):
        # Zoom factor needs a decimal, but the input here is a float, so divide.
        self.__applyZoomLvl(newZoomFactor)
        # self.__applyColourMode(newColourMode)
        # Update the colour config variable.
        self.configColourMode = newColourMode
        
    def __applyZoomLvl(self, newZoomFactor):
        newZoomFactor = int(newZoomFactor) / 100
        self.zoomFactor = newZoomFactor
        self.searchOutputBrowser.setZoomFactor(newZoomFactor)
    
    def __applyColourMode(self, newColourMode):
        self.colourMode = newColourMode
        
        if self.colourMode == "dark":
            self.__activateDarkmode()
        else:  
            self.__activateLightmode()
        
        self.__updateHtmlView()
    
    def getZoomFactor(self):
        """Get the current zoom factor.
        
        :return: The current zoom factor.
        :rtype: int
        """
        return self.zoomFactor
    
    def changeLanguage(self):
        """Update the Object's language variable.
        """
        newLang = self.langSelect.currentText()
        self.currentLanguage = newLang
        logger.info("Current lang saved as " + newLang)   
        
    def __findKeywords(self, text):
        # The pattern is: any word that is preceeded by an asterisk.
        pattern = r"\*(\w+)"
        keywords = re.findall(pattern, text)
        return keywords
    
    def __callAPI(self, keyword):
        """Call the Wiktionary API and get the definition for a specific word.
        
        :return: The definitions for the word.
        """
        
        return grab_wik(keyword, self.currentLanguage)
    
    def __searchWiki(self):
        """Search Wiktionary for a specific word.
        """
        # Notify user.
        #self.searchOutputBrowser.append("Searching Wiktionary...")
        
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
            # Sentence mode selected. Locate word and isolate.
            keywords = [text]
        
        # Send search term to API caller and update class dictionary.
        defsDictsArray = []
        conjArray = []
        if self.conjugationMode == True:
            # Conjugation table search
            logger.info("Doing conjugation table search.")
            for keyword in keywords:
                self.conjWord = keyword
                conjs = f"<h3>{keyword}</h3>"
                conjs += grab_wik_conjtable(keyword, self.currentLanguage)
                # Remove links
                conjs = strip_bs4_links(conjs)
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
            for count, defsDict in enumerate(defsDictsArray):
                # Only add a line break if there is more than one word.
                if count > 0:
                    definitions += "<hr>"
                if count == 0:
                    self.wordOne = keywords[count]
                definitions += f"<h3>{keywords[count]}</h3>"
                definitionsString = self.__stringifyDefDict(defsDict, count)
                definitions += definitionsString
            # Update class string defs variable.
            self.__updateDefsString(definitions)
            # Print definitions in text output box.
            self.__displayDefinitions()
            self.__updatCurrentDefinitions(defsDictsArray)
            
            self.displayingSavable = True
            self.verifySaveBtnStatus()
    
    def __stringifyDefDict(self, defsDict, count):
        """Takes a definitions dictionary and converts it to HTML.
        
        :param defsDict: A dictionary of definitions pulled from Wiktionary.
        :type defsDict: dict
        :return: A string holding text formatted to be displayed in an HTML environment.
        :rtype: str
        """
        defs_string = ""
        if defsDict:
            for tag, definition in defsDict.items():
                if definition:
                    if self.currentLanguage in GENDERED_LANGS:
                        if tag == "noun":
                            defs_string += f"{tag.capitalize()}"
                            for line_no, string in enumerate(definition):
                                if line_no == 0:
                                    defs_string += f" <i>{string}</i>"
                                elif line_no == 1:
                                    defs_string += "<ol>"
                                    defs_string += f"<li>{string}</li>"
                                else:
                                    defs_string += f"<li>{string}</li>"
                            defs_string += "</ol>"
                            defs_string += "<br>"
                        else:
                            defs_string += f"{tag.capitalize()}"
                            defs_string += "<ol>"
                            for line_no, string in enumerate(definition):
                                defs_string += f"<li>{string}</li>"
                            defs_string += "</ol>"
                            defs_string += "<br>"
                    
                    else:
                        defs_string += f"{tag.capitalize()}"
                        defs_string += "<ol>"
                        for line_no, string in enumerate(definition):
                            defs_string += f"<li>{string}</li>"
                        defs_string += "</ol>"
                        defs_string += "<br>"
        return defs_string
    
    def __updateSearchTerm(self, savedKeywords):
        """Update the keyword variable.
        
        :param savedKeywords: The individual keyword that the user wants to search Wiktionary for.
        """
        self.savedKeywords = savedKeywords
    
    def __updateDefsString(self, defsString):
        """Update the definitions variable.
        
        :param defsString: The definition retrieved (and processed for legibility) from WIktionary.
        """
        self.currentDefsStringified = defsString
    
    def __updatCurrentDefinitions(self, new_definition_dict):
        """Update the definitions variable.
        
        :param new_definition_dict: A new dictionary of definitions.
        """
        self.current_definitions = new_definition_dict
    
    def __displayDefinitions(self):
        """Clear the search output display and update it with the currently saved definitions.
        """
        #self.searchOutputBrowser.clear()
        #self.searchOutputBrowser.append(self.currentDefsStringified)
        self.htmlContentText = self.currentDefsStringified
        self.__updateHtmlView()
    
    def __constructHtml(self, content):
        html = ""
        isTable = False
        
        # Determine if it's a conjugation table.
        if "<table" in content:
            isTable = True
            
        if self.colourMode == "dark":
            if self.conjugationMode or isTable == True:
                html = html_header_dark_conj + content + html_footer
            else:
                html = html_header_dark + content + html_footer
        else:
            html = html_header_light + content + html_footer
        self.htmlContent = html
        return html
        
    def __updateHtmlView(self):
        self.__constructHtml(self.htmlContentText)
        self.searchOutputBrowser.setHtml(self.htmlContent)
        #print(self.htmlContent)
    
    def __makeCards(self):
        """Begins the process of creating anki cards from the provided file.
        """
        print("Making cards...")
        # self.AAOutputBrowser.setHtml(f"Generating cards, please wait. Do not close the program, this may take some time depending on the amount of cards being generated.")
        make_cards(self.currentInputFilePath, self.currentLanguage)
    
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
    
    def __addFile(self):
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
        
        self.__updatePathDisplay()
    
    def testFile(self):
        """Simply prints the file that has been selected. For development testing purposes.
        """
        # print(self.selectedFileContent)
    
    def __updatePathDisplay(self):
        """Updates the text display to show the user the file path they have selected.
        """
        self.filepathDisp.append(self.currentInputFilePath)
        
    def getCurrentLang(self):
        """Get the current language.
        
        :return: The currently selected search language.
        :rtype: str
        """
        return self.currentLanguage
    
    def updateLanguageVar(self, newLang):
        self.currentLanguage = newLang
        self.updateConfig()
        return
    
    def getColourMode(self):
        return self.colourMode
    
    def saveWordToSide(self):
        """Saves a word to the sidebar.
        """
        if self.conjugationMode:
            logger.info("Saving conjugation table")
            
            unique_id = str(uuid.uuid1(node=None, clock_seq=None))
            self.savedSidebarWords[unique_id] = self.htmlContentText
            
            word = self.conjWord
            
            # Create a new button for the sidebar.
            newWordBtn = QtWidgets.QPushButton(self.sidebarInnerTopFrame)
            number = len(self.savedSidebarWords)
            newWordBtn.setObjectName(f"sideButton{unique_id}")
            self.sidebarTopLayout.addWidget(newWordBtn, 7+number, 0, 1, 1)
            newWordBtn.setText(f"{word} 📜")
            newWordBtn.clicked.connect(lambda: self.loadSavedWord(self.savedSidebarWords[unique_id]))
            
            # Create remove button
            newWordBtnRmv = QtWidgets.QPushButton(self.sidebarInnerTopFrame)
            newWordBtnRmv.setObjectName(f"sideButtonRmv{unique_id}")
            self.sidebarTopLayout.addWidget(newWordBtnRmv, 7+number, 1, 1, 1)
            newWordBtnRmv.setText("-")
            newWordBtnRmv.clicked.connect(lambda: self.__removeSavedWord(unique_id))
            
            # Save word content to file (just the HTML content, not the formatted HTML string used for display)
            self.saveWordToFile(self.htmlContentText)
            
        else:
            # Save the word to class variable.
            unique_id = str(uuid.uuid1(node=None, clock_seq=None))
            self.savedSidebarWords[unique_id] = self.htmlContentText
            
            # Get the word itself.
            word = self.wordOne
            
            # Create a new button for the sidebar.
            newWordBtn = QtWidgets.QPushButton(self.sidebarInnerTopFrame)
            number = len(self.savedSidebarWords)
            newWordBtn.setObjectName(f"sideButton{unique_id}")
            self.sidebarTopLayout.addWidget(newWordBtn, 7+number, 0, 1, 1)
            newWordBtn.setText(f"{word} 🔖")
            newWordBtn.clicked.connect(lambda: self.loadSavedWord(self.savedSidebarWords[unique_id]))
            
            # Create remove button
            newWordBtnRmv = QtWidgets.QPushButton(self.sidebarInnerTopFrame)
            newWordBtnRmv.setObjectName(f"sideButtonRmv{unique_id}")
            self.sidebarTopLayout.addWidget(newWordBtnRmv, 7+number, 1, 1, 1)
            newWordBtnRmv.setText("-")
            newWordBtnRmv.clicked.connect(lambda: self.__removeSavedWord(unique_id))
            
            # Save word content to file (just the HTML content, not the formatted HTML string used for display)
            self.saveWordToFile(self.htmlContentText)
    
    def __genSavedWordsStartup(self, id_word_pair, count):
        """Generate the saved words buttons on startup.
        """        
        # Create a new button for the sidebar.
        newWordBtn = QtWidgets.QPushButton(self.sidebarInnerTopFrame)
        newWordBtn.setObjectName(f"sideButton{id_word_pair[0]}")
        self.sidebarTopLayout.addWidget(newWordBtn, 8+count, 0, 1, 1)
        
        # Create remove button
        newWordBtnRmv = QtWidgets.QPushButton(self.sidebarInnerTopFrame)
        newWordBtnRmv.setObjectName(f"sideButtonRmv{id_word_pair[0]}")
        self.sidebarTopLayout.addWidget(newWordBtnRmv, 8+count, 1, 1, 1)
        newWordBtnRmv.setText("-")
        newWordBtnRmv.setMaximumSize(QtCore.QSize(25, 16777215))
        newWordBtnRmv.clicked.connect(lambda: self.__removeSavedWord(id_word_pair[0]))
        
        # Regex expression that finds the first header in the string and extracts the word.
        match = re.search(r"<h3>(\w+)</h3>", id_word_pair[1])
        print(id_word_pair)
        word = match.group(1)
        newWordBtn.setText(f"{word} 🔖")
        
        # Determine if it's a conjugation table.
        if "<table" in id_word_pair[1]:
            newWordBtn.setText(f"{word} 📜") 
        
        # Align text on buttons to the left.
        # newWordBtn.setStyleSheet("QPushButton { text-align: left; }")
        
        # Dynamically connect button to function.
        newWordBtn.clicked.connect(lambda: self.loadSavedWord(self.savedSidebarWords[id_word_pair[0]]))
    
    def __removeSavedWord(self, unique_id):
        """Remove a saved word from the sidebar.
        """
        # Remove the button.
        word_btn = self.sidebarInnerTopFrame.findChild(QtWidgets.QPushButton, f"sideButton{unique_id}")
        remove_btn = self.sidebarInnerTopFrame.findChild(QtWidgets.QPushButton, f"sideButtonRmv{unique_id}")
        self.sidebarTopLayout.removeWidget(word_btn)
        self.sidebarTopLayout.removeWidget(remove_btn)

        # Remove the word from the dict.
        print(f"Deleting saved word at key {unique_id}")
        self.savedSidebarWords.pop(unique_id)
        # Update the saved words file.
        self.__updateSavedWordsFile()
    
    def __updateSavedWordsFile(self):
        """Update the saved words file with the new list of saved words.
        """
        # Open file
        with open("saved_words.txt", "w", encoding="utf-8") as f:
            for content in self.savedSidebarWords.values():
                f.write(content)
                f.write("\n====================================\n")
            f.close()
    
    def loadSavedWord(self, content):
        """Load a saved word from the sidebar.
        """
        self.__constructHtml(content)
        self.searchOutputBrowser.setHtml(self.htmlContent)
    
    def saveWordToFile(self, content):
        """Save (append) a word to the saved words file.
        """
        # Open file
        with open("saved_words.txt", "a", encoding="utf-8") as f:
            f.write(content)
            f.write("\n====================================\n")
            f.close()
    
    def __readSavedWordsFile(self):
        """Read the saved words file and return the contents.
        
        :return: A string containing the contents of the saved words file, with each set of definitions relating to a
        single word separated by a line of equals signs.
        :rtype: str
        """
        with open("saved_words.txt", "r", encoding="utf-8") as f:
            content = f.read()
            f.close()
        return content
    
    def __parseSavedWords(self, content):
        """Parse the saved words file and return a list of words.
        
        :param content: String containing HTML content for words separated by a line of equals signs.
        :type content: str
        :return: Dictionary of word HTML content.
        :rtype: dict
        """
        content = content.split("\n====================================\n")
        # Remove the last entry (it is empty).
        content.pop()
        # Save the retrieved words to the class variable.
        for item in content:
            unique_id = str(uuid.uuid1(node=None, clock_seq=None))
            self.savedSidebarWords[unique_id] = item
        
        return self.savedSidebarWords


class GuiContactDialog(object):
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
    """The change language dialog. Allows the user to change languages from a list of 'verified' languages, and the 
    option to add a language of their own choosing.
    """
    def __init__(self, parent):
        self.parent = parent
        self.tempLang = ""
        self.window = ""
    
    def setupUi(self, changeLangWindow):
        """Initialise the GUI.
        
        :param changeLangWindow: The dialog object.
        """
        self.window = changeLangWindow
        changeLangWindow.setObjectName("changeLangWindow")
        changeLangWindow.resize(420, 350)
        self.gridLayout_4 = QtWidgets.QGridLayout(changeLangWindow)
        self.gridLayout_4.setObjectName("gridLayout_4")
        
        # Change lang W frame
        self.changeLangWFrame = QtWidgets.QFrame(changeLangWindow)
        self.changeLangWFrame.setMaximumSize(QtCore.QSize(560, 330))
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
        
        # Right frame
        self.bodyRightFrame = QtWidgets.QFrame(self.changeLangWFrame)
        self.bodyRightFrame.setMaximumSize(QtCore.QSize(271, 16777215))
        self.bodyRightFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.bodyRightFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.bodyRightFrame.setObjectName("bodyRightFrame")
        # Add parent border
        self.bodyRightFrame.setStyleSheet("QFrame {border: 1px solid lightgrey;}")
        
        # Grid 2
        self.gridLayout_2 = QtWidgets.QGridLayout(self.bodyRightFrame)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setSpacing(0)
        # Separator line
        self.changeLangLine = QtWidgets.QFrame(self.bodyRightFrame)
        self.changeLangLine.setFrameShape(QtWidgets.QFrame.HLine)
        self.changeLangLine.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.changeLangLine.setObjectName("changeLangLine")
        # Remove border
        self.changeLangLine.setStyleSheet("border: 0px;")
        self.gridLayout_2.addWidget(self.changeLangLine, 2, 0, 1, 1)
        # Top right frame
        self.CLTopFrameR = QtWidgets.QFrame(self.bodyRightFrame)
        self.CLTopFrameR.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.CLTopFrameR.setFrameShadow(QtWidgets.QFrame.Raised)
        self.CLTopFrameR.setObjectName("CLTopFrameR")
        # Remove border for everything above apply button
        self.CLTopFrameR.setStyleSheet("QFrame#changeLangWFrame { border: 0px solid black; }")
        self.CLTopFrameR.setStyleSheet("QFrame {border: 0px; margin: 0px;}")
        self.gridLayout = QtWidgets.QGridLayout(self.CLTopFrameR)
        self.gridLayout.setObjectName("gridLayout")
        
        # Add lang frame
        self.addLangFrame = QtWidgets.QFrame(self.CLTopFrameR)
        self.addLangFrame.setMinimumSize(QtCore.QSize(146, 0))
        self.addLangFrame.setMaximumSize(QtCore.QSize(16777215, 75))
        self.addLangFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.addLangFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.addLangFrame.setObjectName("addLangFrame")
        # Remove border from frame
        self.addLangFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.addLangFrame.setLineWidth(0)
        self.addLangFrame.setStyleSheet("QFrame#changeLangWFrame { border: 0px solid black; }")
        self.addLangFrame.setStyleSheet("QFrame {border: 0px; margin: 0px;}")
        
        # Vertical layout
        self.verticalLayout = QtWidgets.QVBoxLayout(self.addLangFrame)
        self.verticalLayout.setContentsMargins(0, -1, -1, -1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        
        # New lang input
        self.newLangInput = QtWidgets.QLineEdit(self.addLangFrame)
        self.newLangInput.setMinimumSize(QtCore.QSize(0, 22))
        self.newLangInput.setInputMask("")
        self.newLangInput.setText("")
        self.newLangInput.setEchoMode(QtWidgets.QLineEdit.Normal)
        self.newLangInput.setObjectName("newLangInput")
        self.newLangInput.setStyleSheet("border: 1px; border-style: solid;")
        self.newLangInput.setEnabled(False)
        self.verticalLayout.addWidget(self.newLangInput)
        
        # Add lang button
        self.addNewLangBtn = QtWidgets.QPushButton(self.addLangFrame)
        self.addNewLangBtn.setMinimumSize(QtCore.QSize(0, 0))
        self.addNewLangBtn.setMaximumSize(QtCore.QSize(70, 20))
        self.addNewLangBtn.setObjectName("addNewLangBtn")
        self.verticalLayout.addWidget(self.addNewLangBtn)
        self.addNewLangBtn.setEnabled(False)
        self.gridLayout.addWidget(self.addLangFrame, 1, 0, 1, 1)
        
        # Explanation label
        self.langsLabel = QtWidgets.QLabel(self.CLTopFrameR)
        self.langsLabel.setMaximumSize(QtCore.QSize(263, 75))
        self.langsLabel.setTextFormat(QtCore.Qt.AutoText)
        self.langsLabel.setScaledContents(False)
        self.langsLabel.setWordWrap(True)
        self.langsLabel.setObjectName("langsLabel")
        self.gridLayout.addWidget(self.langsLabel, 0, 0, 1, 1)
        
        self.gridLayout_2.addWidget(self.CLTopFrameR, 1, 0, 1, 1)
        self.changeLangConf = QtWidgets.QDialogButtonBox(self.bodyRightFrame)
        self.changeLangConf.setOrientation(QtCore.Qt.Horizontal)
        self.changeLangConf.setStandardButtons(QtWidgets.QDialogButtonBox.Apply)
        self.changeLangConf.clicked.connect(self.__handleApply)
        self.changeLangConf.setCenterButtons(True)
        self.changeLangConf.setObjectName("changeLangConf")
        self.gridLayout_2.addWidget(self.changeLangConf, 3, 0, 1, 1)
        self.gridLayout_3.addWidget(self.bodyRightFrame, 0, 1, 1, 1)
        self.gridLayout_2.setContentsMargins(20, 20, 20, 20)
        
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
        self.langsList.setStyleSheet("QFrame {border: 1px solid lightgrey;}")
        self.gridLayout_3.addWidget(self.langsList, 0, 0, 1, 1)
        self.gridLayout_4.addWidget(self.changeLangWFrame, 0, 0, 1, 1)
        
        self.__retranslateUi(changeLangWindow)
        QtCore.QMetaObject.connectSlotsByName(changeLangWindow)
    
    def __handleApply(self):
        """Applies the selected language by updating the GUI language variable and then closes the dialog.
        """
        if self.tempLang:
            self.parent.updateLanguageVar(self.tempLang)
        self.window.close()
    
    def __retranslateUi(self, changeLangWindow):
        """Initialises the labels for GUI elements.
        
        :param changeLangWindow: The dialog object.
        """
        _translate = QtCore.QCoreApplication.translate
        changeLangWindow.setWindowTitle(_translate("changeLangWindow", "Language Settings"))
        self.newLangInput.setPlaceholderText(_translate("changeLangWindow", "Language name"))
        self.addNewLangBtn.setText(_translate("changeLangWindow", "Add"))
        self.langsLabel.setText(_translate("changeLangWindow", "Use the list to the left to select your search language. Custom language functionality not implemented yet but will be soon."))
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
    
    def __highlightCurrentLang(self, item):
        """Highlight the currently selected language on the selection list. Used at dialog start-up.
        
        :param item: The item within the list representing the currently selected language.
        """
        self.langsList.setCurrentItem(item)
        self.langsList.setFocus()
    
    def __updateTempLangVar(self, lang):
        """Updates the language var used to save, temporarily, when a user clicks on a language list object, but is yet 
        to save that as their selection.
        
        :param lang: The selected language.
        """
        self.tempLang = lang
    
    def __getCurrentLangSelection(self):
        """Get the currently selected language from the list of languages GUI element.
        
        :return: The currently selected list item.
        """
        selection = self.langsList.currentRow()
        selection += 1
        selection = langs[str(selection)]
        # print(selection)
        return selection
    
    def __updateSelection(self):
        """Update the program with the currently selected (temporary, not yet applied) language selection from the list.
        """
        selection = self.__getCurrentLangSelection()
        self.__updateTempLangVar(selection)
    
    def __indexLang(self):
        """Determine which list element a language corresponds with.
        
        :return: An integer corresponding with a list item representing a language.
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
        """Initialise the settings dialog GUI.
        """
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
        
        # Interface language
        self.settingsLangLbl = QtWidgets.QLabel(self.settingsFrame)
        self.settingsLangLbl.setObjectName("settingsLangLbl")
        self.gridLayout.addWidget(self.settingsLangLbl, 0, 0, 1, 1)
        self.interfaceLangCB = QtWidgets.QComboBox(self.settingsFrame)
        self.interfaceLangCB.setMaximumSize(QtCore.QSize(130, 16777215))
        self.interfaceLangCB.setObjectName("interfaceLangCB")
        self.interfaceLangCB.addItem("")
        self.gridLayout.addWidget(self.interfaceLangCB, 0, 1, 1, 1)
        
        # Colour mode
        self.settingsColMdLbl = QtWidgets.QLabel(self.settingsFrame)
        self.settingsColMdLbl.setObjectName("settingsColMdLbl")
        self.gridLayout.addWidget(self.settingsColMdLbl, 1, 0, 1, 1)
        self.defaultColourModeCB = QtWidgets.QComboBox(self.settingsFrame)
        self.defaultColourModeCB.setMaximumSize(QtCore.QSize(130, 16777215))
        self.defaultColourModeCB.setObjectName("defaultColourModeCB")
        self.defaultColourModeCB.addItem("")
        self.defaultColourModeCB.addItem("")
        self.gridLayout.addWidget(self.defaultColourModeCB, 1, 1, 1, 1)
        
        # Font size
        self.fontSizeSelectLbl = QtWidgets.QLabel(self.settingsFrame)
        self.fontSizeSelectLbl.setObjectName("fontSizeSelectLbl")
        self.gridLayout.addWidget(self.fontSizeSelectLbl, 2, 0, 1, 1)
        self.fontSizeSelect = QtWidgets.QSpinBox(self.settingsFrame)
        self.fontSizeSelect.setMinimum(25)
        self.fontSizeSelect.setMaximum(500)
        self.fontSizeSelect.setMaximumSize(QtCore.QSize(130, 16777215))
        self.fontSizeSelect.setObjectName("fontSizeSelect")
        
        # Handle zoom factor
        zoomFactor = self.parent.getZoomFactor()
        zoomFactor = self.convertZoomLevel(zoomFactor)
        self.fontSizeSelect.setValue(zoomFactor)
        self.gridLayout.addWidget(self.fontSizeSelect, 2, 1, 1, 1)
        
        # Tutorial settings
        self.tutorialLbl = QtWidgets.QLabel(self.settingsFrame)
        self.tutorialLbl.setObjectName("tutorialLbl")
        self.gridLayout.addWidget(self.tutorialLbl, 3, 0, 1, 1)
        self.tutorialRadio = QtWidgets.QRadioButton(self.settingsFrame)
        self.gridLayout.addWidget(self.tutorialRadio, 3, 1, 1, 1)
        
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
            stylesheet = qtvsc.load_stylesheet(qtvsc.Theme.DARK_VS, custom_colours)
        else:
            stylesheet = qtvsc.load_stylesheet(qtvsc.Theme.LIGHT_VS, custom_colours)
        self.window.setStyleSheet(stylesheet)    
    
    def retranslateUi(self, settingsDialog):
        """Apply labels to the GUI elements.
        """
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
        self.checkTutorialSetting()
        
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
        
        self.__applyTutorialSetting()
        self.parent.applySettings(newZoomFactor, newColourSelect)
        self.parent.updateConfig()
        self.window.close()
    
    def checkTutorialSetting(self):
        """Check the tutorial setting.
        """
        if self.parent.showTutorial == "True":
            self.tutorialRadio.setChecked(True)
        else:
            self.tutorialRadio.setChecked(False)
    
    def __applyTutorialSetting(self):
        """Apply the tutorial setting.
        """
        if self.tutorialRadio.isChecked():
            self.parent.showTutorial = "True"
        else:
            self.parent.showTutorial = "False"


def config_check():
    if os.path.exists("config.ini"):
        logger.info("Config file found.")
    else:
        logger.info("No config file found. Creating a new one.")
        setup_config()
    config_vars = get_configs()
    return config_vars


def setup_config():
    config = configparser.ConfigParser()
    config['LanguagePreferences'] = {'InterfaceLanauge': 'English', 'SearchLanguage': 'English'}
    config['Interface'] = {'ColourMode': 'light', 'ZoomLevel': 100}
    config['Behaviour'] = {'ShowTutorial': True}
    
    with open("config.ini", 'w') as configfile:
        config.write(configfile)
    
    logger.info("New config file generated.")


def get_configs():
    """Gets the config variables from the config file.
    
    :return: A list of config variables.
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
    
    # Put them into a list
    config_vars = [interface_language, search_language, colour_mode, zoom_level, show_tutorial]
    
    return config_vars  


def get_user_word(lang_selection):
    if langs[lang_selection] == "Deutsch":
        print(f"Geben Sie ein Wort ein: ")
    elif langs[lang_selection] == "English":
        print(f"Enter a word, or type the letter 'c' to change languages: ")
    elif langs[lang_selection] == "French":
        print(f"Enter a word: ")
        
    word_input = input()
    print("-----------")
    return word_input


def find_keywords(dict_array):
    """
    Finds keywords in the text submitted by the user.
    Keywords are designated by adding an * before the keyword.
    
    :param dict_array: An array of dictionaries. Each one respresenting information to be used for an Anki card.
    :returns: dict_array (dict): An updated version of the dictionaries. The keywords designated by the user have not 
    been added to each dictionary's 'words' entry.
    """
    # The pattern is: any word that is preceeded by an asterisk.
    pattern = r"\*(\w+)"
    for dictionary in dict_array:
        text = dictionary.get("text")
        words = re.findall(pattern, text)
        dictionary["words"] = words
    return dict_array


def get_tags(dict_array, language, nlp):
    """
    Gets the grammatical tags for the user's marked words.
    
    :param dict_array: The array of dictionaries being used to create Anki cards. Each dictionary represents a card.
    :returns dict_array: The array of dictionaries, now with added tag entries.
    """
    for count, dictionary in enumerate(dict_array):
        words_and_nltk_tags = determine_grammar(dictionary["words"], dictionary["text"], language, nlp)
        dict_array[count]["tags"] = words_and_nltk_tags
    return dict_array


def determine_grammar(words: list, text, lang, nlp):
    """
    Determines the grammatical context of the specified words in the context of a piece of text using nltk natural 
    language processing.
    
    :param words: A list of words passed to the function from an card dictionary.
    :param text: The text that the word is found in. Passed from an card dictionary.
    :returns nltk_tags: Tags used by nltk to signify the grammatical use of the word. Stored as an array. Each item in 
    that array is itself a single array that holds a tuple containing a word and its nltk tag. The additional array is 
    redundant - I don't know how to remove it.
    """
    nltk_tags = spacy_to_nltk(words, text, lang, nlp)
    
    # else:
    #     nltk_tags = []
        
    #     # Tokenizing the text. Specifying 'german' here doesn't change the model but may adjust tokenization behavior.
    #     tokens = nltk.word_tokenize(text, language=lang)
        
    #     # POS tagging the tokenized text. Note: This still uses the English model, as there's no German model in NLTK.
    #     tagged_text = nltk.pos_tag(tokens)
        
    #     for word in words:
    #         # Finding and appending the tagged words
    #         result = [tag for tag in tagged_text if tag[0].lower() == word.lower()]
    #         nltk_tags.append(result)
    #         logger.info(f"Determine grammar function: tagged {word} as {result}")
    
    return nltk_tags



def strip_punctuation(text):
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


def spacy_to_nltk(words: list, text, lang, nlp):
    """Because nltk doesn't have a German model, we have to use SpaCy to tag the words, then convert the SpaCy tags to
    NLTK tags.
    
    :param text: _description_
    :type text: _type_
    :param lang: _description_, defaults to 'de'
    :type lang: str, optional
    :return: _description_
    :rtype: _type_
    """
    nltk_tags = []
    
    # Remove punctuation
    text = strip_punctuation(text)
    
    # Process the text using SpaCy
    doc = nlp(text)
    # Convert each token to NLTK tag if the token text is in the words list
    for token in doc:
        print(f">> Comparing {token.text} to {words}")
        if token.text in (word for word in words):
            # Find the equivalent NLTK tag for the SpaCy tag from the mapping
            nltk_tag = SPACY_TO_NLTK_TAG_MAP.get(token.pos_, 'NN')  # Default to 'NN' if not found
            
            # Because spacy seems to be identifying German nouns as proper nouns (due to capitalisation),
            # all NNPs need to be converted to NNs, despite this being inaccurate.
            if nltk_tag == 'NNP':
                nltk_tag = 'NN'
            
            nltk_tags.append([token.text, nltk_tag])
            logger.info(f"Tagged {token.text} as {nltk_tag}")
    
    return nltk_tags


def match_tags(dict_array):
    """
    Match the nltk grammar tags with more general (and comprehensible) tags, as set out in the global nltk_tag_ref
    dictionary. Not only does this make things more understandbale, but it makes it easier to match our grammar tags 
    with Wiktionary's grammat tags.
    
    :param dict_array: Array of dictionaries, each dictionary representing an Anki card.
    :returns dict_array: The dictionaries array with its tags edited to be simplified and readable.
    """
    for dict_index, dictionary in enumerate(dict_array):
        for tags_index, tags in enumerate(dictionary["tags"]):
            for tag_index, tag in enumerate(tags):
                # tag = tag[1]
                logger.info(f"Match tags function: tag < {tag} > found in dictionary tags array.")
                for readable_tag, nltk_tags in nltk_tag_ref.items():
                    for nltk_tag in nltk_tags:
                        if nltk_tag == tag:
                            new_tag = readable_tag
                            this_word = dict_array[dict_index]["tags"][tags_index][tag_index][0]
                            dict_array[dict_index]["tags"][tags_index] = [this_word, new_tag]
                            logger.info(f"Changed < {tag} > to > {new_tag} <")	
    return dict_array


def grab_wik(text, language):
    """Grab the Wiktionary definitions for a single word.
    
    :param text: The text provided by the user in the GUI input field.
    :type text: string
    :param language: The currently selected language stored the the GUI variables.
    :type language: string
    :return: The word's definitions.
    :rtype: string
    """
    page_content = get_wiktionary_definition(text)
    print(page_content)
    if page_content:
        parsed_definitions_dict = parse_page(page_content, language)
        if parsed_definitions_dict:
            cleaned_definitions = clean_wikitext(parsed_definitions_dict)
            return cleaned_definitions
        else:
            logger.warning(f"Failed to parse page for < {text} >.")
            return False
    else:
        logger.warning(f"Failed to get definition for < {text} >.")
        return False


def get_wiktionary_url(word):
    base_url = "https://en.wiktionary.org/wiki/"
    # Construct the URL by appending the word to the base URL
    url = f"{base_url}{word}"
    return url


def grab_wik_conjtable(text, language):
    """Grab the Wiktionary conjugation table for a single word.
    
    :param text: The text provided by the user in the GUI input field.
    :type text: string
    :param language: The currently selected language stored the the GUI variables.
    :type language: string
    :return: The word's conjugation table.
    :rtype: html string
    """
    logger.info(f"Getting conjugation table for {text}")
    
    # Get the URL
    wik_url = get_wiktionary_url(text)
    
    # Send a request to the URL
    response = requests.get(wik_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the English language section
    english_section = soup.find('span', {"class": "mw-headline", "id": f"{language}"})
    
    # Proceed only if the English section is found
    if english_section:
        # Navigate to the parent of the span, which should be h2, then to subsequent content
        content = english_section.parent
        
        # Now find the conjugation header within the English section
        conjugation_header = content.find_next('span', id='Conjugation')
        if not conjugation_header:
            conjugation_header = content.find_next('span', id='Conjugation_2')
        if not conjugation_header:
            conjugation_header = content.find_next('span', id='Conjugation_3')
        if not conjugation_header:
            conjugation_header = content.find_next('span', id='Conjugation_4')
        
        if conjugation_header:
            # Find the next table following the conjugation header
            table = conjugation_header.find_next('table')
            if table:
                return str(table)
            else:
                return "Could not find conjugation table."
        else:
            return "Could not find conjugation header"
    else:
        return "English section not found."


def strip_bs4_links(html_content):
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all <a> tags and replace them with their text content
    for link in soup.find_all('a'):
        link.replace_with(link.text)
        
    # Return the modified HTML
    return str(soup)


def get_wiktionary_conjugations(word):
    # Endpoint for the MediaWiki API
    endpoint = "https://en.wiktionary.org/w/api.php"
    
    # Parameters for fetching the content of a page
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
    """
    Get the definition of a word from wiktionary.
    
    :param word: The individual word being defined.
    :returns content: The entire wiktionary page containing the definition of the word.
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


def parse_page(page_content, language):
    """
    Process the page so that it can be worked on.
    
    :param page_content: The raw page content for an individual word. This is an entire wiktionary page, containing 
    definitions for multiple languages.
    :param language: The language being used. This is necessary because the page_content will probably contain multiple 
    languages.
    :returns definitions: A dictionary of definitions. Each entry contains the definitions for the word's different 
    grammatical uses.
    """
    # English Wiktionary pages should display the language in this format.
    
    r_lang = "==" + language + "=="
    #lang_section = re.search(rf'{r_lang}\n(.*?)(?=\n==[^=])', page_content, re.DOTALL)
    try:
        lang_section = re.search(rf'{r_lang}\n(.*?)(?=\n==[^=]|$)', page_content, re.DOTALL)
    except:
        logger.warning(f"No relevant << {language} >> definitions found in >>\n{page_content}\n<<")
        return False
    
    # If the specificed language is found on the page, get the definitions.
    if lang_section:
        lang_content = lang_section.group(1)
        print(lang_content)
        
        # Definitions will be split up by their grammatical type. We need to find each type. They also might be 
        # formatted differently, so we need to search for different formats.
        noun_section = re.findall(r'===Noun===\n(.*?)(\n==|\n===|$|$)', lang_content, re.DOTALL)
        if not noun_section:
            noun_section = re.findall(r'====Noun====\n(.*?)(\n==|\n===|$)', lang_content, re.DOTALL)
        verb_section = re.findall(r'===Verb===\n(.*?)(\n==|\n===|$)', lang_content, re.DOTALL)
        if not verb_section:
            verb_section = re.findall(r'====Verb====\n(.*?)(\n==|\n===|$)', lang_content, re.DOTALL)
        adj_section = re.findall(r'===Adjective===\n(.*?)(\n==|\n===|$)', lang_content, re.DOTALL)
        if not adj_section:
            adj_section = re.findall(r'====Adjective====\n(.*?)(\n==|\n===|$)', lang_content, re.DOTALL)
        adv_section = re.findall(r'===Adverb===\n(.*?)(\n==|\n===|$)', lang_content, re.DOTALL)
        if not adv_section:
            adv_section = re.findall(r'====Adverb====\n(.*?)(\n==|\n===|$)', lang_content, re.DOTALL)
        prep_section = re.findall(r'===Preposition===\n(.*?)(\n==|\n===|$)', lang_content, re.DOTALL)
        if not prep_section:
            prep_section = re.findall(r'====Preposition====\n(.*?)(\n==|\n===|$)', lang_content, re.DOTALL)
        pron_section = re.findall(r'===Pronoun===\n(.*?)(\n==|\n===|$)', lang_content, re.DOTALL)
        if not pron_section:
            pron_section = re.findall(r'====Pronoun====\n(.*?)(\n==|\n===|$)', lang_content, re.DOTALL)
        particle_section = re.findall(r'===Particle===\n(.*?)(\n==|\n===|$)', lang_content, re.DOTALL)
        if not particle_section:
            particle_section = re.findall(r'====Particle====\n(.*?)(\n==|\n===|$)', lang_content, re.DOTALL)
        conjunciton_section = re.findall(r'===Conjunction===\n(.*?)(\n==|\n===|$)', lang_content, re.DOTALL)
        if not conjunciton_section:
            conjunciton_section = re.findall(r'====Conjunction====\n(.*?)(\n==|\n===|$)', lang_content, re.DOTALL)
        article_section = re.findall(r'===Article===\n(.*?)(\n==|\n===|$)', lang_content, re.DOTALL)
        if not article_section:
            article_section = re.findall(r'====Article====\n(.*?)(\n==|\n===|$)', lang_content, re.DOTALL)
        numeral_section = re.findall(r'===Numeral===\n(.*?)(\n==|\n===|$)', lang_content, re.DOTALL)
        if not numeral_section:
            numeral_section = re.findall(r'====Numeral====\n(.*?)(\n==|\n===|$)', lang_content, re.DOTALL)
        interjection_section = re.findall(r'===Interjection===\n(.*?)(\n==|\n===|$)', lang_content, re.DOTALL)
        if not interjection_section:
            interjection_section = re.findall(r'====Interjection====\n(.*?)(\n==|\n===|$)', lang_content, re.DOTALL)
        exclamation_section = re.findall(r'===Exclamation===\n(.*?)(\n==|\n===|$)', lang_content, re.DOTALL)
        if not exclamation_section:
            exclamation_section = re.findall(r'====Exclamation====\n(.*?)(\n==|\n===|$)', lang_content, re.DOTALL)
        determiner_section = re.findall(r'===Determiner===\n(.*?)(\n==|\n===|$)', lang_content, re.DOTALL)
        if not determiner_section:
            determiner_section = re.findall(r'====Determiner====\n(.*?)(\n==|\n===|$)', lang_content, re.DOTALL)
        
        definitions = {
            "noun": noun_section,
            "verb": verb_section,
            "adjective": adj_section,
            "adverb": adv_section,
            "pronoun": pron_section,
            "preposition": prep_section,
            "particle": particle_section,
            "conjunction": conjunciton_section,
            "article": article_section,
            "numeral": numeral_section,
            "interjection": interjection_section,
            "exclamation": exclamation_section,
            "determiner": determiner_section
        }
            
        for part_of_speech, section in definitions.items():
            if section:
                definition = []
                if language == "German" and part_of_speech == "noun":
                    definition += re.findall(r"de-noun\|(.)", section[0][0])
                    definition += re.findall(r"de\|noun form\|g=(.)", section[0][0])
                elif language == "French" and part_of_speech == "noun":
                    definition += re.findall(r"fr-noun\|(.)", section[0][0])
                elif language == "Latin" and part_of_speech == "noun":
                    gender = re.findall(r"la-noun\|[^<]*<.{2}", section[0][0])
                    gender = [match[-3:] for match in gender]
                    # Strip the < > characters from gender var.
                    try:
                        gender[0] = gender[0].replace("<", "")
                        gender[0] = gender[0].replace(">", "")
                        gender[0] = f"declension {gender[0]}"
                        definition += gender
                    except:
                        pass
                elif language == "Spanish" and part_of_speech == "noun":
                    definition += re.findall(r"es-noun\|(.)", section[0][0])
                definition += re.findall(r'# (.*?)(?:\n|$)', section[0][0])
                definitions[part_of_speech] = definition
            
        if any(definitions.values()):
            return definitions
        else:
            logger.warning(f"No definitions found in >>\n{page_content}\n If you see definitions here, that means there is either a problem with the code, or the part of speech is not being considered by the program. If you think this is an oversight and that this particular part of speech should be added, please contact me via the contact form, or if you'd like to fix it yourself, submit a pull request on GitHub.")
            return False
        
    else:
        logger.warning(f"No definitions found in >>\n{page_content}\n If you see definitions here, that means there is either a problem with the code, or the part of speech is not being considered by the program. If you think this is an oversight and that this particular part of speech should be added, please contact me via the contact form, or if you'd like to fix it yourself, submit a pull request on GitHub.")
        return False


def clean_wikitext(parsed_definitions_dict):
    # Remove templates: anything that's inside double curly braces
    clean_definitions = {"noun" : [], "verb" : [], "adjective" : [], "adverb" : [], "pronoun" : [], "preposition" : []}
    
    # Extract and clean links: convert something like [[apple|Apple]] to Apple or [[apple]] to apple
    def clean_link(match):
        # Split on the pipe, if it's there, and return the human-readable part
        parts = match.group(1).split('|')
        return parts[-1] if parts else match.group(1)
    
    for word_type, definitions in parsed_definitions_dict.items():
        for count, definition in enumerate(definitions):
            temp_cleaned_definition = re.sub("{{", '<span style="color:grey;font-size:0.85em;"><i>', definition)
            temp_cleaned_definition = re.sub("}}", '</span></i>', temp_cleaned_definition)
            temp_cleaned_definition = re.sub("lb\|en\|", '', temp_cleaned_definition)
            temp_cleaned_definition = re.sub("n-g-lite\|", '', temp_cleaned_definition)
            temp_cleaned_definition = re.sub("q-lite\|", '', temp_cleaned_definition)
            temp_cleaned_definition = re.sub("senseid\|en\|Q5", '', temp_cleaned_definition)
            temp_cleaned_definition = re.sub("\[\[", '', temp_cleaned_definition)
            temp_cleaned_definition = re.sub("\]\]", '', temp_cleaned_definition)
            temp_cleaned_definition = re.sub("\|", '/', temp_cleaned_definition)
            
            temp_cleaned_definition = temp_cleaned_definition.strip()
            clean_definitions[word_type].append(temp_cleaned_definition)
            
    return clean_definitions


def clean_wikitext_new(definitions):
    """
    Cleans definitions dictionary (which itself is within an Anki card dictionary) so that the text is legible.
    
    :param definitions: A dictionary, passed to the function from an Anki card dictionary, containing definitions.
    :returns clean_definitions_list: An array of lines, each line being a definition, which are now legible.
    """
    # Remove templates: anything that's inside double curly braces
    clean_definitions = []
    new_defs = []
    
    # Extract and clean links: convert something like [[apple|Apple]] to Apple or [[apple]] to apple
    def clean_links(match):
        # Split on the pipe, if it's there, and return the human-readable part
        parts = match.group(1).split('|')
        return parts[-1] if parts else match.group(1)
    
    for definition in definitions:
        logger.info(f"Cleaning definition: {definition}")
        clean_definition_lines_list = []
        for line in definition:
            #temp_cleaned_definition_line = re.sub(r'\{\{.*?\}\}', '', line)
            # temp_cleaned_definition_line = re.sub(r'\[\[(.*?)\]\]', clean_links, temp_cleaned_definition_line)
            temp_cleaned_definition_line = line
            temp_cleaned_definition_line = temp_cleaned_definition_line.replace("{{", "(")
            temp_cleaned_definition_line = temp_cleaned_definition_line.replace("}}", ")")
            temp_cleaned_definition_line = temp_cleaned_definition_line.replace("]", "")
            temp_cleaned_definition_line = temp_cleaned_definition_line.replace("[", "")
            temp_cleaned_definition_line = temp_cleaned_definition_line.replace("|", ", ")
            # temp_cleaned_definition_line = re.sub(r'\n', ' ', temp_cleaned_definition_line)
            # temp_cleaned_definition_line = re.sub(r'#', '', temp_cleaned_definition_line)
            # temp_cleaned_definition_line = ' '.join(temp_cleaned_definition_line.split())
            temp_cleaned_definition_line = temp_cleaned_definition_line.strip()
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
    """
    Removes the definitions for the grammatical use of a word if that grammatical definition was not used in the user's 
    input text. The grammatical context is found in the card's dictionary 'tag' key.
    
    :param dict_array: The array of dictionaries being used to create Anki cards. Each dictionary represents a single 
    card.
    :returns dict_array: The dictionary array, now with irrelent definitions removed.
    """    
    for dict_index, dictionary in enumerate(dict_array):
        # Individual Anki card
        new_card_definitions = []
        
        for word_index, word_definitions_dict in enumerate(dictionary["definitions"]):
            # Individual word definitions
            logger.info(f"Attempting to match definition to tag for < {dictionary['words'][word_index]} >")            
            appropriate_word_def_found = False

            try:
                for grammar_key, definition in word_definitions_dict.items():
                    # Individual definitions for a word
                    
                    if definition and not appropriate_word_def_found:
                        try:
                            nltk_tag = dictionary["tags"][word_index][1]
                            logger.info(f"Comparing NLTK tag < {grammar_key} >  to tag in card dictionary < {nltk_tag} >")
                            if grammar_key == nltk_tag:
                                relevant_def = definition
                                if relevant_def:
                                    logger.info(f"Found relevant definition for < {dictionary['words'][word_index]} >, \n{relevant_def}")
                                    new_card_definitions.append(relevant_def)
                                    appropriate_word_def_found = True
                                logger.info(f"NLTK tag < {grammar_key} >  matches dictionary tag < {nltk_tag} >")
                                logger.info(f"Appropriate definition saved to temp dictionary for < {dictionary['words'][word_index]} >")
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
                    longest.append(f"NOTE: specific definition for the {dictionary['tags'][word_index][1]} form could not be found, so the cloest match was used.")
                    new_card_definitions.append(longest) 

                    logger.warning(f"Couldn't find relevant definition for < {dictionary['words'][word_index]} >, using: \n{longest}") 
                else:
                    logger.warning(f"No user-marked words for < {dictionary['words'][word_index]} >, so no definition being used.") 
                    new_card_definitions.append(["No definition found. You might have made a typo, or the word might not be in Wiktionary."])            
    
        dict_array[dict_index]["definitions"] = new_card_definitions
    return dict_array


def read_sentence_file(text_file):
    """
    Read the text from the selected text file.
    
    :param text_file: Text file containing sentences that should be turned into Anki cards.
    :returns text: The text from the file.
    :returns False: Return False if the file does not exist, or if there is an error.
    """
    try:
        with open(text_file, 'r', encoding="utf-8") as file:
            text = file.read()
    except:
        logger.error(f"Error reading user input file for AutoAnki process.")
        return False
    return text


def format_card(content, defs, words, tags, deck_name, lang):
    """
    Takes the information from a card dictionary and formats that information so that it is readable by anki. Using this
    function in a loop with multiple dictionaries will format multiple cards, all saved in a single variable. Anki will
    read this information (stored as a single unit) and create from it multiple individual cards.
    
    :param content: The text submitted by the user.
    :param defs: The definition(s) of the word(s) marked by the user.
    :param words: The word(s) marked by the user.
    :param deck_name: The name of the deck that the user wishes to import the cards to.
    :returns ankified_text: A string that can be saved to a text file and read by Anki. This contains one of more cards.
    """
    logger.info(f"Formatting card for < {words} >")
    # Remove the "*" keyword marker(s) and bold them with html tags
    pattern = r"\*\w+"
    bolded_text = re.sub(pattern, lambda x: f"<b>{x.group()[1:]}</b>", content)
    
    # Column 1 - Original text
    ankified_text = bolded_text + ";\""
    
    # Column 2 - Definitions
    for count, definition in enumerate(defs):
        tag = tags[count][1]
        ankified_text += f"<h3>{words[count]}, <i>{tag}</i>"
        
        try:
            if tag == "noun" and definition[0] != "No definition found. You might have made a typo, or the word might not be in Wiktionary." and lang in GENDERED_LANGS:
                for line_num, line in enumerate(definition):
                    if line_num == 0 and lang in GENDERED_LANGS:
                        ankified_text += f", <i>{line.replace('}', '')}</i></h3>"
                    else: 
                        ankified_text += f"{line_num}: {line.replace('}', '')}<br>"
            else:
                ankified_text += "</h3>"
                for line_num, line in enumerate(definition):
                    ankified_text += f"{line_num + 1}: {line.replace('}', '')}<br>"
        except:
            ankified_text += f"{str(definition)}"
        
    ankified_text += "\";"
    
    # Column 3 - Deck
    ankified_text += f"deck:{deck_name}"
    
    ankified_text = ankified_text.replace("\n", "<br>")
    ankified_text = ankified_text.replace("</h3><br><br>", "</h3>")
    
    ankified_text = ankified_text.replace("(", "<span style='font-size:0.75em;'><i>")
    ankified_text = ankified_text.replace(")", "</i></span>")
    
    logger.info(f"Successfully formatted card for < {words} >")
    
    return ankified_text


def get_nlp(language):
    # Get the relevant language package.
    # Arabic
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
        # Initialize the pipeline
        nlp = spacy_stanza.load_pipeline("de", package="hdt", processors='tokenize,mwt,pos,lemma', use_gpu=True)
    # Japanese
    if language == "Japanese":
        stanza.download("ja")
        # Initialize the pipeline
        nlp = spacy_stanza.load_pipeline("ja", package="gsd", use_gpu=True)
    # Korean
    if language == "Korean":
        stanza.download("ko")
        # Initialize the pipeline
        nlp = spacy_stanza.load_pipeline("ko", package="kaist", processors='tokenize,mwt,pos,lemma', use_gpu=True)
    # Latin
    if language == "Latin":
        stanza.download("la")
        # Initialize the pipeline
        nlp = spacy_stanza.load_pipeline("la", package="llct", processors='tokenize,mwt,pos,lemma', use_gpu=True)
    # Persian
    if language == "Persina":
        stanza.download("fa")
        # Initialize the pipeline
        nlp = spacy_stanza.load_pipeline("fa", package="seraji", processors='tokenize,mwt,pos,lemma', use_gpu=True)
    # Spanish
    if language == "Spanish":
        stanza.download("es")
        # Initialize the pipeline
        nlp = spacy_stanza.load_pipeline("es", package="ancora", processors='tokenize,mwt,pos,lemma', use_gpu=True)
    
    return nlp


def make_cards(text_file, language): 
    """
    Makes Anki cards from the text file submitted by the user.
    
    :param text_file: The text file selected by the user via the Gui.
    :param language: The language selected by the user via the Gui.
    """
    # Get the text from the user's file.
    text = read_sentence_file(text_file)
    if text == False:
        logger.error(f"Error reading user input file for AutoAnki process. Perhaps the text file is empty, corrupted, or incorrectly formatted. File content: >>\n{text}\n<<")
        return False
    
    # Split lines. This assumes the user submitted their input using independent lines for each card.
    split_text = text.splitlines()
    
    # Create dictionaries for each Anki card and add them to an array.
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
    logger.info(f"Finding all keywords marked with an asterisk.")
    print(f"Finding all keywords marked with an asterisk.")
    dict_array = find_keywords(dict_array)
    logger.info(f"Done finding keywords.")
    
    # Get the relevant language package.
    nlp = get_nlp(language)
    
    # Get grammar tags for each word via nltk natural language processing.
    logger.info(f"Processing grammatical context for all user input in order to find grammar tags.")
    print(f"Processing grammatical context for all user input in order to find grammar tags.")
    dict_array = get_tags(dict_array, language, nlp)
    logger.info(f"Done finding tags.")
    
    # Match nltk tags to wiktionary tag types. This does nothing other than change the definitions of the tags being 
    # used in the dictionaries.
    logger.info(f"Matching NLTK tags with readable tags.")
    print(f"Matching NLTK tags with readable tags.")
    dict_array = match_tags(dict_array)
    logger.info(f"Done matching tags.")
    
    # Get definitions from Wiktionary.
    for count, dictionary in enumerate(dict_array):
        logger.info(f"Getting word definitions from Wiktionary.")
        print(f"Getting word definitions from Wiktionary.")
        for w_count, word in enumerate(dictionary.get("words")):
            print(dictionary)
            if dictionary["tags"][w_count][1] in ["adjective", "verb", "noun"]:
                logger.info(f"Current word < {word} > is a noun, verb, or adjective. Removing any possible declension.")
                
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
                        # This is necessary because words that are not nounds must be lower case, but the user might have
                        # capitalised the word if it was at the start of a sentence.
                        word = word.lower()
                    
                # Replace the word in the dictionary with the undeclined version.
                dict_array[count]["words"][w_count] = word
                logger.info(f"Declension removal complete. Undeclined word: < {word} >")
            if word:
                if language != "German":
                    word = word.lower()
                logger.info(f"Connecting to Wiktionary API to retrieve definition for: < {word} >.")
                page_content = get_wiktionary_definition(word)
                logger.info(f"Defininition for < {word} > in language < {language} > retrieved.")
                logger.info(f"Removing other language definitions for < {word} > and returning only < {language} > definitions.")
                parsed_definitions_dict = parse_page(page_content, language)
                logger.info(f"Successfully isolated < {language} > definitions for < {word} >.")
                dict_array[count]["definitions"].append(parsed_definitions_dict)
                logger.info(f"Added definitions for < {word} > to card dictionary.")
    
    # Remove irrelevent definitions.
    logger.info(f"Removing all definitions that do not match the grammatical context of the word.")
    print(f"Removing all definitions that do not match the grammatical context of the word.")
    dict_array = remove_irrelevant_defs(dict_array)
    logger.info(f"Done removing irrelevant definitions.")
    
    # Clean definitions so that they're readable (remove HTML tags, etc.).
    logger.info(f"Cleaning definitions so that they're readable by removing HTML tags, etc.")
    print(f"Cleaning definitions so that they're readable by removing HTML tags, etc.")
    for count, dictionary in enumerate(dict_array):
        cleaned_defs = clean_wikitext_new(dictionary["definitions"])
        dict_array[count]["definitions"] = cleaned_defs
    logger.info(f"Done cleaning definitions.")
        
    # The text file which will be output and imported into Anki.
    anki_file = ""
    
    # The dictionaries are now ready to be used to create cards. They must be formatted so that Anki can read them and 
    # convert them.
    logger.info(f"Formatting Anki cards.")
    print(f"Formatting Anki cards.")
    for count, dictionary in enumerate(dict_array):
        if count > 0:
            anki_file += "\n"
        anki_file += format_card(dictionary["text"], dictionary["definitions"], dictionary["words"], dictionary["tags"], "Test", language)
    logger.info(f"Cards formatted.")
    
    # Save the cards to a single file for importing to Anki.
    save_filename = f"cards_import.txt"
    desktop_path = "D:\projects\software_dev\\autodict"
    full_file_path = "D:\projects\software_dev\\autodict\cards_import.txt"
    
    logger.info(f"Saving export file.")
    print(f"Saving export file.")
    
    print()
    pprint.pprint(dict_array)
    print()
    
    save_result = export_cards(save_filename, desktop_path, anki_file)
    if save_result:
        logger.info(f"File saved to {full_file_path}")
        print(f"File saved to {full_file_path}")
    else:
        logger.info(f"Error saving file to {full_file_path}")
        print(f"Error saving file to {full_file_path}")
        return False


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


def export_cards(file_name, desktop_path, anki_file):
    """
    Exports the Anki-formatted text file containing all generated Anki cards.
    
    :param file_name: Name that the file will be saved as.
    :anki_file: The content that will be saved as a text file.
    :returns result: Boolean indicating whether the file was successfully saved.
    """
    # Create the full file path
    full_file_path = os.path.join(desktop_path, file_name)
    
    # Open the file at the specified location in write mode
    try:
        with open(full_file_path, 'w', encoding="utf-8") as file:
            file.write(anki_file)
        return True
    except Exception as e:
        print(e)


def get_lemma(target_word, context, nlp):
    """
    Returns the undeclined form of a delcined German word.
    
    :param adjective: The declined German word.
    :returns: The undeclined form of the word.
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
    
    for token in text:
        print()
        print(token.text, token.lemma_, token.pos_, token.dep_, token.ent_type_)

    print("\nLEMMAS")
    print(lemmas)
    
    # Get the lemma of the target word.
    print()
    print(f"Target word: {target_word}")
    lemma = lemmas[target_word]
    
    print(f"Undeclined {target_word}: < {lemma} >")
    
    return lemma


if __name__ == "__main__":
    logger.info(f"Starting application.")
    
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(stylesheet)
    
    MainWindow = QtWidgets.QDialog()
    gui = Gui()
    gui.setupUI(MainWindow)
    MainWindow.show()
    gui.spawnTutorial()
    sys.exit(app.exec_())