import obspython as obs
import math
import time

def script_description():
    return """Scroll with pauses
           OBS already supports scrolling, but doesn't allow for regular pauses during
           the scroll. This is particularly useful for giving the viewer enough time
           to read each line of a given text."""


# User Data Setting:
pause_after = 0
continue_after = 0

def script_defaults(settings):
    obs.obs_data_set_default_int(settings, "pause_after", 5)
    obs.obs_data_set_default_int(settings, "continue_after", 5)


# Called to display the properties GUI
def script_properties():
    props = obs.obs_properties_create()

    obs.obs_properties_add_int(props, "pause_after", "Pause after", 0, 8192, 1)
    obs.obs_properties_add_int(props, "continue_after", "Continue after", 0, 8192, 1)

    return props


# Called after change of settings including once after script load
def script_update(settings):
    global pause_after, continue_after
#    restore_sceneitem_after_shake()
    pause_after = obs.obs_data_get_int(settings, "pause_after")
    continue_after = obs.obs_data_get_int(settings, "continue_after")


source_name = "Rules"
filter_name = "Scroll"
currently_scrolling = False
time_passed = 0

def script_tick(seconds):
    global source_name, filter_name
    global currently_scrolling, time_passed

    cond1 = currently_scrolling and time_passed >= pause_after
    cond2 = not currently_scrolling and time_passed >= continue_after
    if cond1 or cond2:

        source_item = obs.obs_get_source_by_name(source_name)

        if source_item:
            filter_item = obs.obs_source_get_filter_by_name(source_item, filter_name)
            filter_data = obs.obs_source_get_settings(filter_item)

            if cond1:
                obs.obs_data_set_int(filter_data, "speed_y", 1)
                obs.obs_source_update(filter_item, filter_data)
                currently_scrolling = False
                time_passed = -1
            elif cond2:
                obs.obs_data_set_int(filter_data, "speed_y", 100)
                obs.obs_source_update(filter_item, filter_data)
                currently_scrolling = True
                time_passed = -1

            obs.obs_data_release(filter_data)
            obs.obs_source_release(filter_item)

        obs.obs_source_release(source_item)

    time_passed += 1


def script_load(settings):
    global source_name, filter_name

    source_item = obs.obs_get_source_by_name(source_name)

    if source_item:
        filter_item = obs.obs_source_get_filter_by_name(source_item, filter_name)
        filter_data = obs.obs_source_get_settings(filter_item)

        obs.obs_data_set_int(filter_data, "speed_y", 0)
        obs.obs_source_update(filter_item, filter_data)

        obs.obs_data_release(filter_data)
        obs.obs_source_release(filter_item)

    obs.obs_source_release(source_item)

