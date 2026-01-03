#https://blog.miguelgrinberg.com/post/dynamically-update-your-flask-web-pages-using-turbo-flask
#https://www.w3docs.com/snippets/css/how-to-position-one-image-on-top-of-another-in-html-css.html

import os
import psycopg2
from datetime import datetime

from flask import Flask, render_template, url_for, request, redirect
from turbo_flask import Turbo
import threading
import time

app = Flask(__name__)
turbo = Turbo(app)

reaction = 'neutral'
speaking = False
coffee = False
nowtime = "0"
silent_time = 0
silence_filler = [
        #('greeting', 'Upcoming !charity', 'event!'),
        #('notice', 'If you are able to,', 'please !donate'),
        #('star', 'New !event,', 'this is exciting!'),
        ('greeting', 'I like getting', 'a !hug'),
        ('greeting', 'I like giving a !hug', 'to others as well'),
        ('unlurk', 'We can hangout and', '!lurk together'),
        ('greeting', 'Let me know when', 'you want to !unlurk'),
        ('github', 'I live on', '!github'),
        ('greeting', 'I hope everyone', 'is doing well~'),
        ('greeting', 'We finally have a', '!discord server'),
        ('notice', 'I am, in fact,', 'a !plushie'),
        ('greeting', 'I like to keep', 'a !bonkcount...'),
        ('greeting', 'Please let me know', 'when a !bonk happens~'),
        ('github', 'Wait we have a', '!podcast now?'),
        #('unlurk', 'Check out the !mod', 'being played'),
        ('unlurk', 'We have !controller', 'display now!'),
        ('github', 'What is that', '!truehit again?'),
        ('notice', 'I can convert', 'the !temperature'),
        ]
silent_place = -1

responses_from_db = []

##### Database handling #####

try:
    db = psycopg2.connect(
            database=os.environ['KABSBOT_DB_NAME'],
            user=os.environ['KABSBOT_DB_USER'],
            password=os.environ['KABSBOT_DB_PASSWORD'],
            host=os.environ['KABSBOT_DB_HOST'],
            port=os.environ['KABSBOT_DB_PORT']
    )
except Exception as e:
    print("Could not connect to database!")
    print(str(e))
    db = None
else:
    print(f"Connected to {os.environ['KABSBOT_DB_NAME']} database.")
finally:
    pass

def bot_speak():
    global db
    records = []

    if db:
        sql = "SELECT * FROM reactions WHERE shown=false ORDER BY timestamp"
        cur = db.cursor()
        cur.execute(sql)
        try:
            records = cur.fetchall()
        except:
            print("Unable to obtain records")
        finally:
            pass

    return records

def record_shown(record):
    global db

    sql = f"UPDATE reactions set shown = True where id = {record[0]}"
    cur = db.cursor()
    cur.execute(sql)
    db.commit()

#####

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fe_rules')
def rules():
    return render_template('FE_rules.html')

@app.route('/main_game')
def main_game():
    return render_template('main_game.html')

@app.route('/side_game')
def side_game():
    return render_template('side_game.html')

@app.context_processor
def inject_load():
    global reaction, speaking, coffee, nowtime
    global silent_time, silence_filler, silent_place
    global responses_from_db

    text_1 = text_2 = ""
    if coffee and silent_time > 10:
        coffee = False

    if len(responses_from_db) > 0:
        speaking = True
        reaction = responses_from_db[0][2]
        if reaction == "coffee":
            coffee = True
            reaction = "greeting"
            nowtime = datetime.now().strftime('%H%M%S')
        [text_1, text_2] = responses_from_db[0][3].split('\n')

        record_shown(responses_from_db[0])
        del responses_from_db[0]
        silent_time = 0
    else:
        responses_from_db = bot_speak()
        if speaking or silent_time < 300:
            speaking = False
            reaction = 'neutral'
            silent_time += 5
        else:
            speaking = True
            silent_place = (silent_place + 1) % len(silence_filler)
            reaction = silence_filler[silent_place][0]
            text_1 = silence_filler[silent_place][1]
            text_2 = silence_filler[silent_place][2]
            silent_time = 0

    return {
    'reaction' : reaction,
    'speaking' : speaking,
    'text_1' : text_1,
    'text_2' : text_2,
    'coffee' : coffee,
    'nowtime' : nowtime
    }

@app.before_first_request
def before_first_request():
    threading.Thread(target=update_reaction).start()

def update_reaction():
    with app.app_context():
        while True:
            turbo.push(turbo.replace(render_template('kabs_bot_reaction.html'), 'pic'))
            time.sleep(5)

if __name__ == '__main__':
    app.run(debug=True)
