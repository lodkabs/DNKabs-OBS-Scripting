# Improvement:
# Use watchdog module by following tutorial: http://thepythoncorner.com/dev/how-to-create-a-watchdog-in-python-to-look-for-filesystem-changes/

import obspython as obs
import os
import inspect

def script_description():
    return """Kabs_Bot reactions
              Change Kabs_Bot image in response to
              chat, commands, etc."""

# Global variables
source_name   = "Kabs_Bot"
image_source  = None
image_data    = None
location      = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
image_path    = location + "/images/kabs_bot"
response_file = location + "/kabs_bot_response.txt"

def populate_variables():
    global source_name, image_source, image_data

    sources = obs.obs_enum_sources()
    for source in sources:
        if obs.obs_source_get_name(source) == source_name:
            image_source = source
            break
    obs.source_list_release(sources)

    image_data = obs.obs_source_get_settings(image_source)

    obs.obs_data_set_string(image_data, "file", f"{image_path}_lurk.gif")
    obs.obs_source_update(image_source, image_data)

    obs.obs_data_release(image_data)


def script_load(settings):
    populate_variables()

def script_update(settings):
    populate_variables()

