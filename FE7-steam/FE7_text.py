import obspython as obs
import os
import inspect
import json


# Global variables for locale objects
source_name    = "FE_GBA_rules"
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

# Global variables for scroll effect
next_line     = 0
next_char     = 0
time_per_char = 15
display_time  = 5000


def script_description():
    return f"""Fire Emblem GBA-style text scroll
               Create a text source called \"{source_name}\",
               with a scroll filter called \"{filter_name}\".
               Add rule set to local file called \"{text_file_name}\",
               in the same location as this script"""


def remove_rules():
    global rules_data, rules_filter_data

    obs.timer_remove(rules_scrolling)
    obs.timer_remove(rules_line_type)
    obs.timer_remove(rules_wipe_effect)

    # Reset text
    if rules_data:
        set_rules_text("Whoops, something's gone wrong! Well, this is awkward ^_^'")
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
    sources = obs.obs_enum_sources()
    for source in sources:
        if source_name == obs.obs_source_get_name(source):
            rules_source = source
            break
    obs.source_list_release(sources)

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

    # Testing - check data
    json_t = json.loads(obs.obs_data_get_json(rules_data))
    json_s = json.loads(obs.obs_data_get_json(rules_filter_data))
    print(f"{json_t}\n{json_s}")

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


def script_update(setting):
    reset_rules_variables()

def script_load(setting):
    reset_rules_variables()

def script_unload():
    remove_rules()


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


