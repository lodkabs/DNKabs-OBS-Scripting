import obspython as obs
import json
import ctypes

EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible

# Global variables
source_name    = ""
title_name     = ""
title_source   = None
titles = []

def foreach_window(hwnd, lParam):
    global titles

    if IsWindowVisible(hwnd):
        length = GetWindowTextLength(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        GetWindowText(hwnd, buff, length + 1)
        titles.append(buff.value)
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

def populate_list_property_with_window_titles(title_list):
    global titles

    obs.obs_property_list_clear(title_list)
    obs.obs_property_list_add_string(title_list, "", "")

    EnumWindows(EnumWindowsProc(foreach_window), 0)

    for title in set(titles):
        obs.obs_property_list_add_string(title_list, title, title)


def script_defaults(settings):
    obs.obs_data_set_default_string(settings, "source_name", "")

def script_properties():
    props = obs.obs_properties_create()

    list_property = obs.obs_properties_add_list(props, "source_name", "Source name", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
    populate_list_property_with_source_names(list_property)
    # Button to refresh the drop-down list
    obs.obs_properties_add_button(props, "source_button", "Refresh list of sources", lambda props, prop: True if populate_list_property_with_source_names(list_property) else True)

    title_list = obs.obs_properties_add_list(props, "title_name", "Window title", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
    populate_list_property_with_window_titles(title_list)
    # Button to refresh the drop-down list
    obs.obs_properties_add_button(props, "title_button", "Refresh list of windows", lambda props, prop: True if populate_list_property_with_window_titles(title_list) else True)

    return props



#def script_update(settings):
#    global source_name, title_source
#
#    obs.timer_remove(set_title_text)
#    source_name = obs.obs_data_get_string(settings, "source_name")
#
#    if source_name:
#        title_source = get_source_from_source_name(source_name)
#        obs.timer_add(set_title_text, 100)


def title_text():
    global set_title_source, tempWindowName

    pass

