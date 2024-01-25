from base64         import (b64encode, b64decode)
from dataclasses    import (dataclass, asdict)


IMPLEMENTED_LANGUAGES = ["English", "French", "German", "Latin", "Spanish"]


@dataclass(frozen=True, order=True)
class EncodedSavefilesContent:
    English : bytes
    French  : bytes
    German  : bytes
    Latin   : bytes
    Spanish : bytes


@dataclass(frozen=True, order=True)
class UnencodedSavefilesContent:
    English : str
    French  : str
    German  : str
    Latin   : str
    Spanish : str


def encode_savefiles_content(unencoded_savefiles_content: UnencodedSavefilesContent) -> EncodedSavefilesContent:
    temp_encoded_dict = {}
    for language, unencoded_content in asdict(unencoded_savefiles_content).items():
        ascii_encoded_content = unencoded_content.encode("utf-8")
        b64_encoded_content = b64encode(ascii_encoded_content)
        temp_encoded_dict[language] = b64_encoded_content
    
    return EncodedSavefilesContent(**temp_encoded_dict)   


def decode_savefiles_content(encoded_savefiles_content: EncodedSavefilesContent) -> UnencodedSavefilesContent:
    temp_unencoded_dict = {}
    for language, encoded_content in asdict(encoded_savefiles_content).items():
        b64_decoded_content = b64decode(encoded_content)
        ascii_decoded_content = b64_decoded_content.decode("utf-8")
        temp_unencoded_dict[language] = ascii_decoded_content
    
    return UnencodedSavefilesContent(**temp_unencoded_dict)


def encode_single_entry(unencoded_entry: str) -> bytes:
    ascii_encoded_content = unencoded_entry.encode("utf-8")
    b64_encoded_content = b64encode(ascii_encoded_content)
    return b64_encoded_content


def encoder_decoder_test() -> None:
    print("\n\n=== Testing encoder ===")
    
    unencoded_data = UnencodedSavefilesContent(English="Hello", French="Bonjour", German="Hallo", Latin="Salve", Spanish="Hola")
    print(f"\n-- Unencoded Data --\n{unencoded_data}\nEnglish: {unencoded_data.English}")    
    
    encoded_data = encode_savefiles_content(unencoded_data)
    print(f"\n-- Encoded Data --\n{encoded_data}\nEnglish: {encoded_data.English}")
    
    decoded_data = decode_savefiles_content(encoded_data)
    print(f"\n-- Decoded Data --\n{decoded_data}\nEnglish: {decoded_data.English}\n\n")