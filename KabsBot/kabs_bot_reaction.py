# Improvement:
# Use watchdog module by following tutorial: http://thepythoncorner.com/dev/how-to-create-a-watchdog-in-python-to-look-for-filesystem-changes/

import obspython as obs
import os
import sys
import inspect
import psycopg2
import datetime

location = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(location)
import db_variables

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

box_name  = "Speech_Box"
box_scene = None

image_path = location + "/images/kabs_bot"

db = None


def populate_variables():
    global image_name, image_source, image_data, image_path
    global speech_name, speech_source, speech_data
    global box_name, box_scene
    global db

    obs.timer_remove(bot_speak)

    if db:
        db.close()

    try:
        db = psycopg2.connect(
                database=db_variables.KABSBOT_DB_NAME,
                user=db_variables.KABSBOT_DB_USER,
                password=db_variables.KABSBOT_DB_PASSWORD,
                host=db_variables.KABSBOT_DB_HOST,
                port=db_variables.KABSBOT_DB_PORT
        )
    except:
        print("Could not connect to database!")
        db = None
    else:
        print(f"Connected to {db_variables.KABSBOT_DB_NAME} database.")
    finally:
        pass

    if image_data:
        obs.obs_data_release(image_data)

    if speech_data:
        obs.obs_data_release(speech_data)

    if box_scene:
        obs.obs_sceneitem_release(box_scene)

    ok1 = ok2 = False
    sources = obs.obs_enum_sources()
    for source in sources:
        if not ok1 and obs.obs_source_get_name(source) == image_name:
            image_source = source
            ok1 = True
        elif not ok2 and obs.obs_source_get_name(source) == speech_name:
            speech_source = source
            ok2 = True

        if ok1 and ok2:
            break

    obs.source_list_release(sources)

    image_data = obs.obs_source_get_settings(image_source)
    bot_image_set("neutral")

    speech_data = obs.obs_source_get_settings(speech_source)

    box_scene = get_sceneitem_from_source_name_in_current_scene(arrow_name)
    obs.obs_sceneitem_set_visible(box_scene, False)

    obs.timer_add(bot_speak, 2000)


def bot_speak():
    global image_name, image_source, image_data
    global speech_name, speech_source, speech_data
    global db

    sql = "SELECT * FROM reactions WHERE shown=false ORDER BY timestamp"
    cur = db.cursor()
    cur.execute(sql)
    try:
        records = cur.fetchall()
    except:
        print("Unable to obtain records")
    else:
        if records:
            for record in records:
                bot_image_set(record[2])

        obs.remove_current_callback()
        print("Should stop here")
    finally:
        pass


def bot_reactions


def bot_image_set(state):
    global image_source, image_data, image_path

    obs.obs_data_set_string(image_data, "file", f"{image_path}_{state}.gif")
    obs.obs_source_update(image_source, image_data)


def script_load(settings):
    populate_variables()

def script_update(settings):
    populate_variables()

def script_unload(settings):
    global image_data, speech_data, db

    if db:
        db.close()

    obs.obs_data_release(image_data)
    obs.obs_data_release(speech_data)
    obs.obs_sceneitem_release(box_scene)

