from bs4                import BeautifulSoup
from wiktionaryparser   import WiktionaryParser
from manualsearchdb     import ItemDefinitions
from typing             import Union
import logging
import requests
import re
import requests


# Logger
logger    = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler   = logging.FileHandler(f"{__name__}.log", mode = 'w')
formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_conjugation_table(search_token: str, language: str) -> Union[str, None]:
    """Grab the conjugation table from Wiktionary. This is done by webscraping the page. Although the API does return
    conjugation tables, it would require rebuilding the HTML for the table, so scraping is easier.
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
                return None # Could not find conjugation table
        else:
            return None # Could not find conjugation header
    else:
        return None # Language section not found


def strip_bs4_links(html_content: str) -> str:
    """Remove links from the HTML content. This is done because links are visually messy and not needed."""
    soup = BeautifulSoup(html_content, 'html.parser')
    for link in soup.find_all('a'):
        link.replace_with(link.text)
    return str(soup)


def get_definitions(search_token: str, language: str, etym_flag: bool=False, usage_flag: bool =False, 
                    grammar_tag: str="") -> Union[ItemDefinitions, None]:
    """Get the definitions for a word from Wiktionary. Uses the WiktionaryParser library to get the definitions, but
    also manually calls the Wiktionary API to get the etymology and usage notes, as the WiktionaryParser library does 
    not support usage notes ಠ_ಠ.
    
    Called by both manual and AutoAnki searches.
    
    Usage notes searches significantly slow the program due to the doubling up of API calls, so the additional call is
    only made if the user has selected to get the notes. In an attempt to increase speed, etymology calls are also 
    conditional.
    """
    parser = WiktionaryParser()
    # ! This seems to return definitions for words from similar languages, not just the selected language. 
    # Example: sprak (Dutch) has no German definition, but the parser returns the Dutch definition when searching in
    # the German language. Kind of cool, but might be confusing, as it is presented as if it is a valid German
    # definition.
    # TODO: Either disable this functionality, or add a disclaimer in the definition result that the 'related' 
    # TODO: definition is not from the selected language. 
    wik_parser_result = parser.fetch(search_token, language)   

    definitions = {
        "noun"        : tuple(str()),
        "verb"        : tuple(str()),
        "adjective"   : tuple(str()),
        "adverb"      : tuple(str()),
        "pronoun"     : tuple(str()),
        "preposition" : tuple(str()),
        "particle"    : tuple(str()),
        "conjunction" : tuple(str()),
        "article"     : tuple(str()),
        "numeral"     : tuple(str()),
        "interjection": tuple(str()),
        "exclamation" : tuple(str()),
        "determiner"  : tuple(str()),
        "etymology"   : tuple(str()),
        "usage"       : tuple(str())
    }
    
    # if len(wik_parser_result) == 0:
    #     return None
    # if len(wik_parser_result[0]["definitions"]) == 0:
    #     return None
    
    for definition in wik_parser_result:
        for part_of_speech in definition["definitions"]:
            if part_of_speech["partOfSpeech"]   == "noun":
                definitions["noun"]           = part_of_speech["text"]
            elif part_of_speech["partOfSpeech"] == "verb":
                definitions["verb"]           = part_of_speech["text"]
            
            # Because Stanza tags participles as adjectives, we index them as being an adjective. Participle
            # usually indicate that they're participles in the definition (as opposed to the grammar tag) anyway.
            elif part_of_speech["partOfSpeech"] == "adjective":
                definitions["adjective" ]     = part_of_speech["text"]
            elif part_of_speech["partOfSpeech"] == "participle":
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
        
        if language == "German" and grammar_tag == "ADJ" and definitions["adjective"] == tuple(""):
            definitions = double_check_german_participle_adjective(search_token, grammar_tag, parser, definitions)
        
        if etym_flag == True:
            if wik_parser_result[0]["etymology"] != "":
                definitions["etymology"] = (wik_parser_result[0]["etymology"],)
        
        if usage_flag == True:
            page_html = call_api_raw(search_token)
            if page_html is None:
                break
            
            language_header = re.escape("==" + language + "==")
            language_section = re.search(rf'{language_header}\n(.*?)(?=\n==[^=]|$)', page_html, re.DOTALL)
            if language_section is None:
                break
            
            language_section_html = language_section.group(1)
            language_section = re.findall(r'===Usage notes===\n(.*?)(\n==|\n===|$|$)', language_section_html, re.DOTALL)
            if not language_section: # Because Wiktionary can be inconsistent, try another variation of the header
                language_section = re.findall(r'====Usage notes====\n(.*?)(\n==|\n===|$)', language_section_html, re.DOTALL)
            if language_section:
                definitions["usage"] = language_section[0]
        
        item_definitions = ItemDefinitions(**definitions)
        return item_definitions


def call_api_raw(search_token: str) -> Union[str, None]:
    """Manually call the Wiktionary API and get the raw page content."""
    url = "https://en.wiktionary.org/w/api.php"
    params = {
        "action" : "query",
        "titles" : search_token,
        "prop"   : "revisions",
        "rvprop" : "content",
        "format" : "json",
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


def double_check_german_participle_adjective(search_token: str, grammar_tag: str, 
        parser: WiktionaryParser, definitions: dict) -> dict:
    """It is rare for Wiktionary to have present partciple entries for German adjectives, but the definition for 
    these adjectives can be deduced from the verb definition. To find the verb definition of a German present 
    participle, the participle ending is removed. Luckily these participles follow a consistent pattern of
    ending in -d, so the ending is removed and the verb definition is returned, with a disclaimer noting that 
    this is the verb definition, but should be relevant enough to be used as the adjective definition.

    Returns:
        dict: Updated dictionary of definitions with verb definition being used as the adjective participle definition.
    """
    # Remove the particple ending from the adjective
    if search_token[-1] == "d":
        search_token = search_token[:-1]
    else:
        return definitions
    
    wik_parser_result = parser.fetch(search_token, "German")
    
    for definition in wik_parser_result:
        for part_of_speech in definition["definitions"]:
            if part_of_speech["partOfSpeech"] == "verb":
                definitions["adjective"] = part_of_speech["text"]
                # Notify the user that the verb definition is being used
                # TODO: Fix this hacky workaround for how the first word in line 0 is deleted
                definitions["adjective"][0] = "string_to_scrifice ( <br>Verb definition used for adjective participle definition,<br> ) " + definitions["adjective"][0]
    
    return definitions


def clean_wikitext(definitions: list) -> list:
    """Cleans the text pulled from Wiktionary to be more readable. Without cleaning, the text is very messy,
    containing brackets, obscure linguistic tags, etc.
    """
    cleaned_definitions = []
    
    for def_i, definition in enumerate(definitions):
        temp_cleaned_definition_line = definition
        temp_cleaned_definition_line = temp_cleaned_definition_line.replace(")", "</span>")
        temp_cleaned_definition_line = temp_cleaned_definition_line.replace("(", "<span style='color:grey;font-size:0.85em;'>")
        temp_cleaned_definition_line = temp_cleaned_definition_line.replace("]", "</span>")
        temp_cleaned_definition_line = temp_cleaned_definition_line.replace("[", "<span style='color:grey;font-size:0.85em;'>")
        temp_cleaned_definition_line = temp_cleaned_definition_line.replace("{{", "<i>")
        temp_cleaned_definition_line = temp_cleaned_definition_line.replace("}}", "</i>")
        temp_cleaned_definition_line = temp_cleaned_definition_line.replace("[[", "<i>")
        temp_cleaned_definition_line = temp_cleaned_definition_line.replace("]]", "</i>")
        temp_cleaned_definition_line = temp_cleaned_definition_line.replace("m|de|", "")
        temp_cleaned_definition_line = temp_cleaned_definition_line.replace("uxi|de|", "")
        temp_cleaned_definition_line = temp_cleaned_definition_line.replace("|", ", ")
        temp_cleaned_definition_line = temp_cleaned_definition_line.replace("t=", "translation = ")
        temp_cleaned_definition_line = temp_cleaned_definition_line.replace(": ", "")
        
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
