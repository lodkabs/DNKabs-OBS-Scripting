import obspython as obs
import re
import json
import ctypes

EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible

# Global variables
source_name     = ""
selected_window = None
title_name      = ""
title_source    = None
titles          = []
prefix_number   = True

def script_description():
    return """Show the title of a window
           Select a text source and a Windows...window, the title of the window
           will appear in the selected text source.
           Some windows will have bracketed numbers in the title, e.g. (1),
           there's an option to remove that.
           """

def foreach_window(hwnd, lParam):
    global titles

    if IsWindowVisible(hwnd):
        length = GetWindowTextLength(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        GetWindowText(hwnd, buff, length + 1)
        titles.append([hwnd, buff.value])
    return True

def get_source_from_source_name(name):
    result_sourceitem = None
    sources = obs.obs_enum_sources()
    for source in sources:
        if name == obs.obs_source_get_name(source):
            result_sourceitem = source
            break

    obs.source_list_release(sources)

    return result_sourceitem

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
        name = obs.obs_source_get_name(source)
        obs.obs_property_list_add_string(list_property, name, name)
    obs.source_list_release(sources)

def populate_list_property_with_window_titles(title_list):
    global titles

    del titles[:]

    obs.obs_property_list_clear(title_list)
    obs.obs_property_list_add_string(title_list, "", "")

    EnumWindows(EnumWindowsProc(foreach_window), 0)

    titles_set = {t[1] for t in titles}

    for title in titles_set:
        obs.obs_property_list_add_string(title_list, title, title)


def script_defaults(settings):
    obs.obs_data_set_default_string(settings, "source_name", "")
    obs.obs_data_set_default_string(settings, "title_name", "")
    obs.obs_data_set_default_bool(settings, "source_name", True)

def script_properties():
    props = obs.obs_properties_create()

    list_property = obs.obs_properties_add_list(props, "source_name", "Source name", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
    populate_list_property_with_source_names(list_property)

    title_list = obs.obs_properties_add_list(props, "title_name", "Window title", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
    populate_list_property_with_window_titles(title_list)

    # Button to refresh the drop-down lists
    obs.obs_properties_add_button(props, "button", "Refresh lists", lambda props, prop: True if populate_list_property_with_source_names(list_property) and populate_list_property_with_window_titles(title_list) else True)

    obs.obs_properties_add_bool(props, "prefix_number", "Remove bracketed number at start?")

    return props



def script_update(settings):
    global source_name, title_source, titles, title_name, prefix_number, selected_window

    obs.timer_remove(set_title_text)
    source_name = obs.obs_data_get_string(settings, "source_name")
    title_name = obs.obs_data_get_string(settings, "title_name")
    prefix_number = obs.obs_data_get_bool(settings, "prefix_number")

    if source_name and title_name:
        title_source = get_source_from_source_name(source_name)

        if prefix_number:
            title_name = re.sub('^\(\d+\)\s+', '', title_name)

        set_text_of_source(title_source, title_name)

        for t in titles:
            if t[1] == title_name:
                selected_window = t[0]

        obs.timer_add(set_title_text, 100)


def set_title_text():
    global title_source, title_name, prefix_number, selected_window

    length = GetWindowTextLength(selected_window)
    buff = ctypes.create_unicode_buffer(length + 1)
    GetWindowText(selected_window, buff, length + 1)

    new_title = buff.value

    if prefix_number:
        new_title = re.sub('^\(\d+\)\s+', '', new_title)

    if title_name != new_title:
        title_name = new_title
        set_text_of_source(title_source, title_name)


