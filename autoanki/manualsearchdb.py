from enum           import Enum
from dataclasses    import (dataclass, asdict)
from typing         import (Tuple, Union, Optional)
from uuid           import uuid1
import uuid
import pprint


@dataclass
class SearchType(Enum):
    WORD            = 1
    CONJUGATION     = 2
    PHRASE          = 3
    WORD_CONJ_COMBO = 4


@dataclass(frozen=True, order=True)
class ItemDefinitions:
    """A dictionary containing the definitions for a word/phrase. Keys represent a grammar tag, and values are the 
    corresponding definitions.
    """
    noun        : Optional[Tuple[str, ...]] = None
    verb        : Optional[Tuple[str, ...]] = None
    adjective   : Optional[Tuple[str, ...]] = None
    adverb      : Optional[Tuple[str, ...]] = None
    pronoun     : Optional[Tuple[str, ...]] = None
    preposition : Optional[Tuple[str, ...]] = None
    particle    : Optional[Tuple[str, ...]] = None
    conjunction : Optional[Tuple[str, ...]] = None
    article     : Optional[Tuple[str, ...]] = None
    numeral     : Optional[Tuple[str, ...]] = None
    interjection: Optional[Tuple[str, ...]] = None
    exclamation : Optional[Tuple[str, ...]] = None
    determiner  : Optional[Tuple[str, ...]] = None
    etymology   : Optional[Tuple[str, ...]] = None
    usage       : Optional[Tuple[str, ...]] = None


class ManualSearchItem:
    """Holds information about a word/phrase that a user has manually searched for.
    """
    def __init__(self, search_language: str, search_tokens: Tuple[str, ...], search_type: SearchType, etymology_flag: bool,
            usage_notes_flag: bool):
        self.uid                     : str             = str(uuid1(node=None, clock_seq=None))
        self.search_language         : str             = search_language
        self.search_tokens           : Tuple[str, ...] = search_tokens
        self.search_type             : SearchType      = search_type
        self.etymology_flag          : bool            = etymology_flag
        self.usage_notes_flag        : bool            = usage_notes_flag
        self.raw_definitions         : ItemDefinitions
        self.raw_html_table          : str
        self.unwrapped_html_construct: str
    
    def __str__(self) -> str:
        str  = f"UID: {self.uid}\n"
        str += f"Search language: {self.search_language}\n"
        str += f"Search_tokens: {', '.join(self.search_tokens)}\n"
        str += f"Search_type: {self.search_type.name}\n"
        str += f"Unwrapped HTML: {self.unwrapped_html_construct}"
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
            attribute: Attribute of which to get a string representation

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