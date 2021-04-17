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
image_name   = "Kabs_Bot"
image_source = None
image_data   = None

speech_name   = "Bot_Speak"
speech_source = None
speech_data   = None

location      = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
image_path    = location + "/images/kabs_bot"
response_file = location + "/speech_response.txt"


def populate_variables():
    global image_name, image_source, image_data
    global speech_name, speech_source, speech_data

    obs.timer_remove(bot_speak)

    if image_data:
        obs.obs_data_release(image_data)

    if speech_data:
        obs.obs_data_release(specch_data)

    ok1 = ok2 = False
    sources = obs.obs_enum_sources()
    for source in sources:
        if obs.obs_source_get_name(source) == image_name:
            image_source = source
            ok1 = True
        elif obs.obs_source_get_name(source) == speech_name:
            speech_source = source
            ok2 = True

        if ok1 and ok2:
            break

    obs.source_list_release(sources)

    image_data = obs.obs_source_get_settings(image_source)
    obs.obs_data_set_string(image_data, "file", f"{image_path}_neutral.gif")
    obs.obs_source_update(image_source, image_data)

    speech_data = obs.obs_source_get_setting(speech_source)

    obs.timer_add(bot_speak, 2000)


def bot_speak():
    pass



def script_load(settings):
    populate_variables()

def script_update(settings):
    populate_variables()

def script_unload(settings):
    global image_data, speech_data

    obs.obs_data_release(image_data)
    obs.obs_data_release(speech_data)

