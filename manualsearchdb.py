from enum           import Enum
from dataclasses    import (dataclass, asdict)
from typing         import (Tuple, Union, Optional)
import uuid
import pprint


@dataclass
class SearchType(Enum):
    WORD                = 1
    CONJUGATION         = 2
    PHRASE              = 3
    WORD_CONJ_COMBO     = 4


@dataclass(frozen=True, order=True)
class ItemDefinitions:
    """A dictionary containing the definitions for a word/phrase. Keys represent a grammar tag, and values are the 
    corresponding definitions.
    """
    noun            : Optional[Tuple[str, ...]]
    verb            : Optional[Tuple[str, ...]]
    adjective       : Optional[Tuple[str, ...]]
    adverb          : Optional[Tuple[str, ...]]
    pronoun         : Optional[Tuple[str, ...]]
    preposition     : Optional[Tuple[str, ...]]
    particle        : Optional[Tuple[str, ...]]
    conjunction     : Optional[Tuple[str, ...]]
    article         : Optional[Tuple[str, ...]]
    numeral         : Optional[Tuple[str, ...]]
    interjection    : Optional[Tuple[str, ...]]
    exclamation     : Optional[Tuple[str, ...]]
    determiner      : Optional[Tuple[str, ...]]
    etymology       : Optional[Tuple[str, ...]]
    usage           : Optional[Tuple[str, ...]]


class ManualSearchItemsDb:
    """A database of ManualSearchItem objects, which hold information about a word/phrase.
    """
    def __init__(self):
        self.items = {}
    
    def __str__(self) -> str:
        return pprint.pformat(self.items)
    
    def init_new_item(self, language: str, search_tokens: Tuple[str, ...], 
                                search_type: SearchType) -> str:
        """Initialises a new ManualSearchItem object and adds it to the database.

        Arguments:
            language -- Language of the search item
            search_tokens -- Items to search for on Wiktionary 
            search_type -- Type of search(s) to perform
        """
        new_item_uid = self.create_search_item_uid()
        
        new_item = ManualSearchItem(new_item_uid, language, search_tokens, search_type)
        self.items[new_item_uid] = new_item
        
        return new_item_uid
    
    def create_search_item_uid(self) -> str:
        """Creates a unique ID for a ManualSearchItem object.

        Returns:
            Unique ID from uuid1
        """
        unique_id = str(uuid.uuid1(node=None, clock_seq=None))
        return unique_id


class ManualSearchItem:
    """Holds information about a word/phrase that a user has manually searchhed for.
    """
    def __init__(self, search_item_uid: str, language: str, search_tokens: Tuple[str, ...], search_type: SearchType):
        self.uid                        = search_item_uid
        self.language                   = language
        self.search_tokens              = search_tokens
        self.search_type                = search_type
        self.raw_definitions            : ItemDefinitions
        self.raw_html_table             : str
        self.unwrapped_html_construct   : str
    
    def __str__(self) -> str:
        str  = f"uid: {self.uid}\n"
        str += f"language: {self.language}\n"
        str += f"search_tokens: {', '.join(self.search_tokens)}\n"
        str += f"search_type: {self.search_type.name}\n"
        
        if hasattr(self, 'raw_definitions'):
            str += f"Raw definitions: {self.__get_optional_attr_str(self.raw_definitions)}"
        if hasattr(self, 'raw_html_table'):
            str += self.__get_optional_attr_str(self.raw_html_table)
        if hasattr(self, 'finalised_item_html'):
            str += self.__get_optional_attr_str(self.unwrapped_html_construct)
        return str
    
    def add_raw_defs(self, raw_definitions: ItemDefinitions) -> None:
        self.raw_definitions = raw_definitions
    
    def add_raw_table(self, raw_html_table: str) -> None:
        self.raw_html_table = raw_html_table
    
    def add_unwrapped_html(self, unwrapped_html_construct: str) -> None:
        self.unwrapped_html_construct = unwrapped_html_construct
    
    def __get_optional_attr_str(self, attribute: Union[str, ItemDefinitions]) -> str:
        """Returns a string representation of an attribute if it exists.

        Arguments:
            attribute -- Attribute of which to get a string representation

        Returns:
            String representation of the attribute
        """
        print_str_additions = ""
        if type(attribute) is ItemDefinitions:
            attr_dict = asdict(attribute)
            for gramamr_tag, definition in attr_dict.items():
                if definition != None:
                    print_str_additions += f"\n    {gramamr_tag}: {definition}"
        else:
            print_str_additions += f"\n{attribute}"
        return print_str_additions