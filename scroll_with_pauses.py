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

def script_defaults(settings):
    obs.obs_data_set_default_string(settings, "source_name", "")

# Called to display the properties GUI
def script_properties():
    props = obs.obs_properties_create()

    list_property = obs.obs_properties_add_list(props, "source_name", "Source name", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
    populate_list_property_with_source_names(list_property)
    # Button to refresh the drop-down list
    obs.obs_properties_add_button(props, "button", "Refresh list of sources", lambda props, prop: True if populate_list_property_with_source_names(list_property) else True)

    return props

