from PyQt5              import QtCore, QtWidgets
from setupdialogs       import setup_settings_dialog
import qtvscodestyle    as qtvsc



class GuiSettingsDialog(object):
    def __init__(self, parent: QtWidgets.QDialog) -> None:
        self.parent = parent
    
    def setupUi(self, settingsDialog: QtWidgets.QDialog) -> None:
        """Sets up the settings dialog.
        """
        setup_settings_dialog(self, settingsDialog)
        
        self.window = settingsDialog
        
        self.settings_frame.clicked.connect(self.__handleApplySettings)
        
        # Setup zoom factor
        zoom_factor = self.parent.zoom_factor
        zoom_factor = self._convert_zoom_level(zoom_factor)
        self.font_size_select.setValue(zoom_factor)
        
        self.__retranslateUi(settingsDialog)
        self.settings_frame.accepted.connect(settingsDialog.accept) # type: ignore
        self.settings_frame.rejected.connect(settingsDialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(settingsDialog)
        
        colour_mode = self.parent.colour_mode
        if colour_mode.value == "dark":
            stylesheet = qtvsc.load_stylesheet(qtvsc.Theme.DARK_VS)
        else:
            stylesheet = qtvsc.load_stylesheet(qtvsc.Theme.LIGHT_VS)
        
        self.window.setStyleSheet(stylesheet)
        self.settings_frame.setStyleSheet("QFrame {border: 0px solid dimgrey;}")    
    
    def __retranslateUi(self, settingsDialog: QtWidgets.QDialog) -> None:
        _translate = QtCore.QCoreApplication.translate
        settingsDialog.setWindowTitle(_translate("settingsDialog", "Settings"))
        
        # Interface language select
        self.settings_language_label.setText(_translate("settingsDialog", "Interface Language"))
        self.combobox.setItemText(0, _translate("settingsDialog", "English"))
        
        # Colour mode
        self.settnigs_column_middle_label.setText(_translate("settingsDialog", "Default Colour Mode"))
        self.default_colour_mode_combo.setItemText(0, _translate("settingsDialog", "Light"))
        self.default_colour_mode_combo.setItemText(1, _translate("settingsDialog", "Dark"))
        
        # Set colour mode selection to current config value
        if self.parent.config_colour_mode.value == "dark":
            self.default_colour_mode_combo.setCurrentIndex(1)
        else:
            self.default_colour_mode_combo.setCurrentIndex(0)
        
        # Font size
        self.font_size_select_label.setText(_translate("settingsDialog", "Zoom percentage"))
        
        # Tutorial
        self.tutorial_label.setText(_translate("tutorialSetting", "Show tutorial"))
        self.__checkBoxes()
        self.__getLocations()
        
        # Set text
        self.etymology_flag_label.setText(_translate("getEtymLbl", "Show etymology"))
        self.get_usage_label.setText(_translate("getUsageLbl", "Show usage notes"))
        self.search_settings_label.setText(_translate("searchSettingsLbl", "Manual search settings"))
        self.general_settings_lbl.setText(_translate("generalSettingsLbl", "General settings"))
        self.definitions_with_conjugation_label.setText(_translate("defInConjLbl", "Definition + conjugation"))
        self.default_load_label.setText(_translate("defaultLoadLbl", "Default notes file"))
        self.default_save_label.setText(_translate("defaultSaveLbl", "Default output folder"))
        
    def _convert_zoom_level(self, zoomLevel: float) -> int:
        """Converts the zoom level from a float to an int. This is because the front-end slider only accepts ints.

        Arguments:
            zoomLevel: Zoom level currently being used

        Returns:
            Zoom level compatabile with the front-end
        """
        zoomLevel = int(zoomLevel* 100)
        return zoomLevel
    
    def __handleApplySettings(self) -> None:
        """Applies the selected language by updating the parent's language variable and then closes the dialog.
        """
        # Get settings variables
        newZoomFactor   = self.font_size_select.value()
        newColourSelect = self.default_colour_mode_combo.currentText()
        newColourSelect = newColourSelect.lower()
        
        self._apply_checks()
        self._apply_file_locations()
        self.parent.apply_settings(newZoomFactor, newColourSelect)
        self.window.close()
    
    def __checkBoxes(self) -> None:
        """Sets the checkboxes to the current config values.
        """
        if self.parent.show_tutorial_on_startup == True:
            self.tutorial_checkbox.setChecked(True)
        else:
            self.tutorial_checkbox.setChecked(False)
        
        if self.parent.get_etymology_flag == True:
            self.etymology_checkbox.setChecked(True)
        else:
            self.etymology_checkbox.setChecked(False)
        
        if self.parent.get_usage_flag == True:
            self.usage_flag_checkbox.setChecked(True)
        else:
            self.usage_flag_checkbox.setChecked(False)
            
        if self.parent.display_definitions_with_conjugations == True:
            self.definitions_with_conjugations_flag_checkbox.setChecked(True)
        else:
            self.definitions_with_conjugations_flag_checkbox.setChecked(False)
    
    def _apply_checks(self) -> None:
        """Updates the parent's variables according to the checkbox values.
        """
        if self.tutorial_checkbox.isChecked():
            self.parent.show_tutorial_on_startup = True
        else:
            self.parent.show_tutorial_on_startup = False
            
        if self.etymology_checkbox.isChecked():
            self.parent.get_etymology_flag = True
        else:
            self.parent.get_etymology_flag = False
            
        if self.usage_flag_checkbox.isChecked():
            self.parent.get_usage_flag     = True
        else:
            self.parent.get_usage_flag     = False
            
        if self.definitions_with_conjugations_flag_checkbox.isChecked():
            self.parent.display_definitions_with_conjugations    = True
        else:
            self.parent.display_definitions_with_conjugations    = False
    
    def _apply_file_locations(self) -> None:
        """Updates the parent's default load and save paths.
        """
        self.parent.default_notes_file_location = self.default_load_edit.text()
        self.parent.default_autoanki_output_folder = self.default_save_edit.text()
        
    def __getLocations(self) -> None:
        """Sets the default load and save paths to the current config values.
        """
        self.default_load_edit.setText(self.parent.default_notes_file_location)
        self.default_save_edit.setText(self.parent.default_autoanki_output_folder)