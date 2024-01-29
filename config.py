import os
import configparser

def config_check() -> list:
    """Checks if the config file exists, if not, creates it.

    Returns:
        A list of config variables.
    """
    if os.path.exists("config.ini"):
        pass
    else:
        setup_config()
    config_vars = get_configs()
    return config_vars


def setup_config() -> None:
    """Creates a config file with default values.
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
            return
    except:
        return


def get_configs() -> list:
    """Gets the config variables from the config file.
    
    Returns:
        List of config variables.
    """
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    interface_language                    = config['LanguagePreferences']['InterfaceLanauge']
    search_language                       = config['LanguagePreferences']['SearchLanguage']
    colour_mode                           = config['Interface']['ColourMode']
    zoom_level                            = int(config['Interface']['ZoomLevel'])
    show_tutorial_flag                    = config['Behaviour'].getboolean('ShowTutorial')
    get_etymology_flag                    = config['SearchSettings'].getboolean('GetEtymology')
    get_usage_notes_flag                  = config['SearchSettings'].getboolean('GetUsage')
    display_definitions_with_conjugations = config['SearchSettings'].getboolean('defInConj')
    default_note_location                 = config['DefaultLocations']['defaultNotesFile']
    default_output_folder                 = config['DefaultLocations']['defaultOutputFolder']
    
    config_vars = [
        interface_language, search_language, colour_mode, zoom_level, show_tutorial_flag, get_etymology_flag, 
        get_usage_notes_flag, display_definitions_with_conjugations, default_note_location, default_output_folder]
    
    return config_vars  