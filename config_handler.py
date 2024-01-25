import os
import configparser

def config_check() -> list:
    """Checks if the config file exists, if not, creates it.

    Returns
    -------
    list
        A list of config variables.
    """
    if os.path.exists("config.ini"):
        pass
    else:
        setup_config()
    config_vars = get_configs()
    return config_vars


def setup_config():
    """Creates a config file with default values.

    Returns
    -------
    bool
        Whether the config file was successfully created.
    """
    config = configparser.ConfigParser()
    config['LanguagePreferences'] = {'InterfaceLanauge': 'English', 'SearchLanguage': 'English'}
    config['Interface']           = {'ColourMode': 'light', 'ZoomLevel': '100'}
    config['Behaviour']           = {'ShowTutorial': 'True'}
    config['ManualSearch']        = {'Etymology': 'False', 'UsageNotes': 'False', 'defInConj': 'False'}
    config['DefaultLocations']    = {'defaultNotesFile': 'False', 'defaultOutputFolder': 'False'}
    
    try:
        with open("config.ini", 'w') as configfile:
            config.write(configfile)
            return True
    except:
        return False


def get_configs():
    """Gets the config variables from the config file.

    Returns
    -------
    list
        A list of config variables.
    """
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    interface_language    = config['LanguagePreferences']['InterfaceLanauge']
    search_language       = config['LanguagePreferences']['SearchLanguage']
    colour_mode           = config['Interface']['ColourMode']
    zoom_level            = int(config['Interface']['ZoomLevel'])
    show_tutorial         = config['Behaviour']['ShowTutorial']
    get_etymology         = config['SearchSettings']['GetEtymology']
    get_usage_notes       = config['SearchSettings']['GetUsage']
    bold_key              = config['SearchSettings']['defInConj']
    default_note_location = config['DefaultLocations']['defaultNotesFile']
    default_output_folder = config['DefaultLocations']['defaultOutputFolder']
    
    config_vars = [
        interface_language, search_language, colour_mode, zoom_level, show_tutorial, get_etymology, get_usage_notes, 
        bold_key, default_note_location, default_output_folder]
    
    return config_vars  