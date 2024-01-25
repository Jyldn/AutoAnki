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


def get_conjugation_table(search_token: str, language: str) -> str:
    """Grab the conjugation table from Wiktionary. This is done by webscraping the page. Although the API does return
    conjugation tables, it would require rebuilding the HTML for the table, so scraping is easier.

    Arguments:
        search_token -- The word to search for.
        language -- Selected language.

    Returns:
        HTML content of the conjugation table.
    """
    base_url = "https://en.wiktionary.org/wiki/"
    wik_url      = f"{base_url}{search_token}"
    
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

    Arguments:
        html_content -- HTML content to strip links from.

    Returns:
        HTML content with links removed.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    for link in soup.find_all('a'):
        link.replace_with(link.text)
    return str(soup)


def handle_manual_def_search(text: str, language: str, get_etymology: str, 
                        get_usage_notes: str) -> Union[Dict[str, List[str]], None]:
    """Wrapper function for manual searches. Grabs definitions for a single search-term from the Wiktionary API and 
    cleans them for display.

    Arguments:
        text -- The individual word/phrase to search for.
        language -- Selected language.
        get_etymology -- Whether to access and save etymology.
        get_usage_notes -- Whether to manually call the Wiktionary API and get usage notes.

    Returns:
        Dictionary of definitions for the individual search-term. Keys represent grammar tags.
    """
    parsed_definitions_dict = get_definitions(language, text, get_etymology, get_usage_notes)
    
    if parsed_definitions_dict is not None:
        for def_tag, definitions in parsed_definitions_dict.items():
            parsed_definitions_dict[def_tag] = clean_wikitext(definitions)        
    return parsed_definitions_dict


def get_definitions(language: str, search_token: str, get_etymology: str ="False", get_usage_notes: str ="False"
                    ) -> Union[Dict[str, List[str]], None]:
    """Get the definitions for a word from Wiktionary. Uses the WiktionaryParser library to get the definitions, but
    also manually calls the Wiktionary API to get the etymology and usage notes, as the WiktionaryParser library does 
    not support usage notes ಠ_ಠ.
    
    Called by both manual and AutoAnki searches.
    
    Usage notes searches significantly slow the program due to the doubling up of API calls, so the additional call is
    only made if the user has selected to get the notes. In an attempt to increase speed, etymology calls are also 
    conditional.
    
    Arguments:
        language -- Selected language.
        search_token -- The word/phrase to search for.

    Keyword Arguments:
        get_etymology -- Whether to access and save etymology. (default: {"False"})
        get_usage_notes -- Whether to manually call the Wiktionary API and get usage notes. (default: {"False"})

    Returns:
        Dictionary of definitions for the individual search-term. Keys represent grammar tags.
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
        
        if get_usage_notes == "True":
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
    """Manually call the Wiktionary API and get the raw page content.

    Arguments:
        search_token -- The word/phrase to search for.

    Returns:
        Raw page content.
    """
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


def clean_wikitext(definitions: list) -> list:
    """Cleans the text pulled from Wiktionary to be more readable. Without cleaning, the text is very messy,
    containing brackets, obscure linguistic tags, etc.

    Arguments:
        definitions -- List of definitions to clean.

    Returns:
        Cleaned list of definitions.
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
