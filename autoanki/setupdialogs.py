from PyQt5              import QtCore, QtGui, QtWidgets
from PyQt5              import QtWidgets, QtCore, QtGui
from PyQt5              import QtWebEngineWidgets
from PyQt5.QtWidgets    import QGraphicsDropShadowEffect
from PyQt5.QtGui        import QColor
from config             import config_check
from PyQt5.QtWidgets    import QTextEdit
from PyQt5.QtCore       import Qt

SHADOW_INTENSITY = 50
SHADOW_BLUR_INTENSITY = 15


def setup_mainwindow(self, MainWindow) -> None:
    self.main_window = MainWindow
    MainWindow.setObjectName("MainWindow")
    MainWindow.resize(900, 718)
    self.main_window_layout = QtWidgets.QGridLayout     (MainWindow)
    self.main_window_layout.setObjectName               ("mainWindowLayout")
    
    # Parent frame
    self.main_frame = QtWidgets.QFrame                  (MainWindow)
    self.main_frame.setFrameShape                       (QtWidgets.QFrame.StyledPanel)
    self.main_frame.setFrameShadow                      (QtWidgets.QFrame.Raised)
    self.main_frame.setObjectName                       ("mainFrame")
    
    # Parent layout
    self.main_layout = QtWidgets.QGridLayout            (self.main_frame)
    self.main_layout.setHorizontalSpacing               (12)
    self.main_layout.setVerticalSpacing                 (4)
    self.main_layout.setObjectName                      ("mainLayout")
    
    # == Sidebar == 
    # Frame
    self.sidebar_frame = QtWidgets.QFrame               (self.main_frame)
    self.sidebar_frame.setMaximumSize                   (QtCore.QSize(410, 16777215))
    self.sidebar_frame.setFrameShape                    (QtWidgets.QFrame.Box)
    self.sidebar_frame.setFrameShadow                   (QtWidgets.QFrame.Raised)
    self.sidebar_frame.setObjectName                    ("sidebarFrame")
    # Layout
    self.sidebar_layout = QtWidgets.QGridLayout         (self.sidebar_frame)
    self.sidebar_layout.setContentsMargins              (1, -1, 0, -1)
    self.sidebar_layout.setObjectName                   ("sidebarLayout")
    # Bottom frame
    self.sidebar_inner_bottom_frame = QtWidgets.QFrame  (self.sidebar_frame)
    self.sidebar_inner_bottom_frame.setMaximumSize      (QtCore.QSize(16777215, 120))
    self.sidebar_inner_bottom_frame.setFrameShape       (QtWidgets.QFrame.StyledPanel)
    self.sidebar_inner_bottom_frame.setFrameShadow      (QtWidgets.QFrame.Raised)
    self.sidebar_inner_bottom_frame.setObjectName       ("sidebarInnerBottomFrame")         # Remove border
    # Bottom layout
    self.sidebar_bottom_layout = QtWidgets.QGridLayout  (self.sidebar_inner_bottom_frame)      # Remove layout
    self.sidebar_bottom_layout.setObjectName            ("sidebarBottomLayout")
    self.sidebar_inner_bottom_frame.setFrameShape       (QtWidgets.QFrame.NoFrame)          # Remove frame
    
    # Colour mode
    self.colour_mode_button = QtWidgets.QPushButton     (self.sidebar_inner_bottom_frame)
    self.colour_mode_button.setObjectName               ("colourModeBtn")
    self.sidebar_bottom_layout.addWidget                (self.colour_mode_button, 0, 0, 1, 1)
            
    # Settings
    self.settings_button = QtWidgets.QPushButton        (self.sidebar_inner_bottom_frame)
    self.settings_button.setObjectName                  ("settingsBtn")
    self.sidebar_bottom_layout.addWidget                (self.settings_button, 1, 0, 1, 1)
    self.sidebar_layout.addWidget                       (self.sidebar_inner_bottom_frame, 2, 0, 1, 1)
    
    # Contact Button
    self.contact_button = QtWidgets.QPushButton         (self.sidebar_inner_bottom_frame)
    self.contact_button.setObjectName                   ("contactBtn")
    self.sidebar_bottom_layout.addWidget                (self.contact_button, 3, 0, 1, 1)
    
    # == Top frame ==
    self.layout = QtWidgets.QVBoxLayout                 (self.sidebar_frame)
    self.sidebar_inner_top_frame = QtWidgets.QFrame     (self.sidebar_frame)
    self.sidebar_inner_top_frame.setFrameShape          (QtWidgets.QFrame.StyledPanel)
    self.sidebar_inner_top_frame.setFrameShadow         (QtWidgets.QFrame.Raised)
    self.sidebar_inner_top_frame.setObjectName          ("sidebarInnerTopFrame")
    self.sidebar_layout.addWidget                       (self.sidebar_inner_top_frame, 0, 0)
    self.sidebar_inner_top_frame.setFrameShape          (QtWidgets.QFrame.NoFrame)          # Remove border
    # Layout
    self.sidebar_top_layout = QtWidgets.QGridLayout     (self.sidebar_inner_top_frame)
    self.sidebar_top_layout.setObjectName               ("sidebarTopLayout")
    
    # AutoAnki
    self.autoanki_button = QtWidgets.QPushButton        (self.sidebar_inner_top_frame)
    self.autoanki_button.setObjectName                  ("autoAnkiBtn")
    self.sidebar_top_layout.addWidget                   (self.autoanki_button, 1, 0, 1, 0)
    
    # Search wiki
    self.separator_line_1 = QtWidgets.QFrame            (self.sidebar_inner_top_frame)
    self.separator_line_1.setFrameShape                 (QtWidgets.QFrame.HLine)
    self.separator_line_1.setFrameShadow                (QtWidgets.QFrame.Sunken)
    self.separator_line_1.setObjectName                 ("line")
    self.sidebar_top_layout.addWidget                   (self.separator_line_1, 2, 0, 1, 1)
    
    # Current lang label
    self.search_language_label = QtWidgets.QLabel       (self.sidebar_inner_top_frame)
    self.search_language_label.setObjectName            ("currentLangLabel")
    self.sidebar_top_layout.addWidget                   (self.search_language_label, 0, 0, 1, 0)
    font = QtGui.QFont                                  ()
    font.setBold                                        (True)
    self.search_language_label.setFont                  (font)
    
    # Change lang
    self.current_language_button = QtWidgets.QPushButton(self.sidebar_inner_top_frame)
    self.current_language_button.setObjectName          ("changeLangBtn")
    self.sidebar_top_layout.addWidget                   (self.current_language_button, 2, 0, 1, 0)
    
    # ScrollArea
    self.scroll_area = QtWidgets.QScrollArea            (self.sidebar_inner_top_frame)
    self.scroll_area.setWidgetResizable                 (True)
    self.scroll_area_widget_contents = QtWidgets.QWidget()
    self.scroll_area.setWidget                          (self.scroll_area_widget_contents)
    self.acroll_area_layout = QtWidgets.QGridLayout     (self.scroll_area_widget_contents)
    self.sidebar_layout.addWidget                       (self.sidebar_inner_top_frame, 0, 0, 1, 1)
    self.main_layout.addWidget                          (self.sidebar_frame, 0, 0, 2, 1)
    # == Saved words ==
    self.saved_words_label = QtWidgets.QLabel           (self.scroll_area_widget_contents)
    self.saved_words_label.setObjectName                ("sideLabel")
    self.acroll_area_layout.addWidget                   (self.saved_words_label, 6, 0, 1, 0)
    font = QtGui.QFont                                  ()
    font.setBold                                        (True)
    self.saved_words_label.setFont                      (font)
    self.separator_line_2 = QtWidgets.QFrame            (self.scroll_area_widget_contents)
    self.separator_line_2.setFrameShape                 (QtWidgets.QFrame.HLine)
    self.separator_line_2.setFrameShadow                (QtWidgets.QFrame.Sunken)
    self.separator_line_2.setObjectName                 ("line2")
    self.acroll_area_layout.addWidget                   (self.separator_line_2, 5, 0, 1, 1)
    # Button
    self.save_word = QtWidgets.QPushButton              (self.scroll_area_widget_contents)
    self.save_word.setObjectName                        ("saveWord")
    self.acroll_area_layout.addWidget                   (self.save_word, 7, 0, 1, 0)
    self.sidebar_top_layout.addWidget                   (self.scroll_area)
    
    # == Search layout ==
    self.search_input_frame = QtWidgets.QFrame          (self.main_frame)
    self.search_input_frame.setMinimumSize              (QtCore.QSize(200, 0))
    self.search_input_frame.setMaximumSize              (QtCore.QSize(16777215, 95))
    self.search_input_frame.setLayoutDirection          (QtCore.Qt.LeftToRight)
    self.search_input_frame.setAutoFillBackground       (False)
    self.search_input_frame.setFrameShape               (QtWidgets.QFrame.Box)
    self.search_input_frame.setFrameShadow              (QtWidgets.QFrame.Raised)
    self.search_input_frame.setObjectName               ("searchInputFrame")
    # Add border
    self.search_input_layout = QtWidgets.QGridLayout    (self.search_input_frame)
    self.search_input_layout.setObjectName              ("searchInputLayout")
    # Combo box
    self.search_mode_combo = QtWidgets.QComboBox        (self.search_input_frame)
    self.search_mode_combo.setObjectName                ("searchModeCombo")
    # Add items
    self.search_mode_combo.addItem                      ("Sentence", "sentence")
    self.search_mode_combo.addItem                      ("Conjugation", "conjugation")
    self.search_mode_combo.addItem                      ("Word", "word")
    self.search_mode_combo.setCurrentIndex              (2)                                 # Assuming "Word" is default
    self.search_input_layout.addWidget                  (self.search_mode_combo, 0, 0, 1, 1)
    # Search button
    self.search_button = QtWidgets.QPushButton          (self.search_input_frame)
    self.search_input_field = MyLineEdit                (self.search_button, self)
    self.search_input_field.setObjectName               ("searchInputEdit")
    # Search input
    self.search_input_layout.addWidget                  (self.search_input_field, 0, 1, 2, 1)
    self.search_button.setObjectName                    ("searchBtn")
    self.search_input_layout.addWidget                  (self.search_button, 1, 0, 1, 1)
    
    # == Output display ==
    self.main_layout.addWidget                          (self.search_input_frame, 0, 1, 1, 1)
    self.output_frame = QtWidgets.QFrame                (self.main_frame)
    self.output_frame.setMinimumSize                    (QtCore.QSize(0, 0))
    self.output_frame.setMaximumSize                    (QtCore.QSize(16777215, 16777215))
    self.output_frame.setLayoutDirection                (QtCore.Qt.LeftToRight)
    self.output_frame.setObjectName                     ("outputFrame")
    self.output_layout = QtWidgets.QGridLayout          (self.output_frame)
    self.output_layout.setObjectName                    ("outputLayout")
    # Text
    self.search_html_browser = QtWebEngineWidgets.QWebEngineView(self.output_frame)
    self.search_html_browser.setZoomFactor              (1)
    size_policy = QtWidgets.QSizePolicy                 (QtWidgets.QSizePolicy.Expanding, 
                                                            QtWidgets.QSizePolicy.Expanding)
    size_policy.setHorizontalStretch                    (100)
    size_policy.setVerticalStretch                      (100)
    size_policy.setHeightForWidth                       (self.search_html_browser.sizePolicy().hasHeightForWidth())
    self.search_html_browser.setSizePolicy              (size_policy)
    self.search_html_browser.setMaximumSize             (QtCore.QSize(16777215, 16777215))
    self.search_html_browser.setObjectName              ("searchOutputBrowser")
    self.output_layout.addWidget                        (self.search_html_browser, 0, 0, 1, 1)
    self.main_layout.addWidget                          (self.output_frame, 1, 1, 1, 1)
    self.main_window_layout.addWidget                   (self.main_frame, 0, 0, 1, 1)
    
    # Border styling        
    self.sidebar_inner_bottom_frame.setStyleSheet       ("QFrame {border: 0px; margin: 0px;}")
    self.sidebar_inner_top_frame.setStyleSheet          ("QFrame {border: 0px; margin: 0px;}")
    self.search_input_frame.setStyleSheet               ("QFrame {border: 1px solid lightgrey;}")
    self.output_frame.setStyleSheet                     ("QFrame {border: 1px solid lightgrey;}")
    
    # Retranslate
    MainWindow.setTabOrder                              (self.search_html_browser, self.current_language_button)
    
    # More styling
    self.sidebar_frame.setMaximumSize                   (QtCore.QSize(148, 16777215))
    self.sidebar_frame.setMinimumSize                   (QtCore.QSize(148, 16777215))
    self.sidebar_inner_top_frame.setMaximumSize         (QtCore.QSize(16777215, 16777215))
    self.scroll_area_widget_contents.setLayout          (self.acroll_area_layout)
    self.acroll_area_layout.setAlignment                (QtCore.Qt.AlignTop)
    
    # Drop shadows
    shadow = QGraphicsDropShadowEffect                  ()
    shadow.setBlurRadius                                (SHADOW_BLUR_INTENSITY)   
    shadow.setXOffset                                   (0)
    shadow.setYOffset                                   (0)
    shadow.setColor                                     (QColor(0, 0, 0, SHADOW_INTENSITY))  
    shadow1 = QGraphicsDropShadowEffect                 ()
    shadow1.setBlurRadius                               (SHADOW_BLUR_INTENSITY)
    shadow1.setXOffset                                  (0)
    shadow1.setYOffset                                  (0)
    shadow1.setColor                                    (QColor(0, 0, 0, SHADOW_INTENSITY))  
    shadow2 = QGraphicsDropShadowEffect                 ()
    shadow2.setBlurRadius                               (SHADOW_BLUR_INTENSITY)
    shadow2.setXOffset                                  (0)
    shadow2.setYOffset                                  (0)
    shadow2.setColor                                    (QColor(0, 0, 0, SHADOW_INTENSITY))  
    self.sidebar_frame.setGraphicsEffect                (shadow)
    self.search_input_frame.setGraphicsEffect           (shadow1)
    

def setup_settings_dialog(self, settingsDialog) -> None:
    settingsDialog.setObjectName("settingsDialog")
    settingsDialog.resize(308, 143)
    self.grid_layout_2 = QtWidgets.QGridLayout(settingsDialog)
    self.grid_layout_2.setObjectName("gridLayout_2")
    self.settings_frame = QtWidgets.QFrame(settingsDialog)
    self.settings_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
    self.settings_frame.setFrameShadow(QtWidgets.QFrame.Raised)
    self.settings_frame.setObjectName("settingsFrame")
    self.grid_layout = QtWidgets.QGridLayout(self.settings_frame)
    self.grid_layout.setObjectName("gridLayout")
    
    # Header preset
    header_font = QtGui.QFont()
    header_font.setBold(True)
    
    # First header
    self.general_settings_lbl = QtWidgets.QLabel(self.settings_frame)
    self.general_settings_lbl.setObjectName("generalSettingsLbl")
    self.general_settings_lbl.setContentsMargins(0, 0, 0, 0)
    self.general_settings_lbl.setFont(header_font)
    self.grid_layout.addWidget(self.general_settings_lbl, 0, 0, 1, 1)
    
    # Interface language
    self.settings_language_label = QtWidgets.QLabel(self.settings_frame)
    self.settings_language_label.setObjectName("settingsLangLbl")
    self.grid_layout.addWidget(self.settings_language_label, 1, 0, 1, 1)
    self.combobox = QtWidgets.QComboBox(self.settings_frame)
    self.combobox.setMaximumSize(QtCore.QSize(130, 16777215))
    self.combobox.setObjectName("interfaceLangCB")
    self.combobox.addItem("")
    self.grid_layout.addWidget(self.combobox, 1, 1, 1, 1)
    
    # Colour mode
    self.settnigs_column_middle_label = QtWidgets.QLabel(self.settings_frame)
    self.settnigs_column_middle_label.setObjectName("settingsColMdLbl")
    self.grid_layout.addWidget(self.settnigs_column_middle_label, 2, 0, 1, 1)
    self.default_colour_mode_combo = QtWidgets.QComboBox(self.settings_frame)
    self.default_colour_mode_combo.setMaximumSize(QtCore.QSize(130, 16777215))
    self.default_colour_mode_combo.setObjectName("defaultColourModeCB")
    self.default_colour_mode_combo.addItem("")
    self.default_colour_mode_combo.addItem("")
    self.grid_layout.addWidget(self.default_colour_mode_combo, 2, 1, 1, 1)
    
    # Font size
    self.font_size_select_label = QtWidgets.QLabel(self.settings_frame)
    self.font_size_select_label.setObjectName("fontSizeSelectLbl")
    self.grid_layout.addWidget(self.font_size_select_label, 3, 0, 1, 1)
    self.font_size_select = QtWidgets.QSpinBox(self.settings_frame)
    self.font_size_select.setMinimum(25)
    self.font_size_select.setMaximum(500)
    self.font_size_select.setMaximumSize(QtCore.QSize(130, 16777215))
    self.font_size_select.setObjectName("fontSizeSelect")
    
    # 
    self.grid_layout.addWidget(self.font_size_select, 3, 1, 1, 1)
    
    # Default load location
    self.default_load_label = QtWidgets.QLabel(self.settings_frame)
    self.default_load_label.setObjectName("defaultLoadLbl")
    self.grid_layout.addWidget(self.default_load_label, 4, 0, 1, 1)
    self.default_load_edit = QtWidgets.QLineEdit(self.settings_frame)
    self.grid_layout.addWidget(self.default_load_edit, 4, 1, 1, 1)
    
    # Default save location 
    self.default_save_label = QtWidgets.QLabel(self.settings_frame)
    self.default_save_label.setObjectName("defaultSaveLbl")
    self.grid_layout.addWidget(self.default_save_label, 5, 0, 1, 1)
    self.default_save_edit = QtWidgets.QLineEdit(self.settings_frame)
    self.grid_layout.addWidget(self.default_save_edit, 5, 1, 1, 1)
    
    # Tutorial settings
    self.tutorial_label = QtWidgets.QLabel(self.settings_frame)
    self.tutorial_label.setObjectName("tutorialLbl")
    self.grid_layout.addWidget(self.tutorial_label, 6, 0, 1, 1)
    self.tutorial_checkbox = QtWidgets.QCheckBox(self.settings_frame)
    self.grid_layout.addWidget(self.tutorial_checkbox, 6, 1, 1, 1)
    
    # Additional search settings
    self.search_settings_label = QtWidgets.QLabel(self.settings_frame)
    self.search_settings_label.setObjectName("searchSettingsLbl")
    self.search_settings_label.setContentsMargins(0, 20, 0, 0)
    self.search_settings_label.setFont(header_font)
    self.grid_layout.addWidget(self.search_settings_label, 7, 0, 1, 1)
    
    # Etymology
    self.etymology_flag_label = QtWidgets.QLabel(self.settings_frame)
    self.etymology_flag_label.setObjectName("getEtymLbl")
    self.grid_layout.addWidget(self.etymology_flag_label, 8, 0, 1, 1)
    self.etymology_checkbox = QtWidgets.QCheckBox(self.settings_frame)
    self.grid_layout.addWidget(self.etymology_checkbox, 8, 1, 1, 1)
        
    # Usage notes
    self.get_usage_label = QtWidgets.QLabel(self.settings_frame)
    self.get_usage_label.setObjectName("getUsageLbl")
    self.grid_layout.addWidget(self.get_usage_label, 9, 0, 1, 1)
    self.usage_flag_checkbox = QtWidgets.QCheckBox(self.settings_frame)
    self.grid_layout.addWidget(self.usage_flag_checkbox, 9, 1, 1, 1)
    
    # Bold key term in definition
    self.definitions_with_conjugation_label = QtWidgets.QLabel(self.settings_frame)
    self.definitions_with_conjugation_label.setObjectName("defInConjLbl")
    self.grid_layout.addWidget(self.definitions_with_conjugation_label, 10, 0, 1, 1)
    self.definitions_with_conjugations_flag_checkbox = QtWidgets.QCheckBox(self.settings_frame)
    self.grid_layout.addWidget(self.definitions_with_conjugations_flag_checkbox, 10, 1, 1, 1)
    
    # Apply layout
    self.grid_layout_2.addWidget(self.settings_frame, 0, 0, 1, 1)
    
    # Confirmation buttons
    self.settings_frame = QtWidgets.QDialogButtonBox(settingsDialog)
    self.settings_frame.setOrientation(QtCore.Qt.Horizontal)
    self.settings_frame.setStandardButtons(QtWidgets.QDialogButtonBox.Apply)
    
    self.settings_frame.setObjectName("settingsBox")
    self.grid_layout_2.addWidget(self.settings_frame, 1, 0, 1, 1)


def setup_tutorial_dialog(self, Dialog) -> None:
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


def setup_guiaa_dialog(self, Dialog) -> None:
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


def setup_contact_dialog(self, Dialog: QtWidgets.QDialog) -> None:
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


def setup_changelang_dialog(self, changeLangWindow: QtWidgets.QDialog) -> None:
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
    self.changeLangConf.setCenterButtons(True)
    self.changeLangConf.setObjectName("changeLangConf")


class MyLineEdit(QTextEdit):
    """Custom Text Edit needed to handle enter key presses.
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