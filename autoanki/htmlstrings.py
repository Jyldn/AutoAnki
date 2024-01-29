CONJUGATION_SEARCH_OVERLOAD_MSG = "<p>Conjugation tables can only be generated for one word at a time.</p>"

HTML_HEADER_DARK =  """
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
                        background-color: transparent !important;
                        border: 1px dotted #404040;
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

HTML_LIGHT_SIDEBAR_FRAME = """
            QFrame {
                border: 0px solid lightgrey;
                border-radius: 10px;
                background-color: #FAFAFA; } 
            """

HTML_LIGHT_SRCH_INPT_FRAME = """
            QFrame#searchInputFrame {
                border: 0px solid lightgrey;
                border-radius: 10px;
                background-color: #FAFAFA; } 
            """

HTML_LIGHT_SRCH_OUPT_FRAME = """
            QFrame {
                border: 0px solid lightgrey;
                border-radius: 10px; } 
            """

HTML_LIGHT_SCR_AREA = """
            QWidget#scrollAreaWidgetContents, QLabel {
                background-color: #FAFAFA; } 
            """

HTML_LIGHT_SRCH_INPT_AREA = """
            QTextEdit {
                border: 1px solid lightgrey;
                border-radius: 5px; }
            """

HTML_LIGHT_MAIN_FRAME = """
            QPushButton {
                border-radius: 3px;
                }
            QComboBox {
                border-radius: 3px;
                }
            QFrame {
                border: 0px; margin: 0px;
                }
            """

HTML_LIGHT_SAVE_WRD = "QPushButton {border-radius: 3px;}"

HTML_DARK_SIDEBAR_FRAME = """
            QFrame {
                border: 0px solid lightgrey;
                border-radius: 10px;
                background-color: #292929;
                    }
            """

HTML_DARK_SRCH_INPT_FRAME = """
            QFrame#searchInputFrame {
                border: 0px solid lightgrey;
                border-radius: 10px;
                background-color: #292929;
                    }
            """

HTML_DARK_SRCH_OUPT_FRAME = """
            QFrame {
                border: 0px solid lightgrey;
                border-radius: 10px;
                    }
            """

HTML_DARK_SCR_AREA = """
            QWidget#scrollAreaWidgetContents, QLabel {
                background-color: #292929; }
            """

HTML_DARK_SRCH_INPT_AREA = """
            QTextEdit {
                border: 1px solid #171717;
                border-radius: 5px; }
            """

HTML_DARK_MAIN_FRAME = """
            QPushButton {
                border-radius: 3px; }
            QComboBox {
                border-radius: 3px; }
            QFrame {
                border: 0px; margin: 0px; }
            """

HTML_DARK_SAVE_WRD = "QPushButton {border-radius: 3px;}"

LIGHT_HTML = [
    HTML_LIGHT_SIDEBAR_FRAME,
    HTML_LIGHT_SRCH_INPT_FRAME,
    HTML_LIGHT_SRCH_OUPT_FRAME,
    HTML_LIGHT_SCR_AREA,
    HTML_LIGHT_SRCH_INPT_AREA,
    HTML_LIGHT_MAIN_FRAME,
    HTML_LIGHT_SAVE_WRD
    ]

DARK_HTML = [
    HTML_DARK_SIDEBAR_FRAME,
    HTML_DARK_SRCH_INPT_FRAME,
    HTML_DARK_SRCH_OUPT_FRAME,
    HTML_DARK_SCR_AREA,
    HTML_DARK_SRCH_INPT_AREA,
    HTML_DARK_MAIN_FRAME,
    HTML_DARK_SAVE_WRD
    ]
