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
    obs.obs_data_set_default_string(settings, "source_name", "")
    obs.obs_data_set_default_int(settings, "h_speed", 0)
    obs.obs_data_set_default_int(settings, "v_speed", 0)
    obs.obs_data_set_default_bool(settings, "limit_width", False)
    obs.obs_data_set_default_int(settings, "width", 500)
    obs.obs_data_set_default_bool(settings, "limit_height", False)
    obs.obs_data_set_default_int(settings, "height", 200)
    obs.obs_data_set_default_bool(settings, "loop", False)

    obs.obs_data_set_default_int(settings, "pause_after", 500)
    obs.obs_data_set_default_int(settings, "continue_after", 500)


# Called to display the properties GUI
def script_properties():
    props = obs.obs_properties_create()

    list_property = obs.obs_properties_add_list(props, "source_name", "Source name", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
    populate_list_property_with_source_names(list_property)
    # Button to refresh the drop-down list
    obs.obs_properties_add_button(props, "button", "Refresh list of sources", lambda props, prop: True if populate_list_property_with_source_names(list_property) else True)

    obs.obs_properties_add_int_slider(props, "h_speed", "Horizontal Speed", -500, 500, 1)
    obs.obs_properties_add_int_slider(props, "v_speed", "Vertical Speed", -500, 500, 1)

    obs.obs_properties_add_bool(props, "limit_width", "Limit Width")
    obs.obs_properties_add_int(props, "width", "Width", 0, 8192, 1)

    obs.obs_properties_add_bool(props, "limit_height", "Limit Height")
    obs.obs_properties_add_int(props, "height", "Height", 0, 8192, 1)

    obs.obs_properties_add_bool(props, "loop", "Loop")

    obs.obs_properties_add_int(props, "pause_after", "Pause after", 0, 8192, 1)
    obs.obs_properties_add_int(props, "continue_after", "Continue after", 0, 8192, 1)

    return props


# Called after change of settings including once after script load
def script_update(settings):
    global source_name, h_speed, v_speed, limit_width, width, limit_height, height, loop, pause_after, continue_after
#    restore_sceneitem_after_shake()
    source_name = obs.obs_data_get_string(settings, "source_name")
    h_speed = obs.obs_data_get_int(settings, "h_speed")
    v_speed = obs.obs_data_get_int(settings, "v_speed")
    limit_width = obs.obs_data_get_bool(settings, "limit_width")
    width = obs.obs_data_get_int(settings, "width")
    limit_height = obs.obs_data_get_bool(settings, "limit_height")
    height = obs.obs_data_get_int(settings, "height")
    loop = obs.obs_data_get_bool(settings, "loop")
    pause_after = obs.obs_data_get_int(settings, "pause_after")
    continue_after = obs.obs_data_get_int(settings, "continue_after")


## Retrieves the scene item of the given source name in the current scene or None if not found
#def get_sceneitem_from_source_name_in_current_scene(name):
#    result_sceneitem = None
#    current_scene_as_source = obs.obs_frontend_get_current_scene()
#    if current_scene_as_source:
#        current_scene = obs.obs_scene_from_source(current_scene_as_source)
#        result_sceneitem = obs.obs_scene_find_source_recursive(current_scene, name)
#        obs.obs_source_release(current_scene_as_source)
#    return result_sceneitem
#
#
## Animates scene item
#def scroll_pause_scene(s_horizontal, s_vertical):
#    sceneitem = get_sceneitem_from_source_name_in_current_scene(source_name)
#    if sceneitem:
#        angle = shaken_sceneitem_angle + amplitude*math.sin(time.time()*frequency*2*math.pi)
#        obs.obs_sceneitem_set_rot(sceneitem, angle)
#
