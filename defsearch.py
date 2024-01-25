from concurrent.futures import Future
from bs4                import BeautifulSoup
from wiktionaryparser   import WiktionaryParser
from typing             import List, Dict
import logging
import requests
import re
import requests
from typing import Union


# Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(f"{__name__}.log", mode='w')
formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_definitions(language: str, search_token: str, get_etymology="False", 
                    get_usage_notes="False") -> Union[Dict[str, List[str]], None]:
    """Get the definitions for a word from Wiktionary. Uses the WiktionaryParser library to get the definitions, but
    uses the Wiktionary API to get the etymology and usage notes, as the WiktionaryParser library does not support
    usage notes ಠ_ಠ.
    
    Called by both manual and AutoAnki searches.
    
    Etymology and usage searches are specificed to increase speed, particularly for usage note searches, as they must
    be done by manually calling the API, resulting in two simultaneous API calls: one from the API library, and another
    from the manual call function.

    Parameters
    ----------
    language : str
        Currently selected language.
    search_token : str
        String to search for.
    get_etymology : str, optional
        Whether the search should grab etymology, by default "False"
    get_usage_notes : str, optional
        Whether the search should grab usage notes, by default "False"
        
    Returns
    -------
    dict, bool
        A dictionary of definitions for the word: keys represent the grammar tag, values represent the definition for
        that tag.
        None if no definitions were found.
    """
    parser = WiktionaryParser()
    wik_parser_result = parser.fetch(search_token, language)
    
    definitions = {}
    for definition in wik_parser_result:
        for part_of_speech in definition["definitions"]:
            if part_of_speech["partOfSpeech"]   == "noun":
                definitions["noun"]           = part_of_speech["text"]
            elif part_of_speech["partOfSpeech"] == "verb":
                definitions["verb"]           = part_of_speech["text"]
            elif part_of_speech["partOfSpeech"] == "adjective":
                definitions["adjective" ]     = part_of_speech["text"]
            elif part_of_speech["partOfSpeech"] == "adverb":
                definitions["adverb"]         = part_of_speech["text"]
            elif part_of_speech["partOfSpeech"] == "pronoun":
                definitions["pronoun"]        = part_of_speech["text"]
            elif part_of_speech["partOfSpeech"] == "preposition":
                definitions["preposition"]    = part_of_speech["text"]
            elif part_of_speech["partOfSpeech"] == "particle":
                definitions["particle"]       = part_of_speech["text"]
            elif part_of_speech["partOfSpeech"] == "conjunction":
                definitions["conjunction"]    = part_of_speech["text"]
            elif part_of_speech["partOfSpeech"] == "article":
                definitions["article"]        = part_of_speech["text"]
            elif part_of_speech["partOfSpeech"] == "numeral":
                definitions["numeral"]        = part_of_speech["text"]
            elif part_of_speech["partOfSpeech"] == "interjection":
                definitions["interjection"]   = part_of_speech["text"]
            elif part_of_speech["partOfSpeech"] == "exclamation":
                definitions["exclamation"]    = part_of_speech["text"]
            elif part_of_speech["partOfSpeech"] == "determiner":
                definitions["determiner"]     = part_of_speech["text"]
        
        if get_etymology == "True":
            if wik_parser_result[0]["etymology"] != "":
                definitions["etymology"] = [wik_parser_result[0]["etymology"]]
        
        if get_usage_notes == "True":  # For some reason the WiktionaryParser library doesn't support usage notes
            page_content = call_api_raw(search_token)
            if page_content is not None:
                r_lang = re.escape("==" + language + "==")
                try:
                    lang_section = re.search(rf'{r_lang}\n(.*?)(?=\n==[^=]|$)', page_content, re.DOTALL)
                    if lang_section is not None:
                        lang_content = lang_section.group(1)
                        usage_section = re.findall(r'===Usage notes===\n(.*?)(\n==|\n===|$|$)', lang_content, re.DOTALL)
                        if not usage_section:
                            usage_section = re.findall(r'====Usage notes====\n(.*?)(\n==|\n===|$)', lang_content, re.DOTALL)
                        try:
                            definitions["usage"] = usage_section[0]
                        except:
                            pass
                except:
                    logger.warning(f"Manual API call found nothing for search_token: {search_token}")
        
        if any(definitions.values()):
            return definitions
        else:
            return None


def call_api_raw(search_token: str) -> Union[str, None]:
        url = "https://en.wiktionary.org/w/api.php"
        params = {
            "action": "query",
            "titles": search_token,
            "prop": "revisions",
            "rvprop": "content",
            "format": "json",
            "rvslots": "*"
        }
        response = requests.get(url, params=params)    
        if response.status_code == 200:  # 200 = success
            data  = response.json()
            pages = data['query']['pages']    
            page  = next(iter(pages.values()))  # Extract the page
            if "revisions" in page:  # If page exists
                content = page['revisions'][0]['slots']['main']['*']
                return content 
            else:
                return None
        else:
            return None


def get_defs_man_search(text: str, language: str, get_etymology: str, 
                        get_usage_notes: str) -> Union[Dict[str, List[str]], None]:
    """Get definitions for user input from Wiktionary. Called for manual searches only.

    Parameters
    ----------
    text : str
        The user's text input.
    language : str
        Language currently selected.
    get_etymology : str
        Whether the search should include etymology. Boolean formatted as str.
    get_usage_notes : str
        Whether the search should include usage notes. Boolean formatted as str.

    Returns
    -------
    list
        Array of dictionaries. Each dictionary contains the definitionss for a single word, with the keys representing
        a grammar tag.
    """
    parsed_definitions_dict = get_definitions(language, text, get_etymology, get_usage_notes)
    
    if parsed_definitions_dict is not None:
        for def_tag, definitions in parsed_definitions_dict.items():
            parsed_definitions_dict[def_tag] = clean_wikitext(definitions)        
    return parsed_definitions_dict


def get_wiktionary_url(search_token: str) -> str:
    """Get the Wiktionary URL for a word.

    Parameters
    ----------
    search_token : str
        The word or phrase to search for.

    Returns
    -------
    str
        Wiktionary URL for the word or phrase.
    """
    base_url = "https://en.wiktionary.org/wiki/"
    url      = f"{base_url}{search_token}"
    return url


def grab_wik_conjtable(search_token: str, language: str) -> str:
    """Grab the conjugation table from Wiktionary. This is done by webscraping the page: although the API does return
    conjugation tables, it would require rebuilding the HTML for the table, so scraping is easier.

    Parameters
    ----------
    search_token : str
        The word to search for.
    language : str
        Currently selected language, used to find the correct section on the Wiktionary page.

    Returns
    -------
    str
        HTML for the conjugation table.
    """
    wik_url      = get_wiktionary_url(search_token)
    response     = requests.get(wik_url)
    soup         = BeautifulSoup(response.text, 'html.parser')
    lang_section = soup.find('span', {"class": "mw-headline", "id": f"{language}"})
    conjugation_header = None
    
    if lang_section:
        content = lang_section.parent
        if content:
            conjugation_header = content.find_next('span', id='Conjugation')
            if not conjugation_header:
                conjugation_header = content.find_next('span', id='Conjugation_2')
            if not conjugation_header:
                conjugation_header = content.find_next('span', id='Conjugation_3')
            if not conjugation_header:
                conjugation_header = content.find_next('span', id='Conjugation_4')
        
        if conjugation_header:
            table = conjugation_header.find_next('table')
            if table:
                return str(table)
            else:
                return "Could not find conjugation table."
        else:
            return "Could not find conjugation header"
    else:
        return "Language section not found."


def strip_bs4_links(html_content: str) -> str:
    """Remove links from the HTML content. This is done because links are visually messy and not needed.

    Parameters
    ----------
    html_content : str
        HTML content representing a conjugation table.

    Returns
    -------
    str
        HTML content with links removed.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    for link in soup.find_all('a'):
        link.replace_with(link.text)
    return str(soup)


def clean_wikitext(definitions: list) -> list:
    """Cleans the text pulled from Wiktionary to be more readable. Without cleaning, the text is visually messy,
    containing brackets, obscure linguistic tags, etc.

    Parameters
    ----------
    definitions : list
        List of definitions of a single grammar tag for a single word.

    Returns
    -------
    list
        Readable definitions of a single grammar tag for a single word.
    """
    cleaned_definitions = []
    
    for def_i, definition in enumerate(definitions):
        temp_cleaned_definition_line = definition
        temp_cleaned_definition_line = temp_cleaned_definition_line.replace(")", "</span>")
        temp_cleaned_definition_line = temp_cleaned_definition_line.replace("(", "<span style='color:grey;font-size:0.85em;'>")
        temp_cleaned_definition_line = temp_cleaned_definition_line.replace("]", "</span>")
        temp_cleaned_definition_line = temp_cleaned_definition_line.replace("[", "<span style='color:grey;font-size:0.85em;'>")
        
        if def_i == 0:
            temp_cleaned_definition_line = temp_cleaned_definition_line.replace("plural ", "plural: ")
            temp_cleaned_definition_line = temp_cleaned_definition_line.replace("diminutive ", "diminutive: ")
            temp_cleaned_definition_line = temp_cleaned_definition_line.replace("genitive ", "genitive: ")
            temp_cleaned_definition_line = temp_cleaned_definition_line.replace("feminine ", "feminine: ")
            temp_cleaned_definition_line = temp_cleaned_definition_line.replace("masculine ", "masculine: ")
            temp_cleaned_definition_line = temp_cleaned_definition_line.replace("feminine: plural", "feminine plural")
            temp_cleaned_definition_line = temp_cleaned_definition_line.replace("masculine: plural", "masculine plural")
            temp_cleaned_definition_line = temp_cleaned_definition_line.replace("masculine: singular", "masculine singular:")
            temp_cleaned_definition_line = temp_cleaned_definition_line.replace("comparative ", "comparative: ")
            temp_cleaned_definition_line = temp_cleaned_definition_line.replace("superlative ", "superlative: ")
            temp_cleaned_definition_line = temp_cleaned_definition_line.replace("singular present", "singular present:")
            temp_cleaned_definition_line = temp_cleaned_definition_line.replace("past tense", "past tense:")
            temp_cleaned_definition_line = temp_cleaned_definition_line.replace("past participle", "past participle:")
            temp_cleaned_definition_line = temp_cleaned_definition_line.replace("past subjunctive", "past subjunctive:")
            temp_cleaned_definition_line = temp_cleaned_definition_line.replace("auxiliary", "auxiliary:")
        
        cleaned_definitions.append(temp_cleaned_definition_line)        
    
    return cleaned_definitions
