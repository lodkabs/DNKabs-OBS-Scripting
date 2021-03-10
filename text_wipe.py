import obspython as obs
import json

def script_description():
    return """Text wipe
           Remove and replace individual lines of text with a wipe effect.
           Each line is determined by carriage return separation."""

# Global variables holding the values of data settings / properties
source_name      = ""   # Name of Text source to wipe
char_add         = 0    # Time between each letter addition/removal
display_time     = 0    # Time text line is displayed before being wiped
wipe_source      = None # Reference to the modified source item
wipe_source_text = ""   # Initial text in source item

# User Data Setting:

def get_text_of_source(source):
    ret_value = ""
    source_data = obs.obs_source_get_settings(source)
    json_obj = json.loads(obs.obs_data_get_json(source_data))
    if "text" in json_obj:
        ret_value = json_obj["text"]
    obs.obs_data_release(source_data)

    return ret_value

def populate_list_property_with_source_names(list_property):
    obs.obs_property_list_clear(list_property)
    obs.obs_property_list_add_string(list_property, "", "")

    sources = obs.obs_enum_sources()
    for source in sources:
        # Restrict selectable source list to Text objects
        if get_text_of_source(source):
            name = obs.obs_source_get_name(source)
            obs.obs_property_list_add_string(list_property, name, name)
    obs.source_list_release(sources)

def script_defaults(settings):
    obs.obs_data_set_default_string(settings, "source_name", "")
    obs.obs_data_set_default_int(settings, "char_add", 50)
    obs.obs_data_set_default_int(settings, "display_time", 200)

# Called to display the properties GUI
def script_properties():
    props = obs.obs_properties_create()

    list_property = obs.obs_properties_add_list(props, "source_name", "Source name", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
    populate_list_property_with_source_names(list_property)
    # Button to refresh the drop-down list
    obs.obs_properties_add_button(props, "button", "Refresh list of sources", lambda props, prop: True if populate_list_property_with_source_names(list_property) else True)

    obs.obs_properties_add_int_slider(props, "char_add", "Time between each character addition/removal", 1, 500, 1)
    obs.obs_properties_add_int_slider(props, "display_time", "Time line is displayed before being wiped", 0, 1000, 1)

    return props


# Called after change of settings including once after script load
def script_update(settings):
    global source_name, char_add, display_time, wipe_source, wipe_source_text
    
    source_name = obs.obs_data_get_string(settings, "source_name")
    if source_name:
        wipe_source = get_source_from_source_name(source_name) 
        wipe_source_text = get_text_of_source(wipe_source)

    char_add = obs.obs_data_get_int(settings, "char_add")
    display_time = obs.obs_data_get_int(settings, "display_time")


# Callback for item_remove signal
def on_wipe_source_removed(calldata):
    restore_text_after_wipe()

# Signal handler of source kept to restore
wipe_source_handler = None

# Restores the original text on the source item
def restore_text_after_wipe():
    global source_name, wipe_source, wipe_source_text
    if source_name:
        source_data = obs.obs_source_get_settings(wipe_source)
        obs.obs_data_set_string(source_data, "text", wipe_source_text)
        obs.obs_source_update(wipe_source, source_data)

        obs.signal_handler_disconnect(wipe_source_handler, "item_remove", on_wipe_source_removed)
        wipe_source = None

def get_source_from_source_name(name):
    result_sourceitem = None
    sources = obs.obs_enum_sources()
    for source in sources:
        if name == obs.obs_source_get_name(source):
            result_sourceitem = source
            break

    return result_sourceitem


def wipe_source():
    pass

def script_load(settings):
    sources = obs.obs_enum_sources()
    for source in sources:
        print(get_text_of_source(source))
    obs.source_list_release(sources)

# Called at script unload
def script_unload():
    restore_text_after_wipe()


# Called before data settings are saved
def script_save(settings):
    restore_text_after_wipe()
    obs.obs_save_sources()

