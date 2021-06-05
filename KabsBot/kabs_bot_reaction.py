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
records = []
next_line = 0

silent_time = 0
silence_filler = [
        ("greeting", "I like getting\na !hug"),
        ("unlurk", "We can hangout and\n!lurk together"),
        ("greeting", "Let me know when\nyou want to !unlurk"),
        ("github", "I live on\n!github"),
        ("greeting", "I hope everyone\nis doing well~"),
        ("notice", "I am, in fact,\na !plushie"),
        ("greeting", "!hakurei has been\nannounced!"),
        ("greeting", "I like to keep\na !bopcount..."),
        ("greeting", "Please let me know\nwhen a !bop happens~")
        ]
silent_place = 0


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

    box_scene = get_sceneitem_from_source_name_in_current_scene(box_name)
    obs.obs_sceneitem_set_visible(box_scene, False)

    obs.timer_add(bot_speak, 1000)
    obs.timer_add(silence_check, 1000)

def silence_check():
    global db, silent_time, silence_filler, silent_place

    if silent_time <= 300:
        silent_time += 1
    else:
        sql = f"""INSERT INTO reactions (timestamp, reaction, speech, shown)
              VALUES ('{datetime.datetime.now()}', '{silence_filler[silent_place][0]}', '{silence_filler[silent_place][1]}', False);"""

        cur = db.cursor()
        cur.execute(sql)
        db.commit()

        silent_place = (silent_place + 1) % len(silence_filler)
        silent_time = 0


def bot_speak():
    global speech_name, speech_source, speech_data
    global db, records

    sql = "SELECT * FROM reactions WHERE shown=false ORDER BY timestamp"
    cur = db.cursor()
    cur.execute(sql)
    try:
        records = cur.fetchall()
    except:
        print("Unable to obtain records")
    else:
        if records:
            obs.remove_current_callback()
            obs.timer_add(bot_reaction, 5000)
    finally:
        pass


def bot_reaction():
    global box_scene, records, next_line
    global db, silent_time

    silent_time = 0

    if next_line < len(records):
        bot_image_set(records[next_line][2])
        obs.obs_sceneitem_set_visible(box_scene, True)
        set_speech_text(records[next_line][3])

        sql = f"UPDATE reactions set shown = True where id = {records[next_line][0]}"
        cur = db.cursor()
        cur.execute(sql)
        db.commit()

        next_line += 1
    else:
        obs.remove_current_callback()
        set_speech_text("")
        obs.obs_sceneitem_set_visible(box_scene, False)
        bot_image_set("neutral")
        next_line = 0
        obs.timer_add(bot_speak, 1000)


def bot_image_set(state):
    global image_source, image_data, image_path

    obs.obs_data_set_string(image_data, "file", f"{image_path}_{state}.gif")
    obs.obs_source_update(image_source, image_data)


def set_speech_text(text):
    global speech_source, speech_data
    obs.obs_data_set_string(speech_data, "text", f"{text}")
    obs.obs_source_update(speech_source, speech_data)


# Retrieves the scene item of the given source name in the current scene or None if not found
def get_sceneitem_from_source_name_in_current_scene(name):
    result_sceneitem = None
    current_scene_as_source = obs.obs_frontend_get_current_scene()
    if current_scene_as_source:
        current_scene = obs.obs_scene_from_source(current_scene_as_source)
        result_sceneitem = obs.obs_scene_find_source_recursive(current_scene, name)
        obs.obs_source_release(current_scene_as_source)
    return result_sceneitem


def script_load(settings):
    populate_variables()

def script_update(settings):
    populate_variables()

def script_unload(settings):
    global image_data, speech_data, box_scene, db

    if db:
        db.close()

    obs.obs_data_release(image_data)
    obs.obs_data_release(speech_data)
    obs.obs_sceneitem_release(box_scene)

