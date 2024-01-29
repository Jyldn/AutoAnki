import uuid
import pprint
import manualsearchdb
from enum           import (Enum, Flag, auto)
from dataclasses    import (dataclass, asdict)
from typing         import (Dict, List, Tuple, Union, Optional)
from callapi        import (get_conjugation_table, strip_bs4_links)
from manualsearchdb import (ManualSearchItem, ItemDefinitions, SearchType)
from htmlstrings    import (HTML_HEADER_DARK, HTML_HEADER_DARK_CONJ, HTML_HEADER_LIGHT, HTML_FOOTER)
from callapi        import clean_wikitext
import time


def construct_conj_table_html(table_data: str, token: str, seach_type: SearchType, 
        item_definitions: ItemDefinitions) -> str:
    """Construct the HTML data for a conjugation table (without header and footer). If the search type is for both
    a table and defintoins, as determined by the user, the definitions are also appened to the bottom of the table
    HTML construct.

    Arguments:
        table_data: Raw HTML data for the conjugation table.
        token: The word that *was* searched for.
        seach_type: Whether this *was* a conjugation or a conjugation + definitions search.
        item_definitions: The definitions for the word that *was* searched for, if applicable.

    Returns:
        HTML data for the conjugation table, with or without definitions, cleaned, but without HTML header and footer.
    """
    header            = f"<h3>{token}</h3>"
    linkcleaned_table = strip_bs4_links(table_data)
    table_construct   = header + linkcleaned_table
    
    if seach_type.name == "WORD_CONJ_COMBO":
        spacer_construct      =  f"<h3></h3>"
        table_combo_construct =  table_construct + spacer_construct
        definitions_construct =  construct_mansearch_defs(item_definitions, token, called_by_table=True)
        table_combo_construct += definitions_construct
        return table_combo_construct
    
    return table_construct


def construct_mansearch_defs(item_definitions: ItemDefinitions, search_token: str, called_by_table : bool=False) -> str:
    """Construct the HTML data for the definitions of a word/phrase. If called by the conjugation table, the header
    is omitted.

    Arguments:
        item_definitions: The definitions for the word that *was* searched for.
        search_token: The word that *was* searched for.

    Keyword Arguments:
        called_by_table: Whether this function was called by the conjugation table constructor (default: {False})

    Returns:
        HTML data for the definitions, cleaned, but without HTML header and footer.
    """    
    definitions = asdict(item_definitions)
    
    if not called_by_table:
        defs_string = f"<h3>{search_token}</h3>"     
    else:
        defs_string = ""
    
    for lexical_tag, definition_items in definitions.items():    
        if len(definition_items) < 1:
            continue
        cleaned_definitions: list = clean_wikitext(definition_items)
        if lexical_tag != "etymology" and lexical_tag != "usage":
            defs_string = construct_general_html(defs_string, lexical_tag, cleaned_definitions)
        elif lexical_tag == "etymology":
            defs_string = construct_etymology_html(cleaned_definitions[0], lexical_tag, defs_string)
        elif lexical_tag == "usage":
            defs_string = construct_usage_notes_html(cleaned_definitions[0], lexical_tag, defs_string)
        
    return defs_string


def construct_general_html(defs_string: str, lexical_tag: str, cleaned_definitions: list) -> str:
    """Construct the HTML for definitions. This excludes etymology and usage information.

    Arguments:
        defs_string: The ongoing string of definitions under construction.
        grammar_tag: The grammar tag of the definition, such as "noun", "verb", etc.
        cleaned_definitions: The cleaned definitions (each list item being a single entry/line) for the word that 
        *was* searched for.

    Returns:
        HTML definitions formatted as an ordered list.
    """
    defs_string += f"{lexical_tag.capitalize()}"    
    
    for line_no, string in enumerate(cleaned_definitions):
        if line_no == 0:
            split_def    =  string.split()
            split_def    =  " ".join(split_def[1: ])
            defs_string += f" <i>{split_def}</i>"
        elif line_no == 1:
            defs_string += "<ol>"
            defs_string += f"<li>{string}</li>"
        else:
            defs_string += f"<li>{string}</li>"
    
    defs_string += "</ol>"
    defs_string += "<br>"

    return defs_string    


def construct_etymology_html(cleaned_etymology_section: str, lexical_tag: str, defs_string: str) -> str:
    """Construct the HTML for etymology information.

    Arguments:
        cleaned_etymology_section: Single item from the "cleaned definitions" dictionary pulled from the etymology
        entry.
        lexical_tag: The etymology tag from the "cleaned definitions" dictionary.
        defs_string: The ongoing string of definitions under construction.

    Returns:
        The ongoing HTML construct with etymology information added.
    """
    defs_string += f"<span style='color:grey;font-size:0.85em;'>{lexical_tag.capitalize()}</span>"
    defs_string += f"<span style='color:grey;font-size:0.85em;'><ul><li>{cleaned_etymology_section}</li></ul><br></span>"
    return defs_string

def construct_usage_notes_html(cleaned_usage_section: str, lexical_tag: str, defs_string: str) -> str:
    """Construct the HTML for usage notes.

    Arguments:
        cleaned_definition: Single item from the "cleaned definitions" dictionary pulled from the usage notes entry.
        lexical_tag: The usage notes tag from the "cleaned definitions" dictionary.
        defs_string: The ongoing string of definitions under construction.

    Returns:
        The ongoing HTML construct with usage notes added.
    """
    defs_string += f"<span style='color:grey;font-size:0.85em;'>{lexical_tag.capitalize()}</span>"
    usage_items = cleaned_usage_section.split("*")
    
    for uitem_i, usage_item in enumerate(usage_items):
        if usage_items != "" and uitem_i == 0:
            defs_string += "<ul><span style='color:grey;font-size:0.85em;'>"
        elif usage_item != "":
            defs_string += f"<li>{usage_item}</li>"
    defs_string += "</ul></span><br>"
    
    return defs_string


def wrap_html(html_content: str="", colour_mode: str="light", search_type: SearchType=SearchType.WORD) -> str:
    """Wraps the HTML content in the appropriate header and footer according to colour mode.

    Keyword Arguments:
        html_content: The HTML content to be wrapped.
        colour_mode: The colour mode of the front-end.
        search_type: Whether the conjugation table header or regular header should be added (default: {SearchType.WORD})

    Returns:
        HTML content wrapped in the appropriate header and footer, ready for display.
    """
    if colour_mode == "light":
        return HTML_HEADER_LIGHT + html_content + HTML_FOOTER
    
    if search_type == (SearchType.WORD_CONJ_COMBO or SearchType.CONJUGATION):
        html_construct = HTML_HEADER_DARK_CONJ + html_content + HTML_FOOTER
    else:
        html_construct = HTML_HEADER_DARK + html_content + HTML_FOOTER
    return html_construct