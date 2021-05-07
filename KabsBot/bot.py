# Run: pipenv run python bot.py
# Ensure you're in the same directory as this script!

import os
from random import randrange
import psycopg2
import signal
import datetime

from twitchio.ext import commands

import responses

bot_name = os.environ['BOT_NICK']
streamer_name = os.environ['CHANNEL']

bot = commands.Bot(
    # set up the bot
    irc_token=os.environ['TMI_TOKEN'],
    client_id=os.environ['CLIENT_ID'],
    nick=bot_name,
    prefix=os.environ['BOT_PREFIX'],
    initial_channels=[streamer_name],
    api_token=os.environ['ACCESS_TOKEN'],
    new_client_id=os.environ['NEW_CLIENT_ID'],
    client_secret=os.environ['CLIENT_SECRET']
)


###### Database handling #######

try:
    db = psycopg2.connect(
            database=os.environ['KABSBOT_DB_NAME'],
            user=os.environ['KABSBOT_DB_USER'],
            password=os.environ['KABSBOT_DB_PASSWORD'],
            host=os.environ['KABSBOT_DB_HOST'],
            port=os.environ['KABSBOT_DB_PORT']
    )
except:
    print("Could not connect to database!")
    db = None
else:
    print(f"Connected to {os.environ['KABSBOT_DB_NAME']} database.")
finally:
    pass

def keyboardInterruptHandler(signal, frame):
    print(f"\nKeyboardInterrupt (ID: {signal}) has been caught.\n")
    if db:
        db.close()
        print(f"Disconnected from {os.environ['KABSBOT_DB_NAME']} database.\n")
    exit(0)

signal.signal(signal.SIGINT, keyboardInterruptHandler)

def send_to_db(reaction, speech):
    global streamer_name

    if streamer_name.lower() == 'dnkabs':
        global db

        sql = f"""INSERT INTO reactions (timestamp, reaction, speech, shown)
                  VALUES ('{datetime.datetime.now()}', '{reaction}', '{speech}', False);"""

        cur = db.cursor()
        cur.execute(sql)
        db.commit()



###### Event handling ######

greeted_users = []
noticed_users = []
lurk_users = []

is_command = False

@bot.event
async def event_ready():
    'Called once when the bot goes online.'
    print(f"{os.environ['BOT_NICK']} is online!")
    ws = bot._ws  # this is only needed to send messages within event_ready
    await ws.send_privmsg(os.environ['CHANNEL'], f"/me is happy to be here VoHiYo")

@bot.event
async def event_message(ctx):
    'Runs every time a message is sent in chat.'

    global bot_name, streamer_name, greetings, greeted_users
    global is_command

    # make sure the bot ignores itself
    if ctx.author.name.lower() == bot_name.lower():
        print(f"{datetime.datetime.now()} Returned message:\n\t{ctx.content}")
        return

    print(f"{datetime.datetime.now()} Received from {ctx.author.name}:\n\t{ctx.content}")

    await bot.handle_commands(ctx)

    if not is_command:
        content_string = ctx.content.lower()
        content_set = set(content_string.split())
        bot_names = {"kabsbot", "kabs bot"}
        bye_words = {"bye", "goodbye", "farewell"}

        if bot_name.lower() in content_string or content_set.intersection(bot_names):
            if content_set.intersection(bye_words):
                randnum = randrange(len(responses.bye_responses))
                response = response_replaces(responses.bye_responses[randnum], ctx.author.name)
                print(response)

                await ctx.channel.send(response)

            elif ctx.author.name not in noticed_users:
                await ctx.channel.send(f"@{ctx.author.name} noticed me BegWan")

                noticed_users.append(ctx.author.name)
                greeted_users.append(ctx.author.name)

                send_to_db("notice", f"Happy to see you\n{ctx.author.name}~")

        elif ctx.author.name not in greeted_users and ctx.author.name.lower() != streamer_name.lower():
            await ctx.channel.send(send_greeting(ctx.author.name))
            greeted_users.append(ctx.author.name)

            send_to_db("greeting", f"Hello\n{ctx.author.name}!")
    else:
        if ctx.author.name not in greeted_users:
            greeted_users.append(ctx.author.name)

        is_command = False


###### Commands ######

@bot.command(name="lurk")
async def lurk(ctx):
    global lurk_users
    global is_command

    is_command = True

    if ctx.author.name in lurk_users:
        randnum = randrange(len(responses.re_lurk_responses))
        lurk_response = response_replaces(responses.re_lurk_responses[randnum], ctx.author.name)
        reaction = "relurk"
        speech = f"I still see you\n{ctx.author.name}~"
    else:
        randnum = randrange(len(responses.lurk_responses))
        lurk_response = response_replaces(responses.lurk_responses[randnum], ctx.author.name)
        lurk_users.append(ctx.author.name)
        reaction = "lurk"
        speech = f"Thanks for lurking\n{ctx.author.name}!"

    await ctx.send(lurk_response)
    send_to_db(reaction, speech)

@bot.command(name="unlurk")
async def unlurk(ctx):
    global lurk_users
    global is_command

    is_command = True

    if ctx.author.name in lurk_users:
        randnum = randrange(len(responses.unlurk_responses))
        unlurk_response = response_replaces(responses.unlurk_responses[randnum], ctx.author.name)
        lurk_users.remove(ctx.author.name)
        reaction = "unlurk"
        speech = f"Welcome back\n{ctx.author.name}"
    else:
        randnum = randrange(len(responses.re_unlurk_responses))
        unlurk_response = response_replaces(responses.re_unlurk_responses[randnum], ctx.author.name)
        reaction = "reunlurk"
        speech = f"You scared me\n{ctx.author.name}!"

    await ctx.send(unlurk_response)
    send_to_db(reaction, speech)


@bot.command(name="so")
async def so(ctx):
    global is_command

    is_command = True

    if ctx.author.is_mod:
        msg_list = ctx.content.split()

        if len(msg_list) < 2:
            await ctx.send(f"You\'ve gotta give me someone to shoutout!")
        so_user = msg_list[1]
        if so_user[0] != "@":
            await ctx.send("Sorry, I get confused if you don\'t tag the shoutout SirSad")
        else:
            await ctx.send(f"GivePLZ Go give {so_user} a <3 at https://www.twitch.tv/{so_user.strip('@')}/ TakeNRG")
            send_to_db("shoutout", f"Go follow\n{so_user.strip('@')}!")



@bot.command(name="github")
async def github(ctx):
    global is_command

    is_command = True

    await ctx.send("You can learn more about me here: https://github.com/lodkabs/DNKabs-OBS-Scripting Kappu")


@bot.command(name="hug")
async def hug(ctx):
    global is_command

    is_command = True

    randnum = randrange(len(responses.hug_responses))
    response = response_replaces(responses.hug_responses[randnum], ctx.author.name)

    await ctx.send(response)
    send_to_db("notice", f"Aww, so sweet\n{ctx.author.name}")



###### Other functions ######

def send_greeting(name):
    randnum = randrange(len(responses.greet_responses))

    greet_response = response_replaces(responses.greet_responses[randnum], name)

    return greet_response

def response_replaces(text, author):
    global streamer_name

    replaced_text = text.replace("{NAME}", f"@{author}")
    replaced_text = replaced_text.replace("{STREAMER}", f"@{streamer_name}")

    return replaced_text



if __name__ == "__main__":
    bot.run()
