from concurrent.futures import Future
from typing             import List, Dict
from defsearch           import get_definitions, clean_wikitext
import string
import stanza
import spacy_stanza
import re
import os
from typing_extensions import TypedDict, NotRequired
from typing import Union


GENDERED_LANGS = ["German", "French", "Spanish", "Latin"]

MARKED_TOKEN    = str
DEF_GRAMMAR_TAG = str
DEF_ITEMS       = List[str]

SPACY_TO_NLTK_TAG_MAP = {
    'ADJ'   : 'adjective',
    'ADP'   : 'preposition',
    'ADV'   : 'adverb',
    'AUX'   : 'modal',
    'CONJ'  : 'conjunction',
    'CCONJ' : 'conjunction',
    'DET'   : 'determiner',
    'INTJ'  : 'interjection',
    'NOUN'  : 'noun',
    'NUM'   : 'numeral',
    'PART'  : 'particle',
    'PRON'  : 'pronoun',
    'PROPN' : 'proper noun',
    'PUNCT' : 'symbol', 
    'SCONJ' : 'preposition',
    'SYM'   : 'symbol',
    'VERB'  : 'verb',
    'X'     : 'x',
    'SPACE' : 'space'
}


class BacksideEntriesData(TypedDict):
    all_defs:       NotRequired[Dict[DEF_GRAMMAR_TAG, DEF_ITEMS]]
    relv_defs:      NotRequired[List[str]]
    grammar_tag:    NotRequired[str]
    lemma:          NotRequired[str]
    target_type:    NotRequired[str]


class Card(TypedDict):    
    frontside_text: str
    backside_entries: NotRequired[Dict[MARKED_TOKEN, BacksideEntriesData]]


def make_cards(txt_file_pth: str, language: str, deck_name: str, messageQueue, s_folder_pth: str ="") -> bool: 
    """Main function for the AutoAnki process. Takes the user's input text and generates Anki cards from it.

    Parameters
    ----------
    txt_file_pth : str
        Path to the user's input text file.
    language : str
        Language currently selected.
    deck_name : str
        Name of the deck to be created. Used for formatting the Anki file and for the output filename.
    messageQueue : _type_
        Message queue object that sends updates to the GUI for the user. Messages should be written in non-technical 
        plain language.
    s_folder_pth : str, optional
        Where the output should be saved, by default "" if the user has not selected an output folder.

    Returns
    -------
    bool
        Whether the process was successful.
    """
    feed_msg_queue("start", messageQueue)

    input_file_text = read_sentence_file(txt_file_pth)
    if input_file_text == None:
        feed_msg_queue("file_error", messageQueue)
        return False
    
    frontside_lines = input_file_text.splitlines()
    cards_amount    = len(frontside_lines)
    cards_arr       = []
        
    for card_i, frontside_line in enumerate(frontside_lines):
        cards_arr.append(Card({"frontside_text": frontside_line, "backside_entries": {}}))
    
    feed_msg_queue("keywords", messageQueue)
    cards_arr = find_marked_tokens(cards_arr)
    
    feed_msg_queue("lang_processor", messageQueue)
    nlp = get_nlp(language)
    
    # Get definitions from Wiktionary
    feed_msg_queue("making_cards", messageQueue, cards_amount)
    for card_i, card in enumerate(cards_arr):
        feed_msg_queue("card_progress", messageQueue, cards_amount, card_i + 1)
        for target, bside_entry in card['backside_entries'].items():
            fside_txt = card["frontside_text"]
            lemma, grammar_tag = get_lemma_and_grammar_tag(target, fside_txt, nlp, bside_entry["target_type"])
            if language == "German" and grammar_tag == "NN":  # German nouns must be capitalised
                lemma = lemma.capitalize()
            else:
                lemma = lemma.lower()
            cards_arr[card_i]["backside_entries"][target]["lemma"]       = lemma
            cards_arr[card_i]["backside_entries"][target]["all_defs"]    = get_definitions(language, lemma) 
            cards_arr[card_i]["backside_entries"][target]["grammar_tag"] = grammar_tag           
        
    # Make things readable
    cards_arr = make_tags_readable(cards_arr) 
    feed_msg_queue("processing", messageQueue)
    cards_arr = remove_irrelevant_defs(cards_arr)    
    feed_msg_queue("cleaning", messageQueue)
    for card_i, card in enumerate(cards_arr):
        for bside_entry in card["backside_entries"].values():
            cleaned_defs = clean_wikitext(bside_entry["relv_defs"])
            cards_arr[card_i]["relv_defs"] = cleaned_defs
    
    # All data is now ready to be formatted into Anki cards
    feed_msg_queue("formatting", messageQueue)
    anki_input = ""
    for card_i, card in enumerate(cards_arr):
        if card_i > 0:
            anki_input += "\n"
        anki_input += format_card(card, deck_name)
    
    filename = f"{deck_name}_deck.txt"
    if s_folder_pth == "":
        full_file_path = os.path.join(os.getcwd(), filename)
    else:
        full_file_path = os.path.join(s_folder_pth, filename)

    export_success = export_cards(full_file_path, anki_input)
    if export_success:
        feed_msg_queue("saved", messageQueue, file_path=full_file_path)
    else:
        feed_msg_queue("save_error", messageQueue, file_path=full_file_path)
        return False
    feed_msg_queue("done", messageQueue)
    return True


def read_sentence_file(txt_file_pth: str) -> Union[str, None]:
    """Reads the user's input text file.

    Parameters
    ----------
    txt_file_pth : str
        Path to the user's input text file.

    Returns
    -------
    str or None
        The user's input text. This text should be seperated by line breaks, with each line representing an individual 
        card's front-side text.
    """
    try:
        with open(txt_file_pth, 'r', encoding="utf-8") as file:
            text = file.read()
    except:
        return None
    return text


def find_marked_tokens(cards_arr: list) -> list:
    """Find the tokens marked by the user in the input text. 
    An individual word is marked with a preceeding asterisk: *word
    A phrase is marked with wrapping hashtags: #phrase#

    Parameters
    ----------
    cards_arr : list
        Array of dictionaries. Each dictionary holds the data for an individual card.

    Returns
    -------
    list
        Array of dictionaries with the marked tokens added to the backside_entries dictionary.
    """
    pattern_word = r"\*(\w+)"
    pattern_phrase = r"#(.*?)#"
    new_c_arr = cards_arr
    
    def get_t_type(target: str) -> str:
        if target.count(" ") > 0:
            return "phrase"
        else:
            return "word"

    for card_i, card in enumerate(cards_arr):
        words = re.findall(pattern_word, card.get("frontside_text"))
        phrases = re.findall(pattern_phrase, card.get("frontside_text"))
        targets = words + phrases
        for target in targets:
            target_type = get_t_type(target)
            new_c_arr[card_i]["backside_entries"][f"{target}"] = {
                "all_defs": {}, "relv_defs": [], "grammar_tag": "", "lemma": "", "target_type": target_type}
    
    return new_c_arr


def get_nlp(language: str) -> Union[spacy_stanza.Language, None]:
    """Get the language processor for the selected language.

    Parameters
    ----------
    language : str
        Currently selected language.

    Returns
    -------
    spacy_stanza object
        Language processor object.
    """
    if language == "Arabic":
        stanza.download("ar")
        nlp     = spacy_stanza.load_pipeline("ar", package="padt", processors='tokenize,mwt,pos,lemma', use_gpu=True)
    elif language == "English":
        stanza.download("en")
        nlp     = spacy_stanza.load_pipeline("en", package="partut", processors='tokenize,mwt,pos,lemma', use_gpu=True)
    elif language == "French":
        stanza.download("fr")
        nlp     = spacy_stanza.load_pipeline("fr", package="partut", processors='tokenize,mwt,pos,lemma', use_gpu=True)
    elif language == "German":
        stanza.download("de")
        nlp     = spacy_stanza.load_pipeline("de", package="hdt", processors='tokenize,mwt,pos,lemma', use_gpu=True)
    elif language == "Japanese":
        stanza.download("ja")
        nlp     = spacy_stanza.load_pipeline("ja", package="gsd", use_gpu=True)
    elif language == "Korean":
        stanza.download("ko")
        nlp     = spacy_stanza.load_pipeline("ko", package="kaist", processors='tokenize,mwt,pos,lemma', use_gpu=True)
    elif language == "Latin":
        stanza.download("la")
        nlp     = spacy_stanza.load_pipeline("la", package="llct", processors='tokenize,mwt,pos,lemma', use_gpu=True)
    elif language == "Persian":
        stanza.download("fa")
        nlp     = spacy_stanza.load_pipeline("fa", package="seraji", processors='tokenize,mwt,pos,lemma', use_gpu=True)
    elif language == "Spanish":
        stanza.download("es")
        nlp     = spacy_stanza.load_pipeline("es", package="ancora", processors='tokenize,mwt,pos,lemma', use_gpu=True)
    else:
        nlp = None
    return nlp


def get_lemma_and_grammar_tag(marked_token: str, context: str, nlp, m_token_type: str) -> tuple:
    """Get the lemma and grammar tag for a marked token.

    Parameters
    ----------
    marked_token : str
        The marked token to be lemmatised and grammar-tagged.
    context : str
        The context that the marked token is in. This is simply the front-side text provided by the user.
    nlp : spacy_stanza object
        The language processor for the selected language. Used to lemmatise and grammar-tag the marked token.
    m_token_type : str
        Whether the marked token is a word or a phrase.

    Returns
    -------
    tuple
        The lemma and grammar tag for the marked token.
    """
    if m_token_type == "phrase":  # We don't need to lemmatise phrases
        lemma = marked_token.replace("#", "")
        return lemma, "Phrase"
    
    marked_token  = strip_punctuation(marked_token)
    context = strip_punctuation(context)
    lemmas  = {}
    grammar_tags = {}
    
    text = nlp(context)
    for token in text:
        lemmas[token.text] = token.lemma_
        grammar_tags[token.text] = token.pos_    
    
    lemma = lemmas[marked_token]
    grammar_tag = grammar_tags[marked_token]
    
    return lemma, grammar_tag


def strip_punctuation(text: str) -> str:
    """Remove punctuation from a string.
    Remove apostrophes in the middle of words, but ensure a space is put in their place. 
    This is needed for French so that the lemmatiser doesn't tokenise words with their contracted articles.
    Also removes the asterisks and hashtags used to mark tokens.

    Parameters
    ----------
    text : str
        Either an individual word/phrase or the context that the word/phrase is in. Both must be stripped of
        punctuation.

    Returns
    -------
    str
        The text with punctuation removed.
    """
    new_text = ''
    for i in range(len(text)):
        if text[i] == "'":
            if i > 0 and i < len(text) - 1:
                # Check if the character is surrounded by alphabetical characters.
                if text[i-1].isalpha() and text[i+1].isalpha():
                    new_text += ' '
                    continue
        new_text += text[i]

    # Remove other punctuation
    exclude = set(string.punctuation) - {"'"}
    for ch in exclude:
        new_text = new_text.replace(ch, '')
    
    return ' '.join(new_text.split())


def make_tags_readable(cards_arr: list) -> list:
    """Converts the grammar tags from the Spacy format to a readable format. This is done mainly for the benefit of
    easily saving readable grammar tags to the Anki file, but also makes debugging easier.

    Parameters
    ----------
    cards_arr : list
        Array of dictionaries. Each dictionary holds the data for an individual card.

    Returns
    -------
    list
        Array of dictionaries with the grammar tags converted to a readable format.
    """
    new_cards_arr = cards_arr
    for card_i, card in enumerate(cards_arr):
        for bside_entry_key, bside_entry_d in card["backside_entries"].items():
            tag = bside_entry_d["grammar_tag"]
            for spacy_tag, readable_tag in SPACY_TO_NLTK_TAG_MAP.items():
                if spacy_tag == tag:
                    new_tag = readable_tag
                    new_cards_arr[card_i]["backside_entries"][bside_entry_key]["grammar_tag"] = new_tag
                    break
    return new_cards_arr


def remove_irrelevant_defs(cards_arr: list) -> list:
    """Removes irrelevent definitions for a card. This is done by matching the grammar tag of the marked token with
    the grammar tag of a definition. If the tags match, the definition is kept by adding it to the relv_defs card entry.
    Relevant definitions are used for the Anki card and all others are ignored. This is done to reduce information
    overload on the card: only the definitions for this gramamtical context are used.
    
    Parameters
    ----------
    cards_arr : list
        Array of dictionaries. Each dictionary holds the data for an individual card.

    Returns
    -------
    list
        Array of dictionaries with relv_defs entries added to each card's backside_entries dictionary.
    """
    new_c_arr = cards_arr
    for card_i, card in enumerate(cards_arr):        
        for bside_entry_key, bside_entry in card["backside_entries"].items():
            raw_defs    = bside_entry["all_defs"]
            grammar_tag = bside_entry["grammar_tag"]
            target_type = bside_entry["target_type"]
            relv_defs   = []
            
            relv_def_found = False
            if target_type == "word" and raw_defs:  # raw_defs is false if no defs found during on wik
                for def_grammarkey, definition in raw_defs.items():
                    if not relv_def_found and definition and def_grammarkey == grammar_tag:
                        relevant_def  = definition
                        relv_defs     = relevant_def
                        relv_def_found = True
            
            if (not relv_def_found or target_type == "phrase") and raw_defs != None:  # Use the longest definition available
                longest = max(raw_defs.values(), key=len)
                if target_type == "word":
                    longest.append(f"Note: using {grammar_tag} def.")
                relv_defs = longest
            
            elif raw_defs == None:
                relv_defs = ["No definition found."]
    
            new_c_arr[card_i]["backside_entries"][bside_entry_key]["relv_defs"] = relv_defs
    return new_c_arr



def format_card(card: dict, deck_name: str) -> str:
    """Formats a card's data for usage in Anki. An Anki import requires three columns: frontside, backside, and deck.
    Frontside: the original text line provided by the user (with token tags removed).
    Backside: the text displaying word/phrase definitions and additional information.
    Deck: the name of the deck the cards should be added to.

    Parameters
    ----------
    card : dict
        Dictionary holding all the relevant data for an individual card.
    deck_name : str
        Name of the Anki deck.

    Returns
    -------
    str
        Anki-formatted import text for an individual card. 
        * Note that this is for an individual card, and the string provided by the function must be concatenated to a 
            central string containing all the cards.
    """
    fside_text = card["frontside_text"]
    
    # Remove the "*" keyword marker(s) and bold them with html tags
    pattern = r"\*\w+"
    bolded_text = re.sub(pattern, lambda x: f"<b>{x.group()[1:]}</b>", fside_text)
    pattern_phrase = r"#(.*?)#"
    bolded_text = re.sub(pattern_phrase, lambda x: f"<b>{x.group()[1:]}</b>", bolded_text)
    bolded_text = bolded_text.replace("#", "")
    
    # == Column 1 == Frontside
    ankified_text = bolded_text + ";\""
    
    # == Column 2 == Backside
    for entry_i, entry in enumerate(card["backside_entries"].values()):
        if entry_i > 0:  # Add a horizontal rule between entries
                ankified_text += "<hr style='border: 1px dotted dimgrey;'>"        
        tag = entry["grammar_tag"]
        lemma = entry["lemma"]
        ankified_text += f"<h3>{lemma}</h3>{tag}"  
        # Format each line of the definition
        for line_no, string in enumerate(entry["relv_defs"]):
            if line_no == 0:  # The first line is not a definition, but grammatical/additional info
                split_def = string.split()
                split_def = " ".join(split_def[1:])  # Remove the first word, which is the word itself
                if len(split_def) > 0:
                    ankified_text += f", <i>{split_def}</i>"
            elif line_no == 1:  # Start of defs, open ordered list
                ankified_text += "<ol>"
                ankified_text += f"<li>{string}</li>"
            else:
                ankified_text += f"<li>{string}</li>"
        ankified_text += "</ol>"
        ankified_text += "\";"
    
    # == Column 3 == Deck
    ankified_text += f"deck:{deck_name}"
    ankified_text  = ankified_text.replace("\n", "<br>")
    ankified_text  = ankified_text.replace("</h3><br><br>", "</h3>")
    ankified_text  = ankified_text.replace("(", "<span style='font-size:0.75em;'><i>")
    ankified_text  = ankified_text.replace(")", "</i></span>")
        
    return ankified_text


def export_cards(full_file_path: str, anki_input: str) -> bool:
    """Export the Anki cards to a text file.

    Parameters
    ----------
    full_file_path : str
        Path used to save the finalised Anki import file.
    anki_input : str
        Text used for the Anki import file.

    Returns
    -------
    bool
        Whether the export was successful.
    """
    try:
        with open(full_file_path, 'w', encoding="utf-8") as file:
            file.write(anki_input)
        return True
    except Exception as e:
        print(e)
        return False


def feed_msg_queue(message: str, messageQueue, total_cards=None, card_num=None, file_path=None) -> None:
    """Feed a message to the message queue. Used to send updates to the front-end.
    Messages should be non-technical and written in plain language.

    Parameters
    ----------
    message : str
        Key used to select the message.
    messageQueue : MessageQueue object
        Message queue object sent from the front-end.
    total_cards : int, optional
        Total cards being created, by default None
    card_num : int, optional
        Current card index being worked on, by default None
    file_path : str, optional
        Path the the finalised Anki import file is saved to, by default None
    """
    q_msgs = {
        "start"          : "AutoAnki Started.",
        "file_error"     : "Error reading file. Please close this window, check the file, and try again.",
        "keywords"       : "Finding keywords.",
        "lang_processor" : "Preparing language processor. This may take a moment, please wait.",
        "making_cards"   : f"Making {str(total_cards)} cards.",
        "card_progress"  : f"Getting Wikti data for card {str(card_num)}/{str(total_cards)}...",
        "processing"     : "Processing cards.",
        "cleaning"       : "Cleaning cards.",
        "formatting"     : "Formatting cards.",
        "saved"          : f"File saved to {file_path}",
        "save_error"     : f"Error saving file to {file_path}",
        "done"           : "You can now close this window."
    }
    
    messageQueue.put(q_msgs[message])