import stanza
import spacy_stanza
# Download the stanza model if necessary
stanza.download("de")

# Initialize the pipeline
nlp = spacy_stanza.load_pipeline("de", package="hdt", processors='tokenize,mwt,pos,lemma')


def get_lemma(target_word, context):
    """
    Returns the undeclined form of a delcined German word.
    
    :param adjective: The declined German word.
    :returns: The undeclined form of the word.
    """
    # Process the word using SpaCy
    lemmas = {}
    text = nlp(context)
    
    # Get all lemmas in text.
    for token in text:
        lemmas[token.text]  = token.lemma_
    
    for token in text:
        print()
        print(token.text, token.lemma_, token.pos_, token.dep_, token.ent_type_)

    print("\nLEMMAS")
    print(lemmas)
    
    # Get the lemma of the target word.
    lemma = lemmas[target_word]
    
    print(f"Undeclined {target_word}: < {lemma} >")
    
    return lemma


lemma = get_lemma("schöner", "Das ist ein schöner Tag.")
print(f"Lemma: {lemma}")