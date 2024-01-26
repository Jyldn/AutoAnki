from PyQt5              import QtCore, QtWidgets
from setupdialogs       import setup_setting_dialog
import qtvscodestyle    as qtvsc



class GuiSettingsDialog(object):
    def __init__(self, parent: QtWidgets.QDialog) -> None:
        self.parent = parent
    
    def setupUi(self, settingsDialog: QtWidgets.QDialog) -> None:
        """Sets up the settings dialog.
        """
        setup_setting_dialog(self, settingsDialog)
        self.settingsBox.clicked.connect(self.__handleApplySettings)
        
        # Setup zoom factor
        zoomFactor = self.parent.zoomFactor
        zoomFactor = self.__convertZoomLevel(zoomFactor)
        self.fontSizeSelect.setValue(zoomFactor)
        
        self.__retranslateUi(settingsDialog)
        self.settingsBox.accepted.connect(settingsDialog.accept) # type: ignore
        self.settingsBox.rejected.connect(settingsDialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(settingsDialog)
        
        colourMode = self.parent.colourMode
        if colourMode == "dark":
            stylesheet = qtvsc.load_stylesheet(qtvsc.Theme.DARK_VS)
        else:
            stylesheet = qtvsc.load_stylesheet(qtvsc.Theme.LIGHT_VS)
        
        self.window.setStyleSheet(stylesheet)
        self.settingsFrame.setStyleSheet("QFrame {border: 0px solid dimgrey;}")    
    
    def __retranslateUi(self, settingsDialog: QtWidgets.QDialog) -> None:
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
        self.__checkBoxes()
        self.__getLocations()
        
        # Set text
        self.getEtymLbl.setText(_translate("getEtymLbl", "Show etymology"))
        self.getUsageLbl.setText(_translate("getUsageLbl", "Show usage notes"))
        self.searchSettingsLbl.setText(_translate("searchSettingsLbl", "Manual search settings"))
        self.generalSettingsLbl.setText(_translate("generalSettingsLbl", "General settings"))
        self.defInConjLbl.setText(_translate("defInConjLbl", "Definition + conjugation"))
        self.defaultLoadLbl.setText(_translate("defaultLoadLbl", "Default notes file"))
        self.defaultSaveLbl.setText(_translate("defaultSaveLbl", "Default output folder"))
        
    def __convertZoomLevel(self, zoomLevel: float) -> int:
        """Converts the zoom level from a float to an int. This is because the front-end slider only accepts ints.

        Arguments:
            zoomLevel -- Zoom level currently being used

        Returns:
            Zoom level compatabile with the front-end
        """
        zoomLevel = int(zoomLevel* 100)
        return zoomLevel
    
    def __handleApplySettings(self) -> None:
        """Applies the selected language by updating the parent's language variable and then closes the dialog.
        """
        # Get settings variables
        newZoomFactor = self.fontSizeSelect.value()
        newColourSelect = self.defaultColourModeCB.currentText()
        newColourSelect = newColourSelect.lower()
        
        self.__applyChecks()
        self.__applyLocations()
        self.parent.applySettings(newZoomFactor, newColourSelect)
        self.window.close()
    
    def __checkBoxes(self) -> None:
        """Sets the checkboxes to the current config values.
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
    
    def __applyChecks(self) -> None:
        """Updates the parent's variables according to the checkbox values.
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
            self.parent.getUsage     = "True"
        else:
            self.parent.getUsage     = "False"
            
        if self.defInConjRadio.isChecked():
            self.parent.defInConj    = "True"
        else:
            self.parent.defInConj    = "False"
    
    def __applyLocations(self) -> None:
        """Updates the parent's default load and save paths.
        """
        self.parent.defaultNoteLocation = self.defaultLoadEdit.text()
        self.parent.defaultOutputFolder = self.defaultSaveEdit.text()
        
    def __getLocations(self) -> None:
        """Sets the default load and save paths to the current config values.
        """
        self.defaultLoadEdit.setText(self.parent.defaultNoteLocation)
        self.defaultSaveEdit.setText(self.parent.defaultOutputFolder)