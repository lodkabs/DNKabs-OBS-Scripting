# Run: pipenv run python bot.py
# Ensure you're in the same directory as this script!

import os
import sys
from random import randrange
import psycopg2
import signal
import datetime
import asyncio
import requests

from twitchio.ext import commands
from twitchAPI.twitch import Twitch

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

# Docs: https://pytwitchapi.readthedocs.io/en/latest/index.html
twitch = Twitch(os.environ['CLIENT_ID'], os.environ['CLIENT_SECRET'])

# Global control variables
kabs_stream = (streamer_name.lower() == 'dnkabs')
if "-disablegreeting" in sys.argv:
    disable_greeting = True
    print("Disabled greeting")
else:
    disable_greeting = False
    print("Greeting not disabled")

###### Database handling #######
if kabs_stream:
    try:
        db = psycopg2.connect(
                database=os.environ['KABSBOT_DB_NAME'],
                user=os.environ['KABSBOT_DB_USER'],
                password=os.environ['KABSBOT_DB_PASSWORD'],
                host=os.environ['KABSBOT_DB_HOST'],
                port=os.environ['KABSBOT_DB_PORT']
        )
        cur = db.cursor()
    except Exception as e:
        print("Could not connect to database!")
        print(str(e))
        db = None
        cur = None
    else:
        print(f"Connected to {os.environ['KABSBOT_DB_NAME']} database.")
    finally:
        pass
else:
    print("Not a DNKabs stream")
    db = None
    cur = None

def keyboardInterruptHandler(signal, frame):
    print(f"\nKeyboardInterrupt (ID: {signal}) has been caught.\n")
    if db and cur:
        cur.close()
        db.close()
        print(f"Disconnected from {os.environ['KABSBOT_DB_NAME']} database.\n")
    exit(0)

signal.signal(signal.SIGINT, keyboardInterruptHandler)

def send_to_db(reaction, speech):
    global db, cur

    if db:
        sql = f"""INSERT INTO reactions (timestamp, reaction, speech, shown)
                  VALUES ('{datetime.datetime.now()}', '{reaction}', '{speech}', False);"""

        cur.execute(sql)
        db.commit()

###### Event handling ######

greeted_users = []
noticed_users = []
lurk_users = []
bop_count = 0

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

    global bot_name, streamer_name, greetings, greeted_users, disable_greeting
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
                await ctx.channel.send(rand_resp(responses.bye_responses, ctx.author.name))

            else:
                await ctx.channel.send(rand_resp(responses.notice_responses, ctx.author.name))

                greeted_users.append(ctx.author.name)

                send_to_db("notice", f"Happy to see you\n{ctx.author.name}~")

        elif ctx.author.name not in greeted_users and ctx.author.name.lower() != streamer_name.lower():
            if not disable_greeting:
                await ctx.channel.send(rand_resp(responses.greet_responses, ctx.author.name))
            greeted_users.append(ctx.author.name)

            send_to_db("greeting", f"Hello\n{ctx.author.name}!")
    else:
        if ctx.author.name not in greeted_users:
            greeted_users.append(ctx.author.name)

        is_command = False


###### Commands ######

@bot.command(name="discord")
async def discord(ctx):
    global is_command
    is_command = True

    await ctx.send("Grab a drink at the Kabs_Bot Café: https://discord.gg/actPVgqH3R")


@bot.command(name="obsidian")
async def obsidian(ctx):
    global is_command
    global kabs_stream

    if kabs_stream:
        is_command = True

        await ctx.send("We're playing Obsidian Prince today, check it out: https://store.steampowered.com/app/1373260/Obsidian_Prince/")


@bot.command(name="mod")
async def mod(ctx):
    global is_command
    global kabs_stream

    if kabs_stream:
        is_command = True

        #await ctx.send("Check out the Celeste 2020 Spring collab mod here: https://gamebanana.com/mods/150813")
        await ctx.send("Check out the Fire Emblem - Sword of Heaven Earth mod here: https://bit.ly/3yA83vs")


@bot.command(name="temperature")
async def morse(ctx):
    global is_command
    is_command = True

    msg_list = ctx.content.split()
    temp = msg_list[1]
    temp_type = ""

    try:
        x = float(temp)
    except ValueError:
        x = temp[:-1]
        temp_type = temp[-1].upper()

    try:
        y = float(x)
    except ValueError:
        pass
    else:
        if temp_type in ["C", "F", ""]:
            response = ""
            C_rsp = f"{str(y)}C = {round((y * 9 / 5) + 32, 2)}F"
            F_rsp = f"{str(y)}F = {round((y - 32) * 5 / 9, 2)}C"

            if temp_type == 'C':
                response = C_rsp
            elif temp_type == 'F':
                response = F_rsp
            else:
                response = f"{C_rsp}, {F_rsp}"

            await ctx.send(response)


# @bot.command(name="charity")
# async def charity(ctx):
#     global is_command
#     global kabs_stream
#
#     if kabs_stream:
#         is_command = True
#
#         await ctx.send("This month we are supporting Mind! Check them out and !donate if you can: https://www.mind.org.uk/ TakeNRG")
#
#
# @bot.command(name="donate")
# async def donate(ctx):
#     global is_command
#     global kabs_stream
#
#     if kabs_stream:
#         is_command = True
#
#         await ctx.send("Donate to Mind here! https://donate.tiltify.com/@dnkabs/november-2021-fundraising Gimme5")


@bot.command(name="morse")
async def morse(ctx):
    global is_command
    is_command = True

    await ctx.send("WhoIsDoopu made a game, check it out: https://oliverknight.itch.io/morse")


@bot.command(name="lurk")
async def lurk(ctx):
    global lurk_users
    global is_command

    is_command = True

    if ctx.author.name in lurk_users:
        lurk_response = rand_resp(responses.re_lurk_responses, ctx.author.name)
        reaction = "relurk"
        speech = f"I still see you\n{ctx.author.name}~"
    else:
        lurk_response = rand_resp(responses.lurk_responses, ctx.author.name)
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
        unlurk_response = rand_resp(responses.unlurk_responses, ctx.author.name)
        lurk_users.remove(ctx.author.name)
        reaction = "unlurk"
        speech = f"Welcome back\n{ctx.author.name}"
    else:
        unlurk_response = rand_resp(responses.re_unlurk_responses, ctx.author.name)
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
        else:
            username = msg_list[1].strip('@')
            if username.lower() == 'robertskmiles':
                response = "AI Safety is important! (and really interesting) Check it out: https://www.youtube.com/c/RobertMilesAI"
            else:
                channel_list = twitch.search_channels(query=username)
                channel_info = []
                for c in channel_list['data']:
                    if c['broadcaster_login'].lower() == username.lower():
                        channel_info = c
                        break

                if channel_info:
                    response = f"GivePLZ Go give {channel_info['display_name']} a <3 at https://www.twitch.tv/{channel_info['display_name']}"

                    if 'game_name' in channel_info and channel_info['game_name']:
                        response += f" | I saw them playing {channel_info['game_name']} earlier TakeNRG"

            await ctx.send(response)
            send_to_db("shoutout", f"Go follow\n{channel_info['display_name']}!")


@bot.command(name="github")
async def github(ctx):
    global is_command

    is_command = True

    await ctx.send("You can learn more about me here: https://github.com/lodkabs/DNKabs-OBS-Scripting Kappu")


@bot.command(name="hug")
async def hug(ctx):
    global is_command

    is_command = True

    msg_list = ctx.content.split()

    if len(msg_list) > 1:
        username = msg_list[1].strip('@')

    if len(msg_list) < 2 or username.lower() in [bot_name.lower(), 'kabsbot']:
        response = rand_resp(responses.hug_responses, ctx.author.name)
        await ctx.send(response)
        send_to_db("notice", f"Aww, so sweet\n{ctx.author.name}")
    else:
        resp_lines = rand_resp(responses.hug_user_responses, username)
        for resp_line in resp_lines:
            await ctx.send(resp_line)
            await asyncio.sleep(2)
        send_to_db("notice", f"{username} <3\n{ctx.author.name} <3")


@bot.command(name="bop")
async def bop(ctx):
    global is_command, bop_count

    is_command = True
    bop_count += 1

    if bop_count == 1:
        response = "I'm honoured to have witnessed my first bop TPcrunchyroll"
    else:
        response = f"Bop number {bop_count}! " + rand_resp(responses.bop_responses, ctx.author.name)

    await ctx.send(response)
    send_to_db("reunlurk", f"Oh no!\nWe got this~")

@bot.command(name="unbop")
async def unbop(ctx):
    global is_command, bop_count

    if ctx.author.is_mod and bop_count > 0:
        is_command = True
        bop_count -= 1

        await ctx.send(f"I was misinformed! The bop count is now at {bop_count}")

@bot.command(name="bopset")
async def bopset(ctx):
    global is_command, bop_count

    if ctx.author.is_mod:
        is_command = True

        msg_list = ctx.content.split()

        try:
            b = int(msg_list[1])
        except ValueError:
            pass
        else:
            bop_count = b
            await ctx.send(f"I have readjusted! The bop count is now at {bop_count}")

@bot.command(name="bopcount")
async def bopcount(ctx):
    global is_command, bop_count

    is_command = True

    if bop_count == 0:
        await ctx.send("I have not been informed of any bops so far. Nice! HSWP")
    else:
        await ctx.send(f"The bop count is currently at {bop_count}! ...is that a lot? GunRun")


@bot.command(name="plushie")
async def plushie(ctx):
    global is_command

    is_command = True

    await ctx.send("Come get an adorable plushie! (like me): https://www.sleepywaifu.com/ <3")


@bot.command(name="disablegreeting")
async def disablegreeting(ctx):
    global is_command, disable_greeting

    if ctx.author.is_mod:
        is_command = True
        disable_greeting = True

        await ctx.send("I'll keep quiet, thanks for letting me know :)")


@bot.command(name="enablegreeting")
async def enablegreeting(ctx):
    global is_command, disable_greeting

    if ctx.author.is_mod:
        is_command = True
        disable_greeting = False

        await ctx.send("Ready to greet people :D")


@bot.command(name="hakurei")
async def hakurei(ctx):
    global is_command

    is_command = True
    await ctx.send("Interested in competitive Touhou? Check out the Hakurei League! https://www.twitch.tv/hakureileague")


@bot.command(name="truehit")
async def truehit(ctx):
    global is_command

    is_command = True

    msg_list = ctx.content.split()

    try:
        x = int(msg_list[1])
    except ValueError:
        pass
    else:
        if x in range(0,101):
            y = 2*pow(x, 2) + x

            if x > 50:
                y -= 4*pow(x,2) - 398*x + 9900

            await ctx.send(f"A display hit of {x} in 2RN has a True Hit of {y/100}% VoHiYo")


@bot.command(name="thisisfine")
async def thisisfine(ctx):
    global is_command

    is_command = True
    await ctx.send("CurseLit RalpherZ THIS IS FINE CurseLit")


###### Other functions ######

def send_greeting(name):
    greet_response = rand_resp(responses.greet_responses, name)

    return greet_response


def replace_resp_words(text_replace, author):
    global streamer_name, bop_count

    text_replace = text_replace.replace("{NAME}", f"@{author}")
    text_replace = text_replace.replace("{STREAMER}", f"@{streamer_name}")

    link = f"http://numbersapi.com/{bop_count}/"
    if "{BOPMATH}" in text_replace:
        link += "math"
        try:
            f = requests.get(link)
        except:
            bop_math = f"{bop_count} is...kind of a big number, I'm not going to lie :thinking:"
        else:
            bop_math = f.text
            print(bop_math)
        finally:
            text_replace = text_replace.replace("{BOPMATH}", f"{bop_math}")

    if "{BOPTRIVIA}" in text_replace:
        link += "trivia"
        try:
            f = requests.get(link)
        except:
            bop_trivia = f"{bop_count} is...kind of a big number, I'm not going to lie :woozy_face:"
        else:
            bop_trivia = f.text
            print(bop_trivia)
        finally:
            text_replace = text_replace.replace("{BOPTRIVIA}", f"{bop_trivia}")

    return text_replace


def rand_resp(resp_list, author):
    global streamer_name

    randnum = randrange(len(resp_list))

    text = resp_list[randnum]

    if isinstance(text, str):
        replaced_text = replace_resp_words(text, author)
    elif isinstance(text, list):
        replaced_text = list()
        for count, line in enumerate(text):
            replaced_text.append(line.replace("{NAME}", f"@{author}"))
            replaced_text[count] = replaced_text[count].replace("{STREAMER}", f"@{streamer_name}")

    return replaced_text


##### Custom commands #####

def commands_db_get(command="ALL"):
    global db, cur

    if command == "ALL":
        sql = "SELECT command, response FROM commands WHERE active=True"
    else:
        sql = f"SELECT * FROM commands WHERE command='{command}' AND active=True"

    cur.execute(sql)
    return cur.fetchall()

def commands_db_insert(in_type, cust_command, message, created_by):
    global db, cur
    global streamer_name, preset_commands

    command = cust_command.strip('!')

    if in_type == 'add':
        sql = f"""INSERT INTO commands (command, response, channel, created_by, active)
                  VALUES ('{command}', '{message}', '{streamer_name.lower()}', {created_by}, True);"""
        preset_commands.append(command)
    elif in_type == 'edit':
        sql = f"""UPDATE commands SET response = '{message}'
                  WHERE command='{command}' AND channel='{streamer_name.lower()}' AND active=True;"""
    elif in_type == 'delete':
        sql = f"""UPDATE commands SET active = False
                  WHERE command='{command}' AND channel='{streamer_name.lower()}' AND active=True;"""
        preset_commands.remove(command)

    cur.execute(sql)
    db.commit()


# @bot.command(name="custom")
# async def custom(ctx):
#     global is_command, preset_commands
#     is_command = True
#
#     msg_list = ctx.content.split()
#
#     await ctx.send(preset_commands)

# Ensure this part stays at the bottom of the script!
preset_commands = []
for key, value in list(locals().items()):
    if isinstance(value, commands.core.Command):
        preset_commands.append(key)



if __name__ == "__main__":
    bot.run()
