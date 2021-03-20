import obspython as obs
import os
import inspect
import json

# Global variables for locale objects
source_name    = ""
filter_name    = "Scroll"
location       = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
text_file_name = "rule_set.txt"
text_file      = f"{location}/{text_file_name}"

# Global variables for rules source
rules_source        = None
rules_data          = None
rules_filter_source = None
rules_filter_data   = None
rules_list          = ""

# Global variables for arrow gif source
arrow_name   = "Arrow"
arrow_source = None

# Global variables for scroll effect
next_line     = 0
next_char     = 0
time_per_char = 15
display_time  = 7000


def script_description():
    return f"""Fire Emblem GBA-style text scroll
               Create a text source with a scroll filter called \"{filter_name}\".
               Add rule set to local file called \"{text_file_name}\",
               in the same location as this script"""

def get_text_of_source(source):
    ret_value = ""
    source_data = obs.obs_source_get_settings(source)
    data_json = obs.obs_data_get_json(source_data)
    if data_json:
        json_obj = json.loads(data_json)
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

# Called to display the properties GUI
def script_properties():
    props = obs.obs_properties_create()

    list_property = obs.obs_properties_add_list(props, "source_name", "Source name", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
    populate_list_property_with_source_names(list_property)

    return props

def script_update(settings):
    global source_name

    source_name = obs.obs_data_get_string(settings, "source_name")
    reset_rules_variables()

def script_load(settings):
    reset_rules_variables()


def remove_rules():
    global rules_data, rules_filter_data

    obs.timer_remove(rules_scrolling)
    obs.timer_remove(rules_line_type)
    obs.timer_remove(rules_wipe_effect)

    # Reset text
    if rules_data:
        set_rules_text("Whoops, something's gone wrong! Well, this is awkward...")
        set_scroll_speed(0)
        obs.obs_data_release(rules_data)
        obs.obs_data_release(rules_filter_data)


def reset_rules_variables():
    global source_name, filter_name, text_file
    global rules_source, rules_data, rules_list
    global rules_filter_source, rules_filter_data
    global next_line, next_char, time_per_char, display_time

    remove_rules()
    ok = True

    # Get rule set from local file
    with open(text_file) as f:
        rules_list = f.read().splitlines()

    # Get source
    if ok and source_name:
        sources = obs.obs_enum_sources()
        for source in sources:
            if source_name == obs.obs_source_get_name(source):
                rules_source = source
                break
        obs.source_list_release(sources)
    else:
        ok = False

    if ok and rules_source:
        # Get source data
        rules_data = obs.obs_source_get_settings(rules_source)

        # Get filter source
        rules_filter_source = obs.obs_source_get_filter_by_name(rules_source, filter_name)
    else:
        print(f"Couldn't find source {source_name}")
        ok = False

    if ok and rules_filter_source:
        # Get filter data
        rules_filter_data = obs.obs_source_get_settings(rules_filter_source)

        # Other settings
        set_rules_text(rules_list[0])
        next_line = 1
        next_char = 1
    else:
        print(f"Couldn't find filter {filter_name}")
        ok = False

    # Set timer for scrolling effect
    if ok:
        line_lens = sorted(set([len(x) for x in rules_list]))
        max_len = line_lens[-1]
        full_time = ((max_len * 2) * time_per_char) + display_time
        obs.timer_add(rules_scrolling, full_time)


def set_rules_text(text):
    global rules_source, rules_data
    obs.obs_data_set_string(rules_data, "text", f"{text}\n\n")
    obs.obs_source_update(rules_source, rules_data)


def set_scroll_speed(speed):
    global rules_filter_source, rules_filter_data
    obs.obs_data_set_int(rules_filter_data, "speed_y", speed)
    obs.obs_source_update(rules_filter_source, rules_filter_data)


# First, scroll text upwards off screen
def rules_scrolling():
    set_scroll_speed(500)

    obs.timer_add(rules_line_type, 700)


# Then, blank text and stop scrolling
def rules_line_type():
    global time_per_char

    set_rules_text("")
    set_scroll_speed(0)
    obs.timer_remove(rules_line_type)

    obs.timer_add(rules_wipe_effect, time_per_char)


# Finally, "type out" new line
def rules_wipe_effect():
    global rules_list, next_line, next_char

    text_line = rules_list[next_line]
    no_of_chars = len(text_line)

    if next_char > no_of_chars:
        next_char = 1
        next_line = (next_line + 1) % len(rules_list)
        obs.timer_remove(rules_wipe_effect)
    else:
        set_rules_text(text_line[:next_char])
        next_char += 1


