from PyQt5.QtWidgets    import QWidget
from PyQt5.QtCore       import Qt
from PyQt5              import (QtCore, QtWidgets)
from settingsdialog     import GuiSettingsDialog
from otherdialogs       import (GuiContactDialog, GuiChangeLangWindow, GuiAA, TutorialDialog)
from config             import config_check
from callapi            import (get_conjugation_table)
from makecards          import make_cards
from htmlstrings        import (LIGHT_HTML, DARK_HTML)
from setupdialogs       import setup_mainwindow
from savefiles          import (EncodedSavefilesContent, UnencodedSavefilesContent, encode_savefiles_content, 
                                decode_savefiles_content,encode_single_entry)
from dataclasses        import (dataclass, asdict)
from typing             import (Union, List, Dict, Tuple)
from manualsearchdb     import (ItemDefinitions, SearchType, ManualSearchItem)
from manualsearch       import (wrap_html, construct_mansearch_defs, construct_conj_table_html)
from callapi            import (get_conjugation_table, get_definitions)
from typing_extensions  import (TypedDict, NotRequired)
from enum               import Enum
import qtvscodestyle    as qtvsc
import uuid
import re
import configparser
import time
import os


QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

STYLESHEET = qtvsc.load_stylesheet(qtvsc.Theme.LIGHT_VS)
STYLESHEET_DRK = qtvsc.load_stylesheet(qtvsc.Theme.DARK_VS)

SAVEFILE_SEPERATOR = "\n====================================\n"

LANG_CODE_REF = {
    "English" : "en",
    "French"  : "fr",
    "German"  : "de",
    "Spanish" : "es",
    "Latin"   : "la"
}

uid = str
sidebarUnwrappedHtml = str


class SavedSidebarItems(TypedDict):
    English: Dict[uid, sidebarUnwrappedHtml]
    French : Dict[uid, sidebarUnwrappedHtml]
    German : Dict[uid, sidebarUnwrappedHtml]
    Spanish: Dict[uid, sidebarUnwrappedHtml]
    Latin  : Dict[uid, sidebarUnwrappedHtml]


class ManualSearchModes(Enum):
    WORD = "word"
    CONJUGATION = "conjugation"
    PHRASE = "phrase"


class ColourModes(Enum):
    DARK = "dark"
    LIGHT = "light"


class MainWindowGui(QWidget):
    
    def __init__(self, parent=None) -> None:
        super(MainWindowGui, self).__init__()
        
        # Class variables
        self.manual_search_mode                   : ManualSearchModes = ManualSearchModes.WORD
        
        # Saved items
        self.displaying_savable_item              : bool              = False
        self.saved_sidebar_items                  : SavedSidebarItems = SavedSidebarItems(
            English= {}, French= {}, German= {}, Spanish= {}, Latin= {}
        )
        
        # Temp data
        self.most_recent_search_item              : ManualSearchItem  = ManualSearchItem(
            str(), tuple(), SearchType.WORD, False, False)
        self.current_unwrapped_html               : str               = str()
        self.notes_file_content                   : str
        self.notes_input_filepath                 : str
        
        # Config variables
        self.colour_mode                          : ColourModes       = ColourModes.LIGHT
        self.config_colour_mode                   : ColourModes       = ColourModes.LIGHT
        self.show_tutorial_on_startup             : bool              = True
        self.display_definitions_with_conjugations: bool              = False
        self.get_etymology_flag                   : bool              = False
        self.get_usage_flag                       : bool              = False
        self.zoom_factor                          : float
        self.default_notes_file_location          : str
        self.default_autoanki_output_folder       : str
        self.interface_language                   : str
        self.selected_search_language             : str
            
    def setupUI(self, MainWindow: QtWidgets.QMainWindow) -> None:
        setup_mainwindow(self, MainWindow)

        # Connect buttons
        self.colour_mode_button.clicked.connect(self._toggle_colour_mode)
        self.settings_button.clicked.connect(self._spawn_settings_dialog)
        self.contact_button.clicked.connect(self.__spawnContactDialog)
        self.autoanki_button.clicked.connect(self.__spawnAutoAnkiDialog)
        self.current_language_button.clicked.connect(self._spawn_language_dialog)
        self.save_word.clicked.connect(self._save_to_sidebar)
        self.search_button.clicked.connect(self._manual_wiktionary_search)
        self.search_mode_combo.currentIndexChanged.connect(self._on_change_of_search_mode)

        # Initialise html output display
        html_content = wrap_html()
        self.search_html_browser.setHtml(html_content)
        
        # Initialise config
        config_data = config_check()
        self._apply_config_data(config_data)
        
        # Retranslate
        self._retranslate_ui(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
        # Apply colour mode on startup
        if self.colour_mode.value == "dark":
            self._activate_dark_mode()
            self._update_html_display()
        else:
            self._activate_light_mode()
        self._toggle_savebutton_enabled() # Save button should be disabled at startup
        
        # Load saves words
        raw_sidebar_items_data  = self._get_saved_items_data()
        saved_sidebar_items: SavedSidebarItems = self._parse_saved_items_data(raw_sidebar_items_data)
        
        for savebar_item_index, sidebar_id_content_pair in enumerate(
                saved_sidebar_items[self.selected_search_language].items()):
            self._construct_sidebar_item_data(sidebar_id_content_pair, savebar_item_index)
    
    def _retranslate_ui(self, MainWindow: QtWidgets.QMainWindow) -> None:
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "AutoAnki"))
        
        # Buttons
        self.save_word.setText(_translate("MainWindow",      "Add"))
        self.colour_mode_button.setText(_translate("MainWindow", "Dark   Mode"))
        self.settings_button.setText(_translate("MainWindow",   "Settings"))
        self.autoanki_button.setText(_translate("MainWindow",   "AutoAnki"))
        self.current_language_button.setText(_translate("MainWindow", "Change Language"))
        self.search_button.setText(_translate("MainWindow",     "Search"))
        self.contact_button.setText(_translate("MainWindow",    "Contact"))
        
        # Labels
        self.saved_words_label.setText(_translate("MainWindow", "Saved Words"))
        self.saved_words_label.setAlignment(Qt.AlignCenter) # type: ignore
        
        self._update_language_label(self.selected_search_language)
        self.search_language_label.setAlignment(Qt.AlignCenter) # type: ignore
    
    # ★ SETTINGS ★・・・・・・★・・・・・・★ CONFIG ★・・・・・・★・・・・・・★ LANGUAGE ★・・・・・・★・・・・・・★ CONFIG ★・・
    
    def _apply_config_data(self, configVars: list) -> None:
        """Apply config variables read from the config.ini file.
        
        Arguments:
            configVars: List of conFig variables.
        """
        # General settings
        self.interface_language   = configVars[0]
        self.selected_search_language     = configVars[1]
        
        try:
            self.colour_mode = ColourModes(configVars[2])
        except ValueError:
                print(f"Error reading config file. {configVars[2]} is not a valid colour mode.")
        
        try:
            self.config_colour_mode = ColourModes(configVars[2])
        except ValueError:
                print(f"Error reading config file. {configVars[2]} is not a valid colour mode.")
        
        self.zoom_factor                           = configVars[3]
        self.show_tutorial_on_startup              = configVars[4]
        # Search settings
        self.get_etymology_flag                    = configVars[5]
        self.get_usage_flag                        = configVars[6]
        self.display_definitions_with_conjugations = configVars[7]
        self.default_notes_file_location           = configVars[8]
        self.default_autoanki_output_folder        = configVars[9]
        # Apply config
        self._apply_zoom_factor   (self.zoom_factor)
        self._update_language_label(self.selected_search_language)
    
    def change_language(self, newLang: str) -> None:
        """Called when the user changes the search language from the languages dialog. Becuase saved sidebar items are
        specific to a language, the sidebar items need to be cleared and the relevant sidebar items need to be loaded.
        The config is also updated so that the next time the program is launched, the most recently selected search-
        language is applied. The language label is updated to reflect the new language, and the sidebar save button
        is disabled to prevent the user from saving a word in the wrong language.
        """
        # Remove all buttons from the scroll area
        self._remove_buttons()
        previous_lang = self.selected_search_language
        self.selected_search_language = newLang
        self._load_buttons()
        self.update_config()
        
        if previous_lang != newLang:
            self.displaying_savable_item = False
            self._toggle_savebutton_enabled()

    def apply_settings(self, new_zoom_factor: int, new_colour_mode: str) -> None:
        """Apply settings from the settings dialog to the main window and update the config file.

        Arguments:
            newZoomFactor: Zoom factor to be applied to the search display
            newColourMode: Light/dark mode setting to be saved to the config
        """
        self._apply_zoom_factor(new_zoom_factor)
        self.config_colour_mode = ColourModes(new_colour_mode)
        self.update_config()
    
    def update_config(self) -> None:
        """Updates the config file with current config variables.
        """
        config = configparser.ConfigParser()
        
        config['LanguagePreferences'] = {
            'InterfaceLanauge'        : self.interface_language,
            'SearchLanguage'          : self.selected_search_language
        }

        config['Interface']           = {
            'ColourMode'              : self.config_colour_mode.value,
            'ZoomLevel'               : str(int(self.zoom_factor * 100))
        }
        
        config['Behaviour']           = {
            'ShowTutorial'            : str(self.show_tutorial_on_startup)
        }
        
        config['SearchSettings']      = {
            'GetEtymology'            : str(self.get_etymology_flag),
            'GetUsage'                : str(self.get_usage_flag), 
            'defInConj'               : str(self.display_definitions_with_conjugations)
        }
        
        config['DefaultLocations']    = {
            'defaultNotesFile'        : self.default_notes_file_location,
            'defaultOutputFolder'     : self.default_autoanki_output_folder
        }
        
        with open(f"{os.path.dirname(os.getcwd())}\\autodict\\.config\\config.ini", 'w') as config_file:
            config.write(config_file)                    
        self._update_language_label(self.selected_search_language)
    
    def _update_language_label(self, language: str) -> None:
        """Update the language label and add an emoji.

        Arguments:
            language: The current language.
        """
        emoji = ""
        if language   == "French":
            emoji =  "🥖"
        elif language == "German":
            emoji =  "🥨"
        elif language == "Spanish":
            emoji =  "💃"
        elif language == "Latin": 
            emoji =  "🏺"
        elif language == "English":
            emoji =  "💂"
        self.search_language_label.setText(f"{language} {emoji}")
            
    def _apply_zoom_factor(self, new_zoom_factor: int) -> None:
        """Update the HTML display with a new zoom factor. The HTML display only accepts floats, so the value is 
        converted.
        
        Arguments:
            newZoomFactor: Zoom factor that will be applied to the HTML display after conversion.
        """
        converted_zoom_factor: float = new_zoom_factor / 100 
        self.zoom_factor = converted_zoom_factor
        self.search_html_browser.setZoomFactor(converted_zoom_factor)       
    
    def _on_change_of_search_mode(self, search_mode_combo_index: int) -> None:
        """Change the search mode when the user selects a different option from the combo box.

        Arguments:
            search_mode_combo_index: Index of the selected combo box item.
        """
        mode = self.search_mode_combo.itemData(search_mode_combo_index)
        if mode == "word":
            self.manual_search_mode = ManualSearchModes.WORD
        elif mode == "conjugation":
            self.manual_search_mode = ManualSearchModes.CONJUGATION
        elif mode == "sentence":
            self.manual_search_mode = ManualSearchModes.PHRASE
    
    def _toggle_savebutton_enabled(self) -> None:
        """Toggle the save button on/off."""
        if self.displaying_savable_item is True:
            self.save_word.setEnabled(True)
        else:
            self.save_word.setEnabled(False)
            
    # ★ THEME ★・・・・・・★・・・・・・★ THEME ★・・・・・・★・・・・・・★ THEME ★・・・・・・★・・・・・・★ THEME ★・・・・・・★
    
    def _apply_colour_mode(self):
        """Apply the current colour mode. The HTML display is updated to reflect the colour mode. The language label
        is refreshed because the emojis get crusty and weird when the colour mode changes.
        # TODO - Fix the emoji issue, they're still crusty.
        """
        if self.colour_mode.value == "light":
            self._activate_dark_mode()
        elif self.colour_mode.value == "dark":
            self._activate_light_mode()
        self._update_html_display()
        self._update_language_label(self.selected_search_language)
    
    def _toggle_colour_mode(self) -> None:
        """Toggle dark/light modes. The HTML display is updated to reflect the new colour mode. The HTML display is 
        updated to reflect the colour mode. The language label is refreshed because the emojis get crusty and weird 
        when the colour mode changes.
        # TODO - Fix the emoji issue, they're still crusty.
        """
        if self.colour_mode.value == "light":
            self._activate_dark_mode()
        elif self.colour_mode.value == "dark":
            self._activate_light_mode()
        self._update_html_display()
        self._update_language_label(self.selected_search_language)
    
    def _activate_dark_mode(self) -> None:
        """Apply dark mode. The stylesheet is updated to reflect the new colour mode. The border colours and general
        styling are updated because they differ between modes and are specific changes added on top of the stylesheet. 
        """
        stylesheet = qtvsc.load_stylesheet(qtvsc.Theme.DARK_VS)
        self.main_window.setStyleSheet(stylesheet) # type: ignore
        self.colour_mode = ColourModes.DARK
        self._reapply_border_colours()
        self._apply_style_edits_dark()
        self.colour_mode_button.setText("Light Mode")
    
    def _activate_light_mode(self) -> None:
        """Apply light mode. The stylesheet is updated to reflect the new colour mode. The border colours and general
        styling are updated because they differ between modes and are specific changes added on top of the stylesheet. 
        """
        stylesheet = qtvsc.load_stylesheet(qtvsc.Theme.LIGHT_VS)
        self.main_window.setStyleSheet(stylesheet) # type: ignore
        self.colour_mode = ColourModes.LIGHT
        self._reapply_border_colours()
        self._apply_style_edits_light()
        self.colour_mode_button.setText("Dark Mode")
    
    def _reapply_border_colours(self) -> None:
        """When the theme changes, the colours of the border frames reset. These colours need to be reapplied."""
        if self.colour_mode.value == "dark":
            self.sidebar_frame.setStyleSheet     ("QFrame {border: 1px solid dimgrey;}")
            self.search_input_frame.setStyleSheet ("QFrame {border: 1px solid dimgrey;}")
            self.output_frame.setStyleSheet      ("QFrame {border: 1px solid dimgrey;margin-top: 5px;}")
        else:
            self.sidebar_frame.setStyleSheet     ("QFrame {border: 1px solid lightgrey;}")
            self.search_input_frame.setStyleSheet ("QFrame {border: 1px solid lightgrey;}")
            self.output_frame.setStyleSheet      ("QFrame {border: 1px solid lightgrey;margin-top: 5px;}")
    
    def _apply_style_edits_light(self) -> None:
        """Styling changes (border radius, colours, etc.) applied on top of the current theme."""
        self.sidebar_frame.setStyleSheet(LIGHT_HTML[0])
        self.search_input_frame.setStyleSheet(LIGHT_HTML[1])
        self.output_frame.setStyleSheet(LIGHT_HTML[2])
        
        self.scroll_area_widget_contents.setObjectName("scrollAreaWidgetContents")
        self.acroll_area_layout.setObjectName("scrollAreaLayout")
        self.scroll_area_widget_contents.setStyleSheet(LIGHT_HTML[3])
        
        self.search_input_field.setStyleSheet(LIGHT_HTML[4])
        self.main_frame.setStyleSheet(LIGHT_HTML[5])
        self.save_word.setStyleSheet(LIGHT_HTML[6])
        
    def _apply_style_edits_dark(self) -> None:
        """Styling changes (border radius, colours, etc.) applied on top of the current theme.
        """
        self.sidebar_frame.setStyleSheet(DARK_HTML[0])
        self.search_input_frame.setStyleSheet(DARK_HTML[1])
        self.output_frame.setStyleSheet(DARK_HTML[2])  
        
        self.scroll_area_widget_contents.setObjectName("scrollAreaWidgetContents")
        self.acroll_area_layout.setObjectName("scrollAreaLayout")
        self.scroll_area_widget_contents.setStyleSheet(DARK_HTML[3])   
        
        self.search_input_field.setStyleSheet(DARK_HTML[4])  
        self.main_frame.setStyleSheet(DARK_HTML[5])
        self.save_word.setStyleSheet(DARK_HTML[6])

    # ★ AUTO ANKI ★・・・・・・★・・・・・・★ AUTO ANKI ★・・・・・・★・・・・・・★ AUTO ANKI ★・・・・・・★・・・・・・★ AUTO 
    
    def make_cards(self, deckName: str, messageQueue, savePth: str) -> None:
        """Make Anki cards from the user-selected text file.
        
        Arguments:
            deckName: Name used in the Anki input field and used to name the output file
            messageQueue: Message queue used to report progress to the user
            savePth: Path for the output file
        """
        make_cards(self.notes_input_filepath, self.selected_search_language, deckName, messageQueue, savePth)
    
    # ★ MANUAL SEARCH ★・・・・・・★・・・・・・★ MANUAL SEARCH ★・・・・・・★・・・・・・★ MANUAL SEARCH ★・・・・・・★・・・・ 
    
    def _manual_wiktionary_search(self) -> None:
        """Search Wiktionary for a word, phrase, or conjugation table. Three types of searches can be done: word,
        conjugation, or phrase. The search type is determined by the combo box. This search type is then converted
        to a more specific search type that considers whether the user wants to search for not only a conjugation
        (if they are searching for a conjugation), but a combination of the two. These definitions are then cleaned
        to remove visually confusing elements, and the HTML is then finally constructed according to the colour mode.
        This completed HTML string is then sent to the HTML display and viewed by the user. 
        
        The unwrapped HTML is stored in a temp variable, so that if the user changes colour mode while viewing the
        result, the header and footer can be added to the retrieved HTML according to colour mode.
        
        Calling this function enables the save button, which allows the user to save the current search to the sidebar.
        """        
        selected_search_language = self.selected_search_language
        search_string = self.search_input_field.toPlainText()
        search_string = search_string.strip()
        search_tokens = tuple(search_string.split())
        search_type = self._get_search_term()
        etymology_flag = self.get_etymology_flag
        get_usage_flag = self.get_usage_flag
        
        manual_search_item = ManualSearchItem(selected_search_language, search_tokens, search_type, etymology_flag,
            get_usage_flag)
        
        manual_search_item, search_successful = self._construct_unwrapped_html(manual_search_item)
        if not search_successful:
            unwrapped_html = "<h3>Search failed</h3>"
        else:
            unwrapped_html = manual_search_item.unwrapped_html_construct
        
        self.most_recent_search_item = manual_search_item
        self.current_unwrapped_html = unwrapped_html
        self._update_html_display()
        self.displaying_savable_item = True
        self._toggle_savebutton_enabled()

    def _get_search_term(self) -> SearchType:
        """Convert the combo box's search mode to a more specific search type that considers whether the user
        wants to search for not only a conjugation, but a combination of the two.

        Returns:
            SearchType used to determine the type of search to be performed by the API call.
        """
        if self.manual_search_mode == ManualSearchModes.CONJUGATION and self.display_definitions_with_conjugations:
            search_type = SearchType.WORD_CONJ_COMBO
        elif self.manual_search_mode == ManualSearchModes.CONJUGATION:
            search_type = SearchType.CONJUGATION
        elif self.manual_search_mode == ManualSearchModes.WORD:
            search_type = SearchType.WORD
        else:
            search_type = SearchType.PHRASE
        return search_type

    def _construct_unwrapped_html(self, manual_search_item: ManualSearchItem) -> Tuple[ManualSearchItem, bool]:
        """Wrapper function to construct the HTML that will be displayed to the user. The HTML is constructed 
        differently depending on the type of search.

        Arguments:
            manual_search_item: ManualSearchItem object containing the search term and all other information gathered.

        Returns:
            ManualSearchItem: Object containing all relevant information about the completed search. 
            bool - Whether the search was successful.
        """
        if manual_search_item.search_type.name == "WORD":
            manual_search_item, search_successful = self._manual_word_search(manual_search_item)
        
        elif (manual_search_item.search_type.name == "CONJUGATION" or 
                manual_search_item.search_type.name == "WORD_CONJ_COMBO"):            
            manual_search_item, search_successful = self._manual_conjugation_search(manual_search_item)

        else: # Phrase search/catchall
            manual_search_item, search_successful = self._manual_phrase_search(manual_search_item)
        
        return manual_search_item, search_successful

    def _manual_word_search(self, manual_search_item: ManualSearchItem) -> Tuple[ManualSearchItem, bool]:
        """Search Wiktionary for a word. If the search is successful, the HTML is constructed (without the header and 
        footer) and added to the ManualSearchItem object. The HTML is stored in the unwrapped_html_construct attribute,
        which does not contain the HTML header and footer, which is later added according to the colour mode.

        Arguments:
            manual_search_item: ManualSearchItem object containing the search term and all other information gathered.

        Returns:
            ManualSearchItem: Object containing all relevant information about the completed search. 
            bool - Whether the search was successful.
        """
        unwrapped_html_construct = ""
        for token_i, search_token in enumerate(manual_search_item.search_tokens):
            
            definitions_data = get_definitions(search_token, manual_search_item.search_language, 
                manual_search_item.etymology_flag, manual_search_item.usage_notes_flag)       
            if definitions_data == None:
                return manual_search_item, False
            
            if token_i > 0:
                unwrapped_html_construct += "<hr>"
            unwrapped_html_construct += construct_mansearch_defs(definitions_data, search_token)
        
        manual_search_item.add_unwrapped_html(unwrapped_html_construct)
        return manual_search_item, True
    
    def _manual_conjugation_search(self, manual_search_item: ManualSearchItem) -> Tuple[ManualSearchItem, bool]:
        """Search Wiktionary for a conjugation table. If the user has selected to display definitions with the
        conjugation table, the definitions are also retrieved and added to the ManualSearchItem object.

        Arguments:
            manual_search_item: ManualSearchItem object containing the search term and all other information gathered.

        Returns:
            ManualSearchItem: Object containing all relevant information about the completed search. 
            bool - Whether the search was successful.
        """
        table_data = get_conjugation_table(manual_search_item.search_tokens[0], manual_search_item.search_language) 
        if table_data == None:
            return manual_search_item, False
        manual_search_item.add_raw_table(table_data)
        
        if manual_search_item.search_type.name == "WORD_CONJ_COMBO":
            definitions_data = get_definitions(manual_search_item.search_tokens[0], manual_search_item.search_language,
                manual_search_item.etymology_flag, manual_search_item.usage_notes_flag)
            if definitions_data == None:
                return manual_search_item, False
            manual_search_item.add_raw_defs(definitions_data)
        else:
            manual_search_item.add_raw_defs(ItemDefinitions())
        
        unwrapped_html = construct_conj_table_html(manual_search_item.raw_html_table, 
            manual_search_item.search_tokens[0], manual_search_item.search_type, manual_search_item.raw_definitions)
        manual_search_item.add_unwrapped_html(unwrapped_html)
        
        return manual_search_item, True
    
    def _manual_phrase_search(self, manual_search_item: ManualSearchItem) -> Tuple[ManualSearchItem, bool]:
        """Search Wiktionary for a phrase. If the search is successful, the HTML is constructed (without the header and
        footer) and added to the ManualSearchItem object. The HTML is stored in the unwrapped_html_construct attribute,
        which does not contain the HTML header and footer, which is later added according to the colour mode.

        Arguments:
            manual_search_item: ManualSearchItem object containing the search term and all other information gathered.

        Returns:
            ManualSearchItem: Object containing all relevant information about the completed search. 
            bool - Whether the search was successful.
        """
        definitions_data = get_definitions(manual_search_item.search_tokens[0], manual_search_item.search_language, 
            manual_search_item.etymology_flag, manual_search_item.usage_notes_flag)
        if definitions_data == None:
                return manual_search_item, False
        manual_search_item.add_raw_defs(definitions_data)
        
        unwrapped_html_construct = construct_mansearch_defs(manual_search_item.raw_definitions, 
            manual_search_item.search_tokens[0])
        manual_search_item.add_unwrapped_html(unwrapped_html_construct)
        
        return manual_search_item, True
    
    def _update_html_display(self) -> None:
        """Update the search display."""
        constructed_html = wrap_html(self.current_unwrapped_html, self.colour_mode.value)
        self.search_html_browser.setHtml(constructed_html)
    
    # ★ SAVE SIDEBAR ITEM ★・・・・・・★・・・・・・★ DELETE SIDEBAR ITEM ★・・・・・・★・・・・・・★ LOAD SIDEBAR ITEM ★・・・

    def _save_to_sidebar(self) -> None:
        """Saves a word to the sidebar. Saved words are associated with a language so that only words for the current
        language are displayed. Words are saved to a file (one file per language), and the sidebar is populated 
        with buttons that load the saved words.
        """
        # Save the word content and associate with a unique ID
        sidebar_item_uid = self.most_recent_search_item.uid
        self.saved_sidebar_items[self.selected_search_language][sidebar_item_uid] = (
            self.most_recent_search_item.unwrapped_html_construct)
        button_header = self.most_recent_search_item.search_tokens[0]
        
        # Shorten word used for the display
        if len(button_header) > 9:
            button_header = button_header[:7] + ".."
        
        # Create a new button for the sidebar
        newWordBtn = QtWidgets.QPushButton(self.sidebar_inner_top_frame)
        number     = len(self.saved_sidebar_items[self.selected_search_language])
        newWordBtn.setObjectName(f"sideButton{sidebar_item_uid}")
        self.acroll_area_layout.addWidget(newWordBtn, 7+number, 0, 1, 1)
        newWordBtn.setText(f"{button_header}")
        
        newWordBtn.clicked.connect(lambda: self._render_sidebar_item(
            self.saved_sidebar_items[self.selected_search_language][sidebar_item_uid]))
        
        # Create remove button
        newWordBtnRmv = QtWidgets.QPushButton(self.sidebar_inner_top_frame)
        newWordBtnRmv.setObjectName(f"sideButtonRmv{sidebar_item_uid}")
        self.acroll_area_layout.addWidget(newWordBtnRmv, 7+number, 1, 1, 1)
        newWordBtnRmv.setText("-")
        newWordBtnRmv.clicked.connect(lambda: self._delete_sidebar_item(sidebar_item_uid))
        
        # Save word content to file (just the HTML content, not the formatted HTML string used for display)
        self.displaying_savable_item = False
        self._toggle_savebutton_enabled()
        self._update_sidebar_savefile()
    
    def _get_saved_items_data(self) -> EncodedSavefilesContent:
        """Get the encoded save-content.
        
        Returns:
            Encoded save-content.
        """
        temp_savefiles_content = {}
        for language in self.saved_sidebar_items.keys():
            with open(f"{os.getcwd()}\\autoanki\\savefiles\\{LANG_CODE_REF[language]}-sf.dat", "r", encoding="utf-8") as f:
                savefile_content = f.read()
                f.close()
                temp_savefiles_content[language] = savefile_content
        
        return EncodedSavefilesContent(**temp_savefiles_content)
    
    def _parse_saved_items_data(self, encodedRawContent: EncodedSavefilesContent) -> SavedSidebarItems:
        """Parse the saved words file and return a list of words.
        
        Arguments:
            encodedRawContent: Encoded save-content.
            
        Returns:
            Dictionary of saved words.
        """
        unencodedRawSaveContent : UnencodedSavefilesContent = (decode_savefiles_content(encodedRawContent))
        
        for language, savedContent in asdict(unencodedRawSaveContent).items():
            savedItems = savedContent.split(SAVEFILE_SEPERATOR)
            savedItems.pop() # Remove the last entry (it is empty).
            
            for item in savedItems:
                uniqueId = str(uuid.uuid1(node=None, clock_seq=None))
                self.saved_sidebar_items[language][uniqueId] = item
            
        return self.saved_sidebar_items
    
    def _construct_sidebar_item_data(self, id_word_pair: tuple, count) -> None:
        """Generate the saved words buttons for the sidebar.
        
        Arguments:
            id_word_pair: Tuple containing unique ID and word content.
            count: Number of words already saved.
        """
        if id_word_pair[1] == "":
            return
        
        # Create a new button for the sidebar
        new_sidebar_button = QtWidgets.QPushButton(self.sidebar_inner_top_frame)
        new_sidebar_button.setObjectName(f"sideButton{id_word_pair[0]}")
        self.acroll_area_layout.addWidget(new_sidebar_button, 8+count, 0, 1, 1)

        # Create remove button
        new_sidebar_removal_button = QtWidgets.QPushButton(self.sidebar_inner_top_frame)
        new_sidebar_removal_button.setObjectName(f"sideButtonRmv{id_word_pair[0]}")
        self.acroll_area_layout.addWidget(new_sidebar_removal_button, 8+count, 1, 1, 1)
        new_sidebar_removal_button.setText("-")
        new_sidebar_removal_button.setMaximumSize(QtCore.QSize(25, 16777215))
        new_sidebar_removal_button.clicked.connect(lambda: self._delete_sidebar_item(id_word_pair[0]))

        # Finds the first header in the string and extracts the word
        header_match = re.search(r"<h3>(\w+)</h3>", id_word_pair[1])

        # Get the word, needed for the button
        if header_match == None:
            return        
        header = header_match.group(1)
        
        # Shorten the header if it is too long
        if len(header) > 9:
            header = header[:7] + ".."     
        new_sidebar_button.setText(f"{header}")

        # Determine if it's a conjugation table
        if "<table" in id_word_pair[1]:
            if len(header) > 9:
                header = header[:7] + ".."
            new_sidebar_button.setText(f"{header}") 

        # Dynamically connect button to function
        new_sidebar_button.clicked.connect(
            lambda: self._render_sidebar_item(
                self.saved_sidebar_items[self.selected_search_language][id_word_pair[0]]
            )
        )
    
    def _render_sidebar_item(self, content: str) -> None:
        """Render a sidebar item when the user clicks on a sidebar button.

        Arguments:
            content: HTML content to be rendered.
        """
        self.current_unwrapped_html = content
        self.displaying_savable_item = False
        self._toggle_savebutton_enabled()
        self._update_html_display()
    
    def _load_buttons(self) -> None:
        """Load the saved words buttons for the sidebar.
        """
        for count, id_word_pair in enumerate(self.saved_sidebar_items[self.selected_search_language].items()):
            self._construct_sidebar_item_data(id_word_pair, count)
    
    def _delete_sidebar_item(self, unique_id: str) -> None:
        """Remove a saved word by deleting its save-file content, temp dictionary entry, and sidebar buttons.
        
        Arguments:
            unique_id: Unique ID of the word to be deleted, which is linked to its sidebar buttons.
        """
        # Remove the button.
        item_button   = self.sidebar_inner_top_frame.findChild(QtWidgets.QPushButton, f"sideButton{unique_id}")
        remove_button = self.sidebar_inner_top_frame.findChild(QtWidgets.QPushButton, f"sideButtonRmv{unique_id}")
        self.acroll_area_layout.removeWidget(item_button)
        self.acroll_area_layout.removeWidget(remove_button)

        # Remove the word from the dict
        self.saved_sidebar_items[self.selected_search_language].pop(unique_id)
        self._update_sidebar_savefile()
        # Reload buttons to reorder GUI placement indices # ! this is crusty as, pls fix
        self.change_language(self.selected_search_language)
        
    def _remove_buttons(self) -> None:
        """Remove all sidebar buttons. Used to clear the sidebar when the user changes the search language before new
        buttons are rendered.
        """
        for uid in self.saved_sidebar_items[self.selected_search_language].keys():
            word_btn   = self.sidebar_inner_top_frame.findChild(QtWidgets.QPushButton, f"sideButton{uid}")
            remove_btn = self.sidebar_inner_top_frame.findChild(QtWidgets.QPushButton, f"sideButtonRmv{uid}")
            self.acroll_area_layout.removeWidget(word_btn)
            self.acroll_area_layout.removeWidget(remove_btn)
            word_btn.setParent(None)
            remove_btn.setParent(None)
    
    def _update_sidebar_savefile(self) -> None:
        """Update the saved items file with the session's saved words. Can be used to lazily update the file after
        deleting an item.
        """
        current_lang = self.selected_search_language
        temp_unwrapped_html_d = {}
        for language in self.saved_sidebar_items.keys():
            temp_unwrapped_html = ""
            for unwrapped_html in self.saved_sidebar_items[language].values():
                temp_unwrapped_html += unwrapped_html + SAVEFILE_SEPERATOR
            temp_unwrapped_html_d[language] = temp_unwrapped_html
        
        unencoded_save_data = UnencodedSavefilesContent(**temp_unwrapped_html_d)
        encoded_save_data = encode_savefiles_content(unencoded_save_data)
        
        with open(f"{os.getcwd()}\\autoanki\\savefiles\\{LANG_CODE_REF[self.selected_search_language]}-sf.dat", "w", encoding="utf-8") as f:
            f.write(asdict(encoded_save_data)[current_lang].decode("utf-8"))
            f.close()
    
    # ★ SPAWN DIALOGS ★・・・・・・★・・・・・・★ SPAWN DIALOGS ★・・・・・・★・・・・・・★ SPAWN DIALOGS ★・・・・・・★・・・・
    
    def _spawn_settings_dialog(self) -> None:
        """Bring up the settings dialog.
        """
        self.settings_dialog = QtWidgets.QDialog()
        self.settings_gui = GuiSettingsDialog(self)
        self.settings_gui.setupUi(self.settings_dialog)
        
        if self.colour_mode.value == "dark":
            self.settings_dialog.setStyleSheet(STYLESHEET_DRK)
        else:
            self.settings_dialog.setStyleSheet(STYLESHEET)
        
        self.settings_dialog.show()

    def _spawn_language_dialog(self) -> None:
        """Bring up the language selector dialog.
        """
        self.change_language_dialog = QtWidgets.QDialog()
        self.change_language_gui = GuiChangeLangWindow(self)
        self.change_language_gui.setupUi(self.change_language_dialog)
        
        if self.colour_mode.value == "dark":
            self.change_language_dialog.setStyleSheet(STYLESHEET_DRK)
        else:
            self.change_language_dialog.setStyleSheet(STYLESHEET)
        
        # print(self.most_recent_search_item)
        self.change_language_dialog.show()
        
    def __spawnContactDialog(self) -> None:
        """Bring up the contact dialog.
        """
        self.constact_dialog = QtWidgets.QDialog()
        self.contact_gui = GuiContactDialog()
        self.contact_gui.setupUi(self.constact_dialog)
        
        if self.colour_mode.value == "dark":
            self.constact_dialog.setStyleSheet(STYLESHEET_DRK)
        else:
            self.constact_dialog.setStyleSheet(STYLESHEET)
        
        self.constact_dialog.show()
        
    def __spawnAutoAnkiDialog(self) -> None:
        """Bring up the AutoAnki dialog.
        """
        self.autoanki_dialog = QtWidgets.QDialog()
        self.autoanki_gui = GuiAA(self)
        self.autoanki_gui.setupUi(self.autoanki_dialog)
        
        # Colour mode styling
        if self.colour_mode.value == "dark":
            self.autoanki_dialog.setStyleSheet(STYLESHEET_DRK)
        else:
            self.autoanki_dialog.setStyleSheet(STYLESHEET)
        
        self.autoanki_dialog.show()
        
    def spawn_tutorial_dialog(self) -> None:
        """Bring up the language selector dialog.
        """
        if self.show_tutorial_on_startup == True:
            self.windowTute = QtWidgets.QDialog()
            self.UITute = TutorialDialog(self)
            self.UITute.setupUi(self.windowTute)
            self.windowTute.show()
    
    def add_user_file(self) -> None:
        """Opens a file explorer and saves the user's file.
        """
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)
        
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            self.notes_input_filepath = filenames[0]
            f = open(filenames[0], 'r', encoding="utf-8")
            with f:
                data = f.read()
                self.notes_file_content = data