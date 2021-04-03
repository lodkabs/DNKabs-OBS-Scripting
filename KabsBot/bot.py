# Run: pipenv run python bot.py
# Ensure you're in the same directory as this script!

import os
from random import randrange
from twitchio.ext import commands

bot_name = os.environ['BOT_NICK']
streamer_name = os.environ['CHANNEL']

bot = commands.Bot(
    # set up the bot
    irc_token=os.environ['TMI_TOKEN'],
    client_id=os.environ['CLIENT_ID'],
    nick=bot_name,
    prefix=os.environ['BOT_PREFIX'],
    initial_channels=[streamer_name]
)

greetings = {"hello", "hi", "hey", "heya", "heplo", "greetings", "morning", "afternoon", "evening", "yo", "koncha", "heyguys"}
greet_responses = [
        "Hi {NAME}, glad you could make it :)",
        "Woah, {NAME}, great to see you here :O",
        "Hey Kabs, {NAME} is here, isn't that awesome? :D",
        "Eeey, it's {NAME}, nice B)",
        "{NAME}! I was hoping you'd make it <3"
        ]
greeted_users = []
noticed_users = []

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

    # make sure the bot ignores itself
    if ctx.author.name.lower() == bot_name.lower():
        return

    print(f"Received from {ctx.author.name}: {ctx.content}")

#    await bot.handle_commands(ctx)

    content_string = ctx.content.lower()
    content_set = set(content_string.split())

    if (bot_name.lower() in content_string or "kabsbot" in content_string) and ctx.author.name not in noticed_users:
        await ctx.channel.send(f"@{ctx.author.name} noticed me BegWan")
        noticed_users.append(ctx.author.name)
        greeted_users.append(ctx.author.name)
    elif greetings.intersection(content_set) and ctx.author.name not in greeted_users:
        await ctx.channel.send(send_greeting(ctx.author.name))
        greeted_users.append(ctx.author.name)


# @bot.command(name="test")
# async def test(ctx):
#     await ctx.send("test passed!")

def send_greeting(name):
    global greet_responses
    randnum = randrange(len(greet_responses))

    greet_response = greet_responses[randnum].replace("{NAME}", f"@{name}")

    return greet_response


if __name__ == "__main__":
    bot.run()
