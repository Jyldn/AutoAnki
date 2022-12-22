from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.error import HTTPError
import logging
import re


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


def get_word():
    print(f"Enter word: ")
    word_input = input()
    print("-----------")
    return word_input


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
    definitions = get_defs(elements)
    return definitions


def get_defs(elements):
    definitions = []
    for element in elements:
        if element.get_text() == "Bedeutungen:":
            raw_defs = element.find_next_siblings(name=['dl'], limit=1)
            definitions.append(raw_defs)
        elif element.name == "h2":
            # End search when next language section is parsed.
            return definitions
    return definitions


def print_definitions(definitions):
    counter = 0
    for defi in definitions:
        for element in defi:
            counter += 1
            print(f"Definition {counter}:")
            print(f"{element.get_text()}\n")
    print()
    

def get_definition_index(h2s, lang_selection):
    counter = 0
    for header in h2s:
        header = header.get_text().split(" ")
        if len(header) > 1: 
            split_header = header[1].split(")")
            split_header = split_header[0] + ")"
            logging.info(split_header)
            if split_header == f"({langs[lang_selection]})":
                return counter
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
        word_input = get_word()
        page = save_page(word_input, lang_selection)
        if page != None:
            definitions = parse_page(page, lang_selection)
            print_definitions(definitions)


main()