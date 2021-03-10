import obspython as obs
import json
import time

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
source_text_lines = []   # Line-separated list of source text

# User Data Setting:

def get_text_of_source(source):
    ret_value = ""
    source_data = obs.obs_source_get_settings(source)
    json_obj = json.loads(obs.obs_data_get_json(source_data))
    if "text" in json_obj:
        ret_value = json_obj["text"]
    obs.obs_data_release(source_data)

    return ret_value

def set_text_of_source(source, text):
    source_data = obs.obs_source_get_settings(source)
    obs.obs_data_set_string(source_data, "text", text)
    obs.obs_source_update(source, source_data)
    obs.obs_data_release(source_data)


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

    obs.obs_properties_add_int_slider(props, "char_add", "Time between each\ncharacter addition/removal", 15, 500, 1)
    obs.obs_properties_add_int_slider(props, "display_time", "Time line is displayed\nbefore being wiped", 15, 10000, 1)

    return props


# Called after change of settings including once after script load
def script_update(settings):
    global source_name, char_add, display_time, wipe_source, wipe_source_text, source_text_lines

    obs.timer_remove(wipe_effect_on_source)
    restore_text_pre_wipe()
    
    source_name = obs.obs_data_get_string(settings, "source_name")
    if source_name:
        wipe_source = get_source_from_source_name(source_name) 
        wipe_source_text = get_text_of_source(wipe_source)
        source_text_lines = wipe_source_text.split("\n")
        set_text_of_source(wipe_source, source_text_lines[0])

        char_add = obs.obs_data_get_int(settings, "char_add")
        display_time = obs.obs_data_get_int(settings, "display_time")

        line_lengths = sorted(set([len(x) for x in source_text_line]))
        max_1 = line_lengths[-1]
        max_2 = line_lengths[-2]
        full_time = ((max_1 + max_2) * char_add) + display_time
        obs.timer_add(wipe_effect_on_source, full_time)


# Callback for item_remove signal
def on_wipe_source_removed(calldata):
    restore_text_pre_wipe()

# Signal handler of source kept to restore
wipe_source_handler = None

# Restores the original text on the source item
def restore_text_pre_wipe():
    global source_name, wipe_source, wipe_source_text
    if source_name:
        source_data = obs.obs_source_get_settings(wipe_source)
        obs.obs_data_set_string(source_data, "text", wipe_source_text)
        obs.obs_source_update(wipe_source, source_data)
        obs.obs_data_release(source_data)

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


# Global variables to track wipe effect
curr_line = 0

def wipe_effect_on_source():
    global source_text_lines, curr_line

    no_of_lines = len(source_text_lines)

    if curr_line = no_of_lines - 1:
        wipe_text_line_into_next(source_text_lines[curr_line], source_text_lines[0])
        curr_line = 0
    else:
        wipe_text_line_into_next(source_text_lines[curr_line], source_text_lines[curr_line + 1])
        curr_line += 1


def wipe_text_line_into_next(line_before, line_after):
    global wipe_source, char_add

    list_before = line_before.split()
    for _ in line_before:
        list_before.pop()
        set_text_of_source(wipe_source, "".join(list_before))
        time.sleep(char_add / 1000)

    list_after = line_after.split()
    new_line_list = []
    for _ in line_after:
        new_line_list.append(list_after.pop(0))
        set_text_of_source(wipe_source, "".join(new_line_list))
        time.sleep(char_add / 1000)


def script_load(settings):
    sources = obs.obs_enum_sources()
    for source in sources:
        print(get_text_of_source(source))
    obs.source_list_release(sources)

# Called at script unload
def script_unload():
    restore_text_pre_wipe()


# Called before data settings are saved
def script_save(settings):
    restore_text_pre_wipe()
    obs.obs_save_sources()

