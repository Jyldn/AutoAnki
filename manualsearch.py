import uuid
import pprint
import manualsearchdb
from enum           import (Enum, Flag, auto)
from dataclasses    import (dataclass, asdict)
from typing         import (Dict, List, Tuple, Union, Optional)
from callapi        import (get_conjugation_table, strip_bs4_links)
from manualsearchdb import (ManualSearchItem, ItemDefinitions, SearchType)
from htmlstrings    import (HTML_HEADER_DARK, HTML_HEADER_DARK_CONJ, HTML_HEADER_LIGHT, HTML_FOOTER)


def construct_conj_table(table_data: str, token: str, seach_type: SearchType, definitions_data = {}) -> str:
    header = f"<h3>{token}</h3>"
    linkcleaned_table = strip_bs4_links(table_data)
    table_construct = header + linkcleaned_table
    
    if seach_type.name == "WORD_CONJ_COMBO":
        spacer_construct = f"<h3></h3>"
        table_combo_construct = table_construct + spacer_construct
        
        definitions_construct = construct_mansearch_defs(definitions_data, token, True)
        table_combo_construct += definitions_construct
        
        return table_combo_construct
    
    return table_construct


def construct_mansearch_defs(item_definitions: ItemDefinitions, search_term: str, table_called : bool=False) -> str:
    """
    """
    definitions = asdict(item_definitions)
    
    if not table_called:
        defs_string = f"<h3>{search_term}</h3>"     
    else:
        defs_string = ""
    
    for tag, definition in definitions.items():
        if definition != None:
            
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
            
            else:
                defs_string = f"<span style='color:grey;font-size:0.85em;'>{tag.capitalize()}</span>"
                defs_string += f"""<span style='color:grey;font-size:0.85em;'><ul><li>{definition[0]}
                    </li></ul><br></span>"""
    
    return defs_string


def construct_html(html_content: str="", colour_mode: str="", search_type: SearchType=SearchType.WORD) -> str:
    """Construct the HTML data for the front-end display. Appropriate headers are added depending on colour mode
    and footer.
    """
    if colour_mode == "dark":
        
        if search_type == (SearchType.WORD_CONJ_COMBO or SearchType.CONJUGATION):
            html_construct = HTML_HEADER_DARK_CONJ + html_content 
        else:
            html_construct = HTML_HEADER_DARK + html_content

    else:
        html_construct = HTML_HEADER_LIGHT + html_content
    
    html_construct += HTML_FOOTER
    return html_construct