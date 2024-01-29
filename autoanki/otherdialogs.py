from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import QtWidgets, QtCore, QtGui
import qtvscodestyle as qtvsc
from setupdialogs   import (setup_tutorial_dialog, setup_guiaa_dialog, setup_contact_dialog, setup_changelang_dialog)
from typing         import Union
import queue
import threading
import labeldata


LANGS = {
    # TODO: Get these languages working 
    "1": "Arabic",      # Not implemented
    "2": "English",
    "3": "French",
    "4": "German",
    "5": "Japanese",    # Not implemented
    "6": "Korean",      # Not implemented
    "7": "Latin",
    "8": "Persian",     # Not implemented
    "9": "Spanish"
}


class TutorialDialog(object):
    """Tutorial dialog that opens on startup.
    """
    def __init__(self, parent: QtWidgets.QDialog):
        self.parent = parent
        # Keep the dialog on top.
        # self.setWindowModality(QtCore.Qt.ApplicationModal) # type: ignore
        # self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint) # type: ignore
        
    def setupUi(self, Dialog: QtWidgets.QDialog) -> None:
        setup_tutorial_dialog(self, Dialog)
        
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        
        colourMode = self.parent.colour_mode
        if colourMode == "dark":
            stylesheet = qtvsc.load_stylesheet(qtvsc.Theme.DARK_VS)
        else:
            stylesheet = qtvsc.load_stylesheet(qtvsc.Theme.LIGHT_VS)
        self.window.setStyleSheet(stylesheet)
    
    def retranslateUi(self, Dialog: QtWidgets.QDialog) -> None:
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Tutorial"))
        self.radioButton.setText(_translate("Dialog", "Don\'t show this again"))
        self.pushButton_2.setText(_translate("Dialog", "close"))
        self.label_6.setText(_translate("Dialog", "Manually Search Wiktionary"))
        self.label_4.setText(_translate("Dialog", "Welcome to AutoAnki. "))
        self.label.setText(_translate("Dialog", labeldata.tutorial[0]))
        self.label_2.setText(_translate("Dialog", labeldata.tutorial[1]))
        self.label_3.setText(_translate("Dialog", "Tutorial, please read!"))
        self.label_5.setText(_translate("Dialog", "Automate Anki Cards Creation"))
    
    def close(self) -> None:
        """Close the tutorial dialog and update the config file to reflect the user's choice.
        """
        if self.radioButton.isChecked():
            self.parent.show_tutorial_on_startup = False
            self.parent.update_config()
        self.window.close()


class GuiAA(object):
    """The AutoAnki dialog.
    """
    def __init__(self, parent: QtWidgets.QDialog) -> None:
        self.parent = parent
        self.explorerUsed = False
    
    def setupUi(self, Dialog: QtWidgets.QDialog) -> None:
        setup_guiaa_dialog(self, Dialog)
        # Connect the custom buttons to their respective slots
        self.pushButton.clicked.connect(self._open_fileile)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        self.makeCardsButton.clicked.connect(self.__makeCards)
        self.cancelButton.clicked.connect(Dialog.reject)
        self.retranslateUi(Dialog)

    def retranslateUi(self, Dialog: QtWidgets.QDialog) -> None:
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "AutoAnki Card Generator"))
        self.headerLbl.setText(_translate("Dialog", "🀄 AutoAnki Card Generator 🀄"))
        self.label_2.setText(_translate("Dialog", "Deck name"))
        self.pushButton.setText(_translate("Dialog", "Open"))
        self.lineEdit.setText(self.parent.default_notes_file_location)

    def _open_fileile(self) -> None:
        """Opens a file explorer.
        """
        self.parent.add_user_file()
        self.lineEdit.setText(self.parent.notes_input_filepath)
        self.explorerUsed = True
        
    def __makeCards(self) -> None:
        """Start the card-making process.
        """
        if self.explorerUsed is False:
            self._open_file_default()
        
        deckName = self.lineEdit_2.text()
        if deckName == "":
            deckName = "unnamed"
            
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
        thread = threading.Thread(target=self.parent.make_cards, args=(deckName, self.messageQueue, 
            self.parent.default_autoanki_output_folder))
        thread.daemon = True
        thread.start()
        
        # Start a timer to periodically check the queue and update the console display
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.checkQueue)
        self.timer.start(100)  # Check every 100 ms

        self.overlay.show()
        
    def _open_file_default(self) -> None:
        filename = self.parent.default_notes_file_location
        self.parent.notes_input_filepath = filename
        
        f = open(filename, 'r', encoding="utf-8")
        with f:
            data = f.read()
            self.parent.notes_file_content = data
            
    def append_to_console_display(self, text) -> None:
        """Append text to the console display.

        :param text: Text sent from the card making thread.
        :type text: str
        """
        self.consoleDisplay.moveCursor(QtGui.QTextCursor.End)
        self.consoleDisplay.insertPlainText(text + '\n')
        self.consoleDisplay.moveCursor(QtGui.QTextCursor.End)
        
    def checkQueue(self) -> None:
        """Check the message queue for new messages.
        """
        while not self.messageQueue.empty():
            message = self.messageQueue.get()
            self.append_to_console_display(message)


class GuiContactDialog(QtWidgets.QDialog):
    """The contact dialog.
    """
    
    def setupUi(self, Dialog: QtWidgets.QDialog) -> None:
        setup_contact_dialog(self, Dialog)
        
        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept) # type: ignore
        self.buttonBox.rejected.connect(Dialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog: QtWidgets.QDialog) -> None:
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Contact"))
        self.label.setText(_translate("Dialog", labeldata.contact[0]))
        self.label_2.setText(_translate("Dialog", labeldata.contact[1]))
        self.label_3.setText(_translate("Dialog", "✨ **Contact Me** ✨"))


class GuiChangeLangWindow(object):
    """The change language dialog.
    """
    def __init__(self, parent: QtWidgets.QDialog) -> None:
        self.parent = parent
        self.tempLang = ""
    
    def setupUi(self, changeLangWindow: QtWidgets.QDialog) -> None:
        setup_changelang_dialog(self, changeLangWindow)
        
        self.changeLangConf.clicked.connect(self._handle_apply)

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
        
        self._retranslate_ui(changeLangWindow)
        QtCore.QMetaObject.connectSlotsByName(changeLangWindow)
    
    def _retranslate_ui(self, changeLangWindow: QtWidgets.QDialog) -> None:
        _translate = QtCore.QCoreApplication.translate
        changeLangWindow.setWindowTitle(_translate("changeLangWindow", "Language Settings"))
        __sortingEnabled = self.langsList.isSortingEnabled()
        
        self.langsList.setSortingEnabled(False)
        item1 = self.langsList.item(0)
        item2 = self.langsList.item(1)
        item3 = self.langsList.item(2)
        item4 = self.langsList.item(3)
        item5 = self.langsList.item(4)
        item6 = self.langsList.item(5)
        item7 = self.langsList.item(6)
        item8 = self.langsList.item(7)
        item9 = self.langsList.item(8)
        items_arr = [item1, item2, item3, item4, item5, item6, item7, item8, item9]
        
        # Apply text to list elements
        for item_i, item in enumerate(items_arr):
            if item != None:
                item.setText(_translate("changeLangWindow", LANGS[str(item_i + 1)]))
        
        # Hide unimplemented languages
        unimplemented = [item1, item5, item6, item8]
        for u_item in unimplemented:
            if u_item != None:
                u_item.setHidden(True)
                
        self.langsList.setSortingEnabled(__sortingEnabled)
        self.langsList.clicked.connect(self._update_selection)
        
        # Apply the program's currently selected language to the list
        langIndex = self._index_language()
        if langIndex   == 1:
            langItem   =  item1
        elif langIndex == 2:
            langItem   =  item2
        elif langIndex == 3:
            langItem   =  item3
        elif langIndex == 4:
            langItem   =  item4
        elif langIndex == 5:
            langItem   =  item5
        elif langIndex == 6:
            langItem   =  item6
        elif langIndex == 7:
            langItem   =  item7
        elif langIndex == 8:
            langItem   =  item8
        elif langIndex == 9:
            langItem   =  item9
        else:
            langItem = None 
        if langItem != None:
            self._highlight_currentLang(langItem)
    
    def _handle_apply(self) -> None:
        """Applies the selected language by updating the main window language variable.
        """
        if self.tempLang:
            self.parent.change_language(self.tempLang)
        self.window.close()
    
    def _highlight_currentLang(self, item: QtWidgets.QListWidgetItem) -> None:
        """Highlight the currently selected language on the selection list.
        """
        self.langsList.setCurrentItem(item)
        self.langsList.setFocus()
    
    def _update_temp_language_var(self, lang: str) -> None:
        """Updates the language var used to save, temporarily, when a user clicks on a language list object, but is yet 
        to save that as their selection.
        """
        self.tempLang = lang
    
    def _get_current_lang_selection(self) -> str:
        """Get the currently selected language from the list of languages GUI element.
        """
        selection = self.langsList.currentRow()
        selection += 1
        selection = LANGS[str(selection)]
        return selection
    
    def _update_selection(self) -> None:
        """Update the program with the currently selected (temporary, not yet applied) language selection from the list.
        """
        selection = self._get_current_lang_selection()
        self._update_temp_language_var(selection)
    
    def _index_language(self) -> Union[int, None]:
        """Determine which list element a language corresponds with.
        """
        lang = self.parent.selected_search_language
        # print(lang)
        if lang   == "Arabic":
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
            return None