from base64         import (b64encode, b64decode)
from dataclasses    import (dataclass, asdict)


IMPLEMENTED_LANGUAGES = ["English", "French", "German", "Latin", "Spanish"]


@dataclass(frozen=True, order=True)
class EncodedSavefilesContent:
    """A string encoded with base64 holding the content of saved search terms.
    """
    English : bytes
    French  : bytes
    German  : bytes
    Latin   : bytes
    Spanish : bytes


@dataclass(frozen=True, order=True)
class UnencodedSavefilesContent:
    """Unencoded strings holding the content of saved search terms, retrieved from their corresponding .dat file.
    """
    English : str
    French  : str
    German  : str
    Latin   : str
    Spanish : str


def encode_savefiles_content(unencoded_savefiles_content: UnencodedSavefilesContent) -> EncodedSavefilesContent:
    """Encodes saved/pinned search term data using base64, the contents of which should be saved to their corresponding
    language .dat file. This is done to discourage the user potentially editing stuff.

    Args:
        unencoded_savefiles_content (UnencodedSavefilesContent): HTML content of saved/pinned search terms.

    Returns:
        EncodedSavefilesContent: Base64 encoded HTML content of saved/pinned search terms.
    """
    temp_encoded_dict = {}
    for language, unencoded_content in asdict(unencoded_savefiles_content).items():
        ascii_encoded_content = unencoded_content.encode("utf-8")
        b64_encoded_content = b64encode(ascii_encoded_content)
        temp_encoded_dict[language] = b64_encoded_content
    
    return EncodedSavefilesContent(**temp_encoded_dict)   


def decode_savefiles_content(encoded_savefiles_content: EncodedSavefilesContent) -> UnencodedSavefilesContent:
    """Decodes saved/pinned search term data from base64.

    Args:
        encoded_savefiles_content (EncodedSavefilesContent): Base64 encoded HTML content of saved/pinned search terms.

    Returns:
        UnencodedSavefilesContent: Usable HTML content of saved/pinned search terms.
    """
    temp_unencoded_dict = {}
    for language, encoded_content in asdict(encoded_savefiles_content).items():
        b64_decoded_content = b64decode(encoded_content)
        ascii_decoded_content = b64_decoded_content.decode("utf-8")
        temp_unencoded_dict[language] = ascii_decoded_content
    
    return UnencodedSavefilesContent(**temp_unencoded_dict)


def encode_single_entry(unencoded_entry: str) -> bytes:
    """Encodes a single entry using base64.

    Args:
        unencoded_entry (str): The entry to encode.

    Returns:
        bytes: The encoded entry. Note that this is a bytes object, not a string.
    """
    ascii_encoded_content = unencoded_entry.encode("utf-8")
    b64_encoded_content = b64encode(ascii_encoded_content)
    return b64_encoded_content