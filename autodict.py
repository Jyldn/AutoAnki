from bs4 import BeautifulSoup, NavigableString
from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.parse import quote
import logging
import re
from pprint import pprint


langs = {
    "1": "Deutsch",
    "2": "English"
}


def select_lang():
    print(f"Select your language:\n1) Deutsch\n2) English")
    valid_selection = False
    # Keep asking for user input until a valid section is made.
    while valid_selection == False:
        lang_selection = input()
        # Check the input, make sure it's an integer.
        if lang_selection in langs:
            valid_selection = True
        else:
            print("Invalid selection. Please enter the number that corresponds to your selection.")
    print("\n")
    return lang_selection


def get_word(lang_selection):
    if langs[lang_selection] == "Deutsch":
        print(f"Geben Sie ein Wort ein: ")
        word_input = input()
    elif langs[lang_selection] == "English":
        print(f"Enter a word: ")
        word_input = input()
    print("-----------")
    return quote(word_input)


def save_page(word_input, lang_selection):
    # Create the URL.
    # Select language.
    if langs[lang_selection] == "Deutsch":
        url = "https://de.wiktionary.org/wiki/"
    elif langs[lang_selection] == "English":
        url = "https://en.wiktionary.org/wiki/"
    # Concatenate the base URL with the word input.
    url += word_input
    # Save the page contents.
    try:
        page = urlopen(url)
    except HTTPError:
        print("Page not found.\n\n")
        return None
    # Open with BS.
    try:
        page = BeautifulSoup(page.read(), 'html.parser')
    except UnboundLocalError:
        print("Page not found.\n\n")
        return None
    return page


def parse_page(page, lang_selection):
    # Get H2s. These should be the headers that introduce each word by language. Within each language entry, there can be multiple groups of definitions.
    h2s = page.find_all("h2")
    definition_index = get_definition_index(h2s, lang_selection)
    logging.info(f"Definition index: {definition_index}")
    # Get header for selected lang.
    main_header = h2s[definition_index]
    logging.info(f"Selected header: {main_header}\n{main_header.get_text()}")
    # Get all the elements between the selected header and the next header.
    elements = main_header.find_next_siblings()
    definitions = get_defs(elements, lang_selection)
    elements = main_header.find_next_siblings()
    definitions = get_defs(elements, lang_selection)
    return definitions


def get_defs(elements, lang_selection):
    # German definitions are simple to find. They are listed under the keyword 'Bedeutungen'. English has no keyword, it's just the word search term repeated. However, it does seem to have a unique class, 'Latn headword'.
    definitions = []
    word_type = ""
    counter = 0
    # GERMAN DEFINITIONS
    if langs[lang_selection] == "Deutsch":
        for element in elements:
            if element.name == "h3":
                word_type = element
                #.append(word_type)
            if element.get_text() == "Bedeutungen:":
                raw_defs = element.find_next_siblings(name=['dl'], limit=1)
                raw_defs[0].insert(0, word_type)
                raw_defs[0].insert(1, "\n")
                definitions.append(raw_defs)
                counter += 1
            elif element.name == "h2":
                # End search when next language section is parsed.
                #pprint(definitions)
                return definitions
    # ENGLISH DEFINITIONS
    elif langs[lang_selection] == "English":
        for element in elements:
            counter = 0
            if element.name == "h4":
                definitions.append(f"\n{element.get_text()}")
            if element.name == "ol":
                counter = 0
                temp_strs = []
                for child in element.children:
                    temp_str = ""
                    counter += counter
                    if type(child) is not NavigableString:
                        for child_child in child.children:
                            if child_child.name != "dl" and child_child.string:
                                temp_str = temp_str + child_child.get_text()
                    temp_strs.append(temp_str)
                # Remove blank lines from array.
                temp_strs = [string for string in temp_strs if string.strip() != ""]
                # Remove all line breaks.
                temp_strs = [s.replace('\n', '') for s in temp_strs]
                for line in temp_strs:
                    counter += 1
                    definitions.append(f"[{counter}] {line}")
            if element.name == "h2":
                # End search when next language section is parsed.
                return definitions
    return definitions


def print_definitions(definitions, lang_selection):
    counter = 0
    if langs[lang_selection] == "Deutsch":
        for defi in definitions:
            for element in defi:
                counter += 1
                print(f"\nBedeutung {counter}:")
                text = element.get_text()
                text = re.sub(r"\[Bearbeiten\]", "", text)
                # Remove the initial new line character.
                text = text[1:]
                print(text)
    elif langs[lang_selection] == "English":
        for line in definitions:
            counter += 1
            print(f"{line}")
    print()
    

def get_definition_index(h2s, lang_selection):
    # Like most things, Wiktionary does not have a standard across languages for how pages are set up with regards to styling. Therefore, different languages format things differently. 
    counter = 0
    for header in h2s:
        header = header.get_text()
        if langs[lang_selection] == "Deutsch":
            header = header.split(" ")
        if len(header) > 1: 
            if langs[lang_selection] == "Deutsch":
                split_header = header[1].split(")")
                split_header = split_header[0] + ")"
                # Note the brackets necessary for German Wiktionary.
                if split_header == f"({langs[lang_selection]})":
                    return counter
            elif langs[lang_selection] == "English":
                split_header = header.split("[")
                split_header = split_header[0]
                if split_header == f"{langs[lang_selection]}":
                    return counter
            logging.info(f"HEADER: {split_header},{langs[lang_selection]}")
            
        counter += 1
    # No definition found for the target language.
    return None


def main():
    level = logging.WARNING
    logging.basicConfig(level=level)
    # Get language selection from user.
    lang_selection = select_lang()
    while True:
        # Get the word that the user wants to define.
        word_input = get_word(lang_selection)
        page = save_page(word_input, lang_selection)
        if page != None:
            definitions = parse_page(page, lang_selection)
            print_definitions(definitions, lang_selection)


main()