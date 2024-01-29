import savefiles
from manualsearchdb import *
import pprint

def encoder_decoder_test() -> None:
    print("\n\n=== Testing encoder ===")
    
    unencoded_data = savefiles.UnencodedSavefilesContent(English="Hello", French="Bonjour", German="Hallo", 
                                                            Latin="Salve", Spanish="Hola")
    
    print(f"\n-- Unencoded Data --\n{unencoded_data}\nEnglish: {unencoded_data.English}")    
    
    encoded_data = savefiles.encode_savefiles_content(unencoded_data)
    print(f"\n-- Encoded Data --\n{encoded_data}\nEnglish: {encoded_data.English}")
    
    decoded_data = savefiles.decode_savefiles_content(encoded_data)
    print(f"\n-- Decoded Data --\n{decoded_data}\nEnglish: {decoded_data.English}\n\n")


if __name__ == "__main__":
    search_items_db = ManualSearchItemsDb()
    
    language = "German"
    search_tokens = ("befindet", "Test")
    def_1 = ("To be located somewhere", "To find oneself somewhere",)
    def_2 = ("This isn't a preposition! Ignore me!",)
    definitions = ItemDefinitions(noun=def_1, preposition=def_2)
    search_type = SearchType.WORD
    
    uid = search_items_db.init_new_item(language, search_tokens, search_type)
    search_items_db.items[uid].add_raw_definitions(definitions)
    
    search_tokens = ("test string",)
    search_type = SearchType.WORD_CONJ_COMBO
    search_items_db.init_new_item("English", search_tokens, search_type)
    
    print(f"\nwiki_items in DB:\n{search_items_db}")
    for search_item in search_items_db.items.values():
        print(f"\nsearch_item:\n{search_item}")
    
    print()