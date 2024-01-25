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
    self.mainWindow = MainWindow
    MainWindow.setObjectName("MainWindow")
    MainWindow.resize(900, 718)
    self.mainWindowLayout = QtWidgets.QGridLayout   (MainWindow)
    self.mainWindowLayout.setObjectName             ("mainWindowLayout")
    
    # Parent frame
    self.mainFrame = QtWidgets.QFrame               (MainWindow)
    self.mainFrame.setFrameShape                    (QtWidgets.QFrame.StyledPanel)
    self.mainFrame.setFrameShadow                   (QtWidgets.QFrame.Raised)
    self.mainFrame.setObjectName                    ("mainFrame")
    
    # Parent layout
    self.mainLayout = QtWidgets.QGridLayout         (self.mainFrame)
    self.mainLayout.setHorizontalSpacing            (12)
    self.mainLayout.setVerticalSpacing              (4)
    self.mainLayout.setObjectName                   ("mainLayout")
    
    # == Sidebar == 
    # Frame
    self.sidebarFrame = QtWidgets.QFrame            (self.mainFrame)
    self.sidebarFrame.setMaximumSize                (QtCore.QSize(410, 16777215))
    self.sidebarFrame.setFrameShape                 (QtWidgets.QFrame.Box)
    self.sidebarFrame.setFrameShadow                (QtWidgets.QFrame.Raised)
    self.sidebarFrame.setObjectName                 ("sidebarFrame")
    # Layout
    self.sidebarLayout = QtWidgets.QGridLayout      (self.sidebarFrame)
    self.sidebarLayout.setContentsMargins           (1, -1, 0, -1)
    self.sidebarLayout.setObjectName                ("sidebarLayout")
    # Bottom frame
    self.sidebarInnerBottomFrame = QtWidgets.QFrame (self.sidebarFrame)
    self.sidebarInnerBottomFrame.setMaximumSize     (QtCore.QSize(16777215, 120))
    self.sidebarInnerBottomFrame.setFrameShape      (QtWidgets.QFrame.StyledPanel)
    self.sidebarInnerBottomFrame.setFrameShadow     (QtWidgets.QFrame.Raised)
    self.sidebarInnerBottomFrame.setObjectName      ("sidebarInnerBottomFrame")         # Remove border
    # Bottom layout
    self.sidebarBottomLayout = QtWidgets.QGridLayout(self.sidebarInnerBottomFrame)      # Remove layout
    self.sidebarBottomLayout.setObjectName          ("sidebarBottomLayout")
    self.sidebarInnerBottomFrame.setFrameShape      (QtWidgets.QFrame.NoFrame)          # Remove frame
    
    # Colour mode
    self.colourModeBtn = QtWidgets.QPushButton      (self.sidebarInnerBottomFrame)
    self.colourModeBtn.setObjectName                ("colourModeBtn")
    self.sidebarBottomLayout.addWidget              (self.colourModeBtn, 0, 0, 1, 1)
            
    # Settings
    self.settingsBtn = QtWidgets.QPushButton        (self.sidebarInnerBottomFrame)
    self.settingsBtn.setObjectName                  ("settingsBtn")
    self.sidebarBottomLayout.addWidget              (self.settingsBtn, 1, 0, 1, 1)
    self.sidebarLayout.addWidget                    (self.sidebarInnerBottomFrame, 2, 0, 1, 1)
    
    # Contact Button
    self.contactBtn = QtWidgets.QPushButton         (self.sidebarInnerBottomFrame)
    self.contactBtn.setObjectName                   ("contactBtn")
    self.sidebarBottomLayout.addWidget              (self.contactBtn, 3, 0, 1, 1)
    
    # == Top frame ==
    self.layout = QtWidgets.QVBoxLayout             (self.sidebarFrame)
    self.sidebarInnerTopFrame = QtWidgets.QFrame    (self.sidebarFrame)
    self.sidebarInnerTopFrame.setFrameShape         (QtWidgets.QFrame.StyledPanel)
    self.sidebarInnerTopFrame.setFrameShadow        (QtWidgets.QFrame.Raised)
    self.sidebarInnerTopFrame.setObjectName         ("sidebarInnerTopFrame")
    self.sidebarLayout.addWidget                    (self.sidebarInnerTopFrame, 0, 0)
    self.sidebarInnerTopFrame.setFrameShape         (QtWidgets.QFrame.NoFrame)          # Remove border
    # Layout
    self.sidebarTopLayout = QtWidgets.QGridLayout   (self.sidebarInnerTopFrame)
    self.sidebarTopLayout.setObjectName             ("sidebarTopLayout")
    
    # AutoAnki
    self.autoAnkiBtn = QtWidgets.QPushButton        (self.sidebarInnerTopFrame)
    self.autoAnkiBtn.setObjectName                  ("autoAnkiBtn")
    self.sidebarTopLayout.addWidget                 (self.autoAnkiBtn, 1, 0, 1, 0)
    
    # Search wiki
    self.line = QtWidgets.QFrame                    (self.sidebarInnerTopFrame)
    self.line.setFrameShape                         (QtWidgets.QFrame.HLine)
    self.line.setFrameShadow                        (QtWidgets.QFrame.Sunken)
    self.line.setObjectName                         ("line")
    self.sidebarTopLayout.addWidget                 (self.line, 2, 0, 1, 1)
    
    # Current lang label
    self.currentLangLabel = QtWidgets.QLabel        (self.sidebarInnerTopFrame)
    self.currentLangLabel.setObjectName             ("currentLangLabel")
    self.sidebarTopLayout.addWidget                 (self.currentLangLabel, 0, 0, 1, 0)
    font = QtGui.QFont                              ()
    font.setBold                                    (True)
    self.currentLangLabel.setFont                   (font)
    
    # Change lang
    self.changeLangBtn = QtWidgets.QPushButton      (self.sidebarInnerTopFrame)
    self.changeLangBtn.setObjectName                ("changeLangBtn")
    self.sidebarTopLayout.addWidget                 (self.changeLangBtn, 2, 0, 1, 0)
    
    # ScrollArea
    self.scrollArea = QtWidgets.QScrollArea         (self.sidebarInnerTopFrame)
    self.scrollArea.setWidgetResizable              (True)
    self.scrollAreaWidgetContents = QtWidgets.QWidget()
    self.scrollArea.setWidget                       (self.scrollAreaWidgetContents)
    self.scrollAreaLayout = QtWidgets.QGridLayout   (self.scrollAreaWidgetContents)
    self.sidebarLayout.addWidget                    (self.sidebarInnerTopFrame, 0, 0, 1, 1)
    self.mainLayout.addWidget                       (self.sidebarFrame, 0, 0, 2, 1)
    # == Saved words ==
    self.sideLabel = QtWidgets.QLabel               (self.scrollAreaWidgetContents)
    self.sideLabel.setObjectName                    ("sideLabel")
    self.scrollAreaLayout.addWidget                 (self.sideLabel, 6, 0, 1, 0)
    font = QtGui.QFont                              ()
    font.setBold                                    (True)
    self.sideLabel.setFont                          (font)
    self.line2 = QtWidgets.QFrame                   (self.scrollAreaWidgetContents)
    self.line2.setFrameShape                        (QtWidgets.QFrame.HLine)
    self.line2.setFrameShadow                       (QtWidgets.QFrame.Sunken)
    self.line2.setObjectName                        ("line2")
    self.scrollAreaLayout.addWidget                 (self.line2, 5, 0, 1, 1)
    # Button
    self.saveWord = QtWidgets.QPushButton           (self.scrollAreaWidgetContents)
    self.saveWord.setObjectName                     ("saveWord")
    self.scrollAreaLayout.addWidget                 (self.saveWord, 7, 0, 1, 0)
    self.sidebarTopLayout.addWidget                 (self.scrollArea)
    
    # == Search layout ==
    self.searchInputFrame = QtWidgets.QFrame        (self.mainFrame)
    self.searchInputFrame.setMinimumSize            (QtCore.QSize(200, 0))
    self.searchInputFrame.setMaximumSize            (QtCore.QSize(16777215, 95))
    self.searchInputFrame.setLayoutDirection        (QtCore.Qt.LeftToRight)
    self.searchInputFrame.setAutoFillBackground     (False)
    self.searchInputFrame.setFrameShape             (QtWidgets.QFrame.Box)
    self.searchInputFrame.setFrameShadow            (QtWidgets.QFrame.Raised)
    self.searchInputFrame.setObjectName             ("searchInputFrame")
    # Add border
    self.searchInputLayout = QtWidgets.QGridLayout  (self.searchInputFrame)
    self.searchInputLayout.setObjectName            ("searchInputLayout")
    # Combo box
    self.searchModeCombo = QtWidgets.QComboBox      (self.searchInputFrame)
    self.searchModeCombo.setObjectName              ("searchModeCombo")
    # Add items
    self.searchModeCombo.addItem                    ("Sentence", "sentence")
    self.searchModeCombo.addItem                    ("Conjugation", "conjugation")
    self.searchModeCombo.addItem                    ("Word", "word")
    self.searchModeCombo.setCurrentIndex            (2)                                 # Assuming "Word" is default
    self.searchInputLayout.addWidget                (self.searchModeCombo, 0, 0, 1, 1)
    # Search button
    self.searchBtn = QtWidgets.QPushButton          (self.searchInputFrame)
    self.searchInputEdit = MyLineEdit               (self.searchBtn, self)
    self.searchInputEdit.setObjectName              ("searchInputEdit")
    # Search input
    self.searchInputLayout.addWidget                (self.searchInputEdit, 0, 1, 2, 1)
    self.searchBtn.setObjectName                    ("searchBtn")
    self.searchInputLayout.addWidget                (self.searchBtn, 1, 0, 1, 1)
    
    # == Output display ==
    self.mainLayout.addWidget                       (self.searchInputFrame, 0, 1, 1, 1)
    self.outputFrame = QtWidgets.QFrame             (self.mainFrame)
    self.outputFrame.setMinimumSize                 (QtCore.QSize(0, 0))
    self.outputFrame.setMaximumSize                 (QtCore.QSize(16777215, 16777215))
    self.outputFrame.setLayoutDirection             (QtCore.Qt.LeftToRight)
    self.outputFrame.setObjectName                  ("outputFrame")
    self.outputLayout = QtWidgets.QGridLayout       (self.outputFrame)
    self.outputLayout.setObjectName                 ("outputLayout")
    # Text
    self.searchOutputBrowser = QtWebEngineWidgets.QWebEngineView(self.outputFrame)
    self.searchOutputBrowser.setZoomFactor          (1)
    sizePolicy = QtWidgets.QSizePolicy              (QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    sizePolicy.setHorizontalStretch                 (100)
    sizePolicy.setVerticalStretch                   (100)
    sizePolicy.setHeightForWidth                    (self.searchOutputBrowser.sizePolicy().hasHeightForWidth())
    self.searchOutputBrowser.setSizePolicy          (sizePolicy)
    self.searchOutputBrowser.setMaximumSize         (QtCore.QSize(16777215, 16777215))
    self.searchOutputBrowser.setObjectName          ("searchOutputBrowser")
    self.outputLayout.addWidget                     (self.searchOutputBrowser, 0, 0, 1, 1)
    self.mainLayout.addWidget                       (self.outputFrame, 1, 1, 1, 1)
    self.mainWindowLayout.addWidget                 (self.mainFrame, 0, 0, 1, 1)
    
    # Border styling        
    self.sidebarInnerBottomFrame.setStyleSheet      ("QFrame {border: 0px; margin: 0px;}")
    self.sidebarInnerTopFrame.setStyleSheet         ("QFrame {border: 0px; margin: 0px;}")
    self.searchInputFrame.setStyleSheet             ("QFrame {border: 1px solid lightgrey;}")
    self.outputFrame.setStyleSheet                  ("QFrame {border: 1px solid lightgrey;}")
    
    # Retranslate
    MainWindow.setTabOrder                          (self.searchOutputBrowser, self.changeLangBtn)
    
    # More styling
    self.sidebarFrame.setMaximumSize                (QtCore.QSize(148, 16777215))
    self.sidebarFrame.setMinimumSize                (QtCore.QSize(148, 16777215))
    self.sidebarInnerTopFrame.setMaximumSize        (QtCore.QSize(16777215, 16777215))
    self.scrollAreaWidgetContents.setLayout         (self.scrollAreaLayout)
    self.scrollAreaLayout.setAlignment              (QtCore.Qt.AlignTop)
    
    # Drop shadows
    shadow = QGraphicsDropShadowEffect              ()
    shadow.setBlurRadius                            (SHADOW_BLUR_INTENSITY)   
    shadow.setXOffset                               (0)
    shadow.setYOffset                               (0)
    shadow.setColor                                 (QColor(0, 0, 0, SHADOW_INTENSITY))  
    shadow1 = QGraphicsDropShadowEffect             ()
    shadow1.setBlurRadius                           (SHADOW_BLUR_INTENSITY)
    shadow1.setXOffset                              (0)
    shadow1.setYOffset                              (0)
    shadow1.setColor                                (QColor(0, 0, 0, SHADOW_INTENSITY))  
    shadow2 = QGraphicsDropShadowEffect             ()
    shadow2.setBlurRadius                           (SHADOW_BLUR_INTENSITY)
    shadow2.setXOffset                              (0)
    shadow2.setYOffset                              (0)
    shadow2.setColor                                (QColor(0, 0, 0, SHADOW_INTENSITY))  
    self.sidebarFrame.setGraphicsEffect             (shadow)
    self.searchInputFrame.setGraphicsEffect         (shadow1)
    

def setup_setting_dialog(self, settingsDialog) -> None:
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
    
    # 
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
    
    self.settingsBox.setObjectName("settingsBox")
    self.gridLayout_2.addWidget(self.settingsBox, 1, 0, 1, 1)


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