import obspython as obs


# Global variables for rules text
source_name         = "FE_GBA_rules"
filter_name         = "Scroll"
text_file           = "rule_set.txt"
rules_source        = None
rules_data          = None
rules_filter_source = None
rules_filter_data   = None
rules_list          = ""

# Global variables for scroll effect
next_line     = 0
time_per_char = 15
display_time  = 5000


def script_description():
    return f"Fire Emblem GBA-style text scroll
             Create a text source called \"{source_name}\", with a
             scroll filter called \"{filter_name}\n.
             Add rule set to local file called \"{text_file}\", in the same
             location as this script"


def reset_rules_variables:
    global source_name, filter_name, text_file
    global rules_source, rules_data, rules_list
    global rules_filter_source, rules_filter_data
    global next_line, time_per_char, display_time

    obs.timer_remove(rules_scrolling)

    # Reset text
    if rules_data:
        set_rules_text("")
        obs.obs_data_release(rules_data)

    # Get rule set from local file
    with open(text_file) as f:
        rules_list = f.read().splitline()

    # Get source
    sources = obs.obs_enum_sources()
    for source in sources:
        if source_name = obs.obs_source_get_name(source):
            rules_source = source
            break
    obs.source_list_release(sources)

    if rules_source:
        # Get source data
        rules_data = obs.obs_source_get_settings(rules_source)

        # Get filter source
        rules_filter_source = obs.obs_source_get_filter_by_name(rule_source, filter_name)
    else:
        exit(f"Couldn't find source {source_name}")

    if rules_filter_source:
        # Get filter data
        rules_filter_data = obs.obs_source_get_settings(rules_filter_source)

        # Other settings
        set_rules_text(rules_list[0])
        next_line = 1
    else:
        exit(f"Couldn't find filter {filter_name}")

    # Testing - check data
    speed_y = obs.obs_data_get_int(rules_filter_data, "speed_y")
    text_on = obs.obs_data_get_string(rules_data, "text")
    print(f"{text}, {speed_y}")
    exit(0)

    # Set timer for scrolling effect
    line_lens = sorted(set([len(x) for x in rules_list]))
    max_len = line_lens[-1]
    full_time = ((max_len * 2) * time_per_char) + display_time
    obs.timer_add(rules_scrolling, full_time)


def set_rules_text(text):
    global rules_source, rules_data
    obs.obs_data_set_string(rules_data, "text", f"{text}\n\n")
    obs.obs_source_update(rules_source, rules_data)


def script_update(setting):
    reset_rules_variables()


def rules_scrolling():
    global rules_source, rules_data
    global rules_filter_source, rules_filter_data
    global rules_list

    pass

