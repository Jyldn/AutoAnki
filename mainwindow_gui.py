from concurrent.futures import Future
from PyQt5.QtWidgets    import QWidget
from PyQt5.QtCore       import Qt
from PyQt5              import (QtCore, QtWidgets)
from settings_gui       import GuiSettingsDialog
from etc_gui            import (GuiContactDialog, GuiChangeLangWindow, GuiAA, TutorialDialog)
from config_handler      import config_check
from defsearch           import (grab_wik_conjtable, strip_bs4_links, get_defs_man_search)
from make_cards         import make_cards
from html_strings       import (HTML_HEADER_DARK, HTML_HEADER_LIGHT, HTML_HEADER_DARK_CONJ, HTML_FOOTER)
from setup_classes      import setup_mainwindow
from savefile_handler   import (EncodedSavefilesContent, UnencodedSavefilesContent, encode_savefiles_content, 
                                decode_savefiles_content,encode_single_entry)
from dataclasses        import (dataclass, asdict)

import qtvscodestyle    as qtvsc
import uuid
import re
import configparser
import queue
from typing import Union, List, Dict


# Highdpi scaling
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)  # type: ignore
# QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True) 

STYLESHEET = qtvsc.load_stylesheet(qtvsc.Theme.LIGHT_VS)
STYLESHEET_DRK = qtvsc.load_stylesheet(qtvsc.Theme.DARK_VS)

SAVEFILE_SEPERATOR = "\n====================================\n"

LANG_CODE_REF = {
    "English"   : "en",
    "French"    : "fr",
    "German"    : "de",
    "Spanish"   : "es",
    "Latin"     : "la"
}


class MainWindowGui(QWidget):
    """
    The main window.
    """
    def __init__(self, parent=None) -> None:
        super(MainWindowGui, self).__init__()
        
        # Class variables
        self.currentDefsStringified = ""
        self.mainWindow             = ""
        self.selectedFileContent    = ""
        self.currentInputFilePath   = ""
        self.wordOne                = ""
        self.conjWord               = ""
        self.htmlContent            = ""
        self.htmlContentText        = ""
        self.manualSearchMode       = "word"
        self.currentOverallMode     = "search"
        self.savedKeywords          = False
        self.AALayoutSet            = False
        self.conjugationMode        = False
        self.displayingSavable      = False
        self.current_definitions    = {}
        self.savedSidebarWords      = {"English": {}, "French": {}, "German": {}, "Spanish": {}, "Latin": {}}
        self.defaultResolution      = [800, 800]
        
        # Config variables
        self.configColourMode       = ""
        self.defaultNoteLocation    = ""
        self.defaultOutputFolder    = ""
        self.showTutorial           = "True"
        self.defInConj              = "True"
        self.getEtymology           = "False"
        self.getUsage               = "False"
        self.interfaceLanguage      = "English"
        self.currentLanguage        = "English"
        self.colourMode             = "light"
        self.zoomFactor             = 100
        
        # Style values
        self.topOffset = 40
    
    def setupUI(self, MainWindow: QtWidgets.QMainWindow) -> None:
        """Initialise the GUI.
        """
        setup_mainwindow(self, MainWindow)
        
        # Connect buttons
        self.colourModeBtn.clicked.connect              (self.__toggleColourMode)
        self.settingsBtn.clicked.connect                (self.__spawnSettingsDialog)
        self.contactBtn.clicked.connect                 (self.__spawnContactDialog)
        self.autoAnkiBtn.clicked.connect                (self.__openAutoAnki)
        self.changeLangBtn.clicked.connect              (self.__spawnLanguageDialog)
        self.saveWord.clicked.connect                   (self.saveWordToSide)
        self.searchBtn.clicked.connect                  (self.__searchWiki)
        self.searchModeCombo.currentIndexChanged.connect(self.__onSearchModeChange)
        
        # Initialise html output display
        html_content = self.__constructHtml("")
        self.searchOutputBrowser.setHtml(html_content)
        
        # Initialise config
        configVars = config_check()
        self.__applyConfig(configVars)
        
        # Retranslate
        self.__retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
        # Apply colour mode on startup
        if self.colourMode == "dark":
            self.__activateDarkmode()
            self.__updateHtmlView()
        else:
            self.__activateLightmode()
        self.__toggleSaveBtnEnabled() # Save button should be disabled at startup
        
        # Load saves words
        rawSavedWords  = self.__getSavedContentRaw()
        savedWordsDict = self.__parseSavedWords(rawSavedWords)
        for count, id_word_pair in enumerate(savedWordsDict[self.currentLanguage].items()):
            self.__genSavedWords(id_word_pair, count)
    
    def __retranslateUi(self, MainWindow: QtWidgets.QMainWindow) -> None:
        """Retranslate the GUI.
        """
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "AutoAnki"))
        
        # Buttons
        self.saveWord.setText(_translate("MainWindow", "Add"))
        self.colourModeBtn.setText(_translate("MainWindow", "Dark Mode"))
        self.settingsBtn.setText(_translate("MainWindow", "Settings"))
        self.autoAnkiBtn.setText(_translate("MainWindow", "AutoAnki"))
        self.changeLangBtn.setText(_translate("MainWindow", "Change Language"))
        self.searchBtn.setText(_translate("MainWindow", "Search"))
        self.contactBtn.setText(_translate("MainWindow", "Contact"))
        
        # Labels
        self.sideLabel.setText(_translate("MainWindow", "Saved Words"))
        self.sideLabel.setAlignment(Qt.AlignCenter) # type: ignore
        
        self.__updateLangLabel(self.currentLanguage)
        self.currentLangLabel.setAlignment(Qt.AlignCenter) # type: ignore
        
    def updateConfig(self) -> None:
        """Updates the config file with new variables.
        """
        config = configparser.ConfigParser()
        
        config['LanguagePreferences']  = {
            'InterfaceLanauge'         : self.interfaceLanguage,
            'SearchLanguage'           : self.currentLanguage}

        config['Interface']            = {
            'ColourMode'               : self.configColourMode,
            'ZoomLevel'                : int(self.zoomFactor * 100)}
        
        config['Behaviour']            = {
            'ShowTutorial'             : self.showTutorial}
        
        config['SearchSettings']       = {
            'GetEtymology'             : self.getEtymology,
            'GetUsage'                 : self.getUsage, 
            'defInConj'                : self.defInConj}
        
        config['DefaultLocations']     = {
            'defaultNotesFile'         : self.defaultNoteLocation,
            'defaultOutputFolder'      : self.defaultOutputFolder}
        
        with open("config.ini", 'w') as configfile:
            config.write(configfile)                    
        self.__updateLangLabel(self.currentLanguage)
    
    def __applyConfig(self, configVars: list) -> None:
        """Apply config variables read from the config.ini file.

        Parameters
        ----------
        configVars : list
            List of config data.
        """
        self.interfaceLanguage   = configVars[0]
        self.currentLanguage     = configVars[1]
        self.colourMode          = configVars[2]
        self.configColourMode    = configVars[2]
        self.zoomFactor          = configVars[3]
        self.showTutorial        = configVars[4]
        
        # Search settings
        self.getEtymology        = configVars[5]
        self.getUsage            = configVars[6]
        self.defInConj           = configVars[7]
        self.defaultNoteLocation = configVars[8]
        self.defaultOutputFolder = configVars[9]
        
        # Apply config
        self.__applyZoomLvl   (self.zoomFactor)
        self.__updateLangLabel(self.currentLanguage)
    
    def __updateLangLabel(self, lang: str) -> None:
        """Add an emoji to the language label.
        """
        emoji = ""
        if lang   == "French":
            emoji =  "🥖"
        elif lang == "German":
            emoji =  "🥨"
        elif lang == "Spanish":
            emoji =  "💃"
        elif lang == "Latin": 
            emoji =  "🏺"
        elif lang == "English":
            emoji =  "💂"
        self.currentLangLabel.setText(f"{lang} {emoji}")
            
    def applySettings(self, newZoomFactor: int, newColourMode: str) -> None:
        """Apply settings from the settings dialog.
        """
        # Zoom factor needs a decimal, but the input here is a float, so divide.
        self.__applyZoomLvl(newZoomFactor)
        self.configColourMode = newColourMode
        
    def __applyZoomLvl(self, newZoomFactor: int) -> None:
        """Apply the zoom level.
        """
        zoomFactorFlt: float = newZoomFactor / 100 
        self.zoomFactor = zoomFactorFlt
        self.searchOutputBrowser.setZoomFactor(zoomFactorFlt)
    
    def getZoomFactor(self) -> float:
        """Get the current zoom factor.
        """
        return self.zoomFactor        
    
    def __onSearchModeChange(self, index: int) -> None:
        """Change the search mode when the user selects a different option from the combo box.

        Parameters
        ----------
        index : int
            The index of the combo box.
        """
        mode = self.searchModeCombo.itemData(index)
        if mode == "sentence":
            self.manualSearchMode   = "sentence"
            self.conjugationMode    = False
        elif mode == "conjugation":
            self.conjugationMode    = True
        elif mode == "word":
            self.manualSearchMode   = "word"
            self.conjugationMode    = False
    
    def __toggleSaveBtnEnabled(self) -> None:
        """Toggle the save button on/off. Should be off by default, and should be enabled after the user has done a 
        search.
        """
        if self.displayingSavable is True:
            self.saveWord.setEnabled(True)
        else:
            self.saveWord.setEnabled(False)
    
    def __toggleColourMode(self) -> None:
        """Toggle dark/light modes when user presses the colour mode button.
        """
        if self.colourMode == "light":
            self.__activateDarkmode()
        else:
            self.__activateLightmode()
        self.__updateHtmlView()
        self.__updateLangLabel(self.currentLanguage)
    
    def __activateDarkmode(self) -> None:
        """Apply dark mode.
        """
        stylesheet = qtvsc.load_stylesheet(qtvsc.Theme.DARK_VS)
        self.mainWindow.setStyleSheet(stylesheet) # type: ignore
        self.colourMode = "dark"
        self.__reapplyBorderColours()
        self.setMyStyleDark()
        self.colourModeBtn.setText("Light Mode")
    
    def __activateLightmode(self) -> None:
        """Apply light mode.
        """
        stylesheet = qtvsc.load_stylesheet(qtvsc.Theme.LIGHT_VS)
        self.mainWindow.setStyleSheet(stylesheet) # type: ignore
        self.colourMode = "light"
        self.__reapplyBorderColours()
        self.setMyStyleLight()
        self.colourModeBtn.setText("Dark Mode")
    
    def __reapplyBorderColours(self) -> None:
        """When the theme changes, the colour of the border frames resets. These colours need to be reapplied.
        """
        if self.colourMode == "dark":
            self.sidebarFrame.setStyleSheet     ("QFrame {border: 1px solid dimgrey;}")
            self.searchInputFrame.setStyleSheet ("QFrame {border: 1px solid dimgrey;}")
            self.outputFrame.setStyleSheet      ("QFrame {border: 1px solid dimgrey;margin-top: 5px;}")
        else:
            self.sidebarFrame.setStyleSheet     ("QFrame {border: 1px solid lightgrey;}")
            self.searchInputFrame.setStyleSheet ("QFrame {border: 1px solid lightgrey;}")
            self.outputFrame.setStyleSheet      ("QFrame {border: 1px solid lightgrey;margin-top: 5px;}")
    
    def setMyStyleLight(self) -> None:
        """Styling changes (border radius, colours, etc.) applied to the current theme library.
        """
        self.sidebarFrame.setStyleSheet(
            """
            QFrame {
                border: 0px solid lightgrey;
                border-radius: 10px;
                background-color: #FAFAFA; } 
            """)
        
        self.searchInputFrame.setStyleSheet(
            """
            QFrame#searchInputFrame {
                border: 0px solid lightgrey;
                border-radius: 10px;
                background-color: #FAFAFA; } 
            """)
        
        self.outputFrame.setStyleSheet(
            """
            QFrame {
                border: 0px solid lightgrey;
                border-radius: 10px; } 
            """)
        
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollAreaLayout.setObjectName("scrollAreaLayout")
        self.scrollAreaWidgetContents.setStyleSheet(
            """
            QWidget#scrollAreaWidgetContents, QLabel {
                background-color: #FAFAFA; } 
            """)
        
        self.searchInputEdit.setStyleSheet(
            """
            QTextEdit {
                border: 1px solid lightgrey;
                border-radius: 5px; }
            """)
        
        self.mainFrame.setStyleSheet(
            """
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
        
    def setMyStyleDark(self) -> None:
        """Styling changes (border radius, colours, etc.) applied to the current theme library.
        """
        self.sidebarFrame.setStyleSheet(
            """
            QFrame {
                border: 0px solid lightgrey;
                border-radius: 10px;
                background-color: #292929;
                    }
            """)
        
        self.searchInputFrame.setStyleSheet(
            """
            QFrame#searchInputFrame {
                border: 0px solid lightgrey;
                border-radius: 10px;
                background-color: #292929;
                    }
            """)
        
        self.outputFrame.setStyleSheet(
            """
            QFrame {
                border: 0px solid lightgrey;
                border-radius: 10px;
                    }
            """)  
        
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollAreaLayout.setObjectName("scrollAreaLayout")
        self.scrollAreaWidgetContents.setStyleSheet(
            """
            QWidget#scrollAreaWidgetContents, QLabel {
                background-color: #292929; }
            """)   
        
        self.searchInputEdit.setStyleSheet(
            """
            QTextEdit {
                border: 1px solid #171717;
                border-radius: 5px; }
            """)  
        
        self.mainFrame.setStyleSheet(
            """
            QPushButton {
                border-radius: 3px; }
            QComboBox {
                border-radius: 3px; }
            QFrame {
                border: 0px; margin: 0px; }
            """)
        
        self.saveWord.setStyleSheet("QPushButton {border-radius: 3px;}")
    
        
    def __updateHtmlView(self) -> None:
        """Update the front-end search output.
        """
        self.__constructHtml(self.htmlContentText)
        self.searchOutputBrowser.setHtml(self.htmlContent)
    
    def __constructHtml(self, content: str) -> str:
        """Construct the HTML for the front-end output.

        Parameters
        ----------
        content : str
            The content to be displayed in the output.

        Returns
        -------
        str
            Content formatted as HTML for the front-end output.
        """
        html    = ""
        isTable = False
        
        # Determine if it's a conjugation table
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
    
    def __searchWiki(self) -> bool:
        """Search Wiktionary for a specific word, phrase, or conjugation table.
        """        
        # Get search term from input box.
        inputTxt = self.searchInputEdit.toPlainText()
        inputTxt = inputTxt.strip()
        inputTokens = ""
        
        # Check number of words
        if self.manualSearchMode == "word" or self.conjugationMode == True:
            inputTokens = inputTxt.split()
            if not inputTokens:
                self.searchOutputBrowser.setHtml("<p>No input. Please enter a word to get its definition.</p>")
                return False
        elif self.manualSearchMode == "sentence":
            inputTokens = [inputTxt]
        
        # Send search term to API caller and get definitions
        defsDictsArray = []
        if self.conjugationMode == True and len(inputTokens) == 1:
            for token in inputTokens:
                self.conjWord = token
                conjs    = f"<h3>{token}</h3>"
                conjs   += grab_wik_conjtable(token, self.currentLanguage)
                conjs    = strip_bs4_links(conjs)
                
                if self.defInConj == "True":
                    defsDictsArray.append(self.__getDefs(token))
                    self.wordOne      = token
                    conjs            += f"<h3></h3>"
                    definitionsString = self.__stringifyDefDict(defsDictsArray[0])
                    conjs            += definitionsString
                
                self.htmlContentText = conjs
                self.__updateHtmlView()
                self.displayingSavable = True
                self.__toggleSaveBtnEnabled()
                return True
        
        elif self.conjugationMode == True:
            self.searchOutputBrowser.setHtml("<p>Conjugation tables can only be generated for one word at a time.</p>")
            return False
        
        else:  # Word search
            for token in inputTokens:
                defsDictsArray.append(self.__getDefs(token))
        
            # Stringify definitions dictionary.
            defs = ""            
            for defsDictI, defsDict in enumerate(defsDictsArray):
                if defsDictI > 0:
                    defs += "<hr>"
                if defsDictI == 0:
                    self.wordOne = inputTokens[defsDictI]
                defs  += f"<h3>{inputTokens[defsDictI]}</h3>"
                defStr = self.__stringifyDefDict(defsDict)
                defs  += defStr
            
            self.__updateDefsStr              (defs)
            self.__displayDefs                    ()
            self.__updatCurrentDefs (defsDictsArray)
            self.__toggleSaveBtnEnabled           ()
            self.displayingSavable            = True
            return True
        return False
    
    def __getDefs(self, keyword: str) -> Union[Dict[str, List[str]], None]:
        """Call the Wiktionary API and get the definition for a specific word/phrase.
        """
        return get_defs_man_search(keyword, self.currentLanguage, self.getEtymology, self.getUsage)
    
    def __stringifyDefDict(self, defsDict: dict) -> str:
        """Convert a definitions dictionary to a string. Also appropriately formats the string for HTML display.

        Parameters
        ----------
        defsDict : dict
            Dictionary containing the definitions for a word/phrase. Keys represent a grammar tag, and values are the 
            corresponding definitions.

        Returns
        -------
        str
            Stringified version of the definitions dictionary with HTML formatting.
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
    
    def __updateDefsStr(self, defsString: str) -> None:
        """Update the definitions variable.
        """
        self.currentDefsStringified = defsString
    
    def __updatCurrentDefs(self, new_definition_dict) -> None:
        """Update the definitions variable.
        """
        self.current_definitions = new_definition_dict
    
    def __displayDefs(self) -> None:
        """Clear the search output display and update it with the currently saved definitions/table.
        """
        self.htmlContentText = self.currentDefsStringified
        self.__updateHtmlView()
    
    def makeCards(self, deckName: str, messageQueue, savePth: str) -> None:
        """Make Anki cards from the user-selected text file.

        Parameters
        ----------
        deckName : str
            The name of the Anki deck. Used for the Anki deck name and the output file name.
        messageQueue : MessageQueue object
            Sends messages to the front-end to update the user on the program's progress.
        savePth : str
            Folder that the Anki input file will be saved.
        """
        make_cards(self.currentInputFilePath, self.currentLanguage, deckName, messageQueue, savePth)
    
    def __spawnSettingsDialog(self) -> None:
        """Bring up the settings dialog.
        """
        self.settingsDlg = QtWidgets.QDialog()
        self.UISettings = GuiSettingsDialog(self)
        self.UISettings.setupUi(self.settingsDlg)
        
        # Colour mode styling
        if self.colourMode == "dark":
            self.settingsDlg.setStyleSheet(STYLESHEET_DRK)
        else:
            self.settingsDlg.setStyleSheet(STYLESHEET)
        
        self.settingsDlg.show()

    def __spawnLanguageDialog(self) -> None:
        """Bring up the language selector dialog.
        """
        self.windowLangs = QtWidgets.QDialog()
        self.UILangs = GuiChangeLangWindow(self)
        self.UILangs.setupUi(self.windowLangs)
        
        # Colour mode styling
        if self.colourMode == "dark":
            self.windowLangs.setStyleSheet(STYLESHEET_DRK)
        else:
            self.windowLangs.setStyleSheet(STYLESHEET)
        
        self.windowLangs.show()
        
    def __spawnContactDialog(self) -> None:
        """Bring up the contact dialog.
        """
        self.windowContact = QtWidgets.QDialog()
        self.UIContact = GuiContactDialog()
        self.UIContact.setupUi(self.windowContact)
        
        # Colour mode styling
        if self.colourMode == "dark":
            self.windowContact.setStyleSheet(STYLESHEET_DRK)
        else:
            self.windowContact.setStyleSheet(STYLESHEET)
        
        self.windowContact.show()
        
    def __openAutoAnki(self) -> None:
        """Bring up the AutoAnki dialog.
        """
        self.windowAa = QtWidgets.QDialog()
        self.UIAa = GuiAA(self)
        self.UIAa.setupUi(self.windowAa)
        
        # Colour mode styling
        if self.colourMode == "dark":
            self.windowAa.setStyleSheet(STYLESHEET_DRK)
        else:
            self.windowAa.setStyleSheet(STYLESHEET)
        
        self.windowAa.show()
        
    def spawnTutorial(self) -> None:
        """Bring up the language selector dialog.
        """
        if self.showTutorial == "True":
            self.windowTute = QtWidgets.QDialog()
            self.UITute = TutorialDialog(self)
            self.UITute.setupUi(self.windowTute)
            self.windowTute.show()
        else:
            pass
    
    def addFile(self) -> None:
        """Opens a file explorer.
        """
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)
        
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            self.currentInputFilePath = filenames[0]
            
            f = open(filenames[0], 'r', encoding="utf-8")
            with f:
                data = f.read()
                self.selectedFileContent = data
    
    def getCurrentLang(self) -> str:
        """Get the current language.
        """
        return self.currentLanguage
    
    def changeLanguage(self, newLang: str) -> None:
        """Update the language variable.
        """
        # Remove all buttons from the scroll area
        for uid in self.savedSidebarWords[self.currentLanguage].keys():
            word_btn    = self.sidebarInnerTopFrame.findChild(QtWidgets.QPushButton, f"sideButton{uid}")
            remove_btn  = self.sidebarInnerTopFrame.findChild(QtWidgets.QPushButton, f"sideButtonRmv{uid}")
            self.scrollAreaLayout.removeWidget(word_btn)
            self.scrollAreaLayout.removeWidget(remove_btn)
        
        self.currentLanguage = newLang
                
        for count, id_word_pair in enumerate(self.savedSidebarWords[self.currentLanguage].items()):
            print("MAKING CARD BTN")
            self.__genSavedWords(id_word_pair, count)
        
        self.updateConfig()
    
    def getColourMode(self) -> str:
        """Get the current colour mode.
        """
        return self.colourMode
    
    def saveWordToSide(self) -> None:
        """Saves a word to the sidebar. Saved words are associated with a language so that only words for the current
        language are displayed. Words are saved to a file (one file per language), and the sidebar is populated 
        with buttons that load the saved words.
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
        self.__savePinnedItemToFile(self.htmlContentText)
    
    def __getSavedContentRaw(self) -> EncodedSavefilesContent:
        """Get the encoded save-content.
        """
        temp_savefiles_content = {}
        for language in self.savedSidebarWords.keys():
            with open(f"{LANG_CODE_REF[language]}-sf.dat", "r", encoding="utf-8") as f:
                savefile_content = f.read()
                f.close()
                temp_savefiles_content[language] = savefile_content
        
        return EncodedSavefilesContent(**temp_savefiles_content)
    
    def __parseSavedWords(self, encodedRawContent: EncodedSavefilesContent) -> dict:
        """Parse the saved words file and return a list of words.
        """
        unencodedRawSaveContent : UnencodedSavefilesContent = (decode_savefiles_content(encodedRawContent))
        
        for language, savedContent in asdict(unencodedRawSaveContent).items():
            savedItems = savedContent.split(SAVEFILE_SEPERATOR)
            # Remove the last entry (it is empty).
            savedItems.pop()
            # Save the retrieved words to the class variable.
            for item in savedItems:
                uniqueId = str(uuid.uuid1(node=None, clock_seq=None))
                self.savedSidebarWords[language][uniqueId] = item
            
        return self.savedSidebarWords
    
    def __genSavedWords(self, id_word_pair: tuple, count) -> None:
        """Generate the saved words buttons for the sidebar.

        Parameters
        ----------
        id_word_pair : list
            List containing the saved item's unique ID and its content.
        count : int
            The number of buttons already in the sidebar. Used to determine the position of the new buttons.
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
        if match != None:
            word = match.group(1)
            if len(word) > 9:
                    word = word[:7] + ".."     
            newWordBtn.setText(f"{word}")

            # Determine if it's a conjugation table.
            if "<table" in id_word_pair[1]:
                if len(word) > 9:
                    word = word[:7] + ".."
                newWordBtn.setText(f"{word}") 
        
        # newWordBtn.setStyleSheet("QPushButton { text-align: left; }") # Align text on buttons to the left.

        # Dynamically connect button to function.
        newWordBtn.clicked.connect(
            lambda: self.loadSavedWord(
                self.savedSidebarWords[self.currentLanguage][id_word_pair[0]]
                )
            )
    
    def __removeSavedWord(self, unique_id: str) -> None:
        """Remove a saved word by deleting its save-file content, session-variable entry, and sidebar buttons.

        Parameters
        ----------
        unique_id : str
            The unique ID of the saved word.
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
    
    def __updateSavedWordsFile(self) -> None:
        """Update the saved words file with the new list of saved words.
        """
        with open(f"{self.currentLanguage}_words.txt", "w", encoding="utf-8") as f:
            for content in self.savedSidebarWords[self.currentLanguage].values():
                f.write(content)
                f.write(SAVEFILE_SEPERATOR)
            f.close()
    
    def loadSavedWord(self, content: str) -> None:
        """Load a saved word into the front-end output.

        Parameters
        ----------
        content : str
            The content of the saved word. HTML formatted, but lacks header and footer information. This is intentional
            because header content is specific to the currently applied colour mode.
        """
        self.htmlContentText = content
        self.__constructHtml(content)
        self.searchOutputBrowser.setHtml(self.htmlContent)
    
    def __savePinnedItemToFile(self, content: str) -> None:
        unencodedEntry = content + SAVEFILE_SEPERATOR
        encodedEntry = encode_single_entry(unencodedEntry).decode("utf-8")
        with open(f"{LANG_CODE_REF[self.currentLanguage]}-sf.dat", "a", encoding="utf-8") as f:
            f.write(encodedEntry)
            f.close()