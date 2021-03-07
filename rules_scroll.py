import obspython as obs
import time

def script_description():
    return """Scroll with pauses
           OBS already supports scrolling, but doesn't allow for regular pauses during
           the scroll. This is particularly useful for giving the viewer enough time
           to read each line of a given text."""


# User Data Setting:

def populate_list_property_with_source_names(list_property):
    sources = obs.obs_enum_sources()
    obs.obs_property_list_clear(list_property)
    obs.obs_property_list_add_string(list_property, "", "")
    for source in sources:
        name = obs.obs_source_get_name(source)
        obs.obs_property_list_add_string(list_property, name, name)
    obs.source_list_release(sources)

def populate_list_property_with_filter_names(source, list_property):
    filters = obs.obs_source_enum_filters(source)
    obs.obs_property_list_clear(list_property)
    obs.obs_property_list_add_string(list_property, "", "")
    for filterItem in filters:
        name = obs.obs_source_get_filter_by_name(source, filterItem)
        obs.obs_property_list_add_string(list_property, name, name)

def script_defaults(settings):
    obs.obs_data_set_default_int(settings, "pause_after", 500)
    obs.obs_data_set_default_int(settings, "continue_after", 500)


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

