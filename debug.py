import savefiles


def encoder_decoder_test() -> None:
    print("\n\n=== Testing encoder ===")
    
    unencoded_data = savefiles.UnencodedSavefilesContent(English="Hello", French="Bonjour", German="Hallo", Latin="Salve", 
                                                Spanish="Hola")
    
    print(f"\n-- Unencoded Data --\n{unencoded_data}\nEnglish: {unencoded_data.English}")    
    
    encoded_data = savefiles.encode_savefiles_content(unencoded_data)
    print(f"\n-- Encoded Data --\n{encoded_data}\nEnglish: {encoded_data.English}")
    
    decoded_data = savefiles.decode_savefiles_content(encoded_data)
    print(f"\n-- Decoded Data --\n{decoded_data}\nEnglish: {decoded_data.English}\n\n")