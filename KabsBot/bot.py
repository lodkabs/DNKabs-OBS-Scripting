# Run: pipenv run python bot.py
# Ensure you're in the same directory as this script!

import os
from random import randrange
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
    initial_channels=[streamer_name]
)

greeted_users = []
noticed_users = []
lurk_users = []

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
        print(f"Returned message:\n\t{ctx.content}")
        return

    print(f"Received from {ctx.author.name}:\n\t{ctx.content}")

    await bot.handle_commands(ctx)

    content_string = ctx.content.lower()
    content_set = set(content_string.split())

    if (bot_name.lower() in content_string or "kabsbot" in content_string) and ctx.author.name not in noticed_users:
        await ctx.channel.send(f"@{ctx.author.name} noticed me BegWan")
        noticed_users.append(ctx.author.name)
        greeted_users.append(ctx.author.name)
    elif ctx.author.name not in greeted_users:
        await ctx.channel.send(send_greeting(ctx.author.name))
        greeted_users.append(ctx.author.name)


@bot.command(name="lurk")
async def lurk(ctx):
    global lurk_users

    if ctx.author.name in lurk_users:
        randnum = randrange(len(responses.re_lurk_responses))
        lurk_response = responses.re_lurk_responses[randnum].replace("{NAME}", f"@{ctx.author.name}")
    else:
        randnum = randrange(len(responses.lurk_responses))
        lurk_response = responses.lurk_responses[randnum].replace("{NAME}", f"@{ctx.author.name}")
        lurk_users.append(ctx.author.name)

    await ctx.send(lurk_response)

@bot.command(name="unlurk")
async def unlurk(ctx):
    global lurk_users

    if ctx.author.name in lurk_users:
        randnum = randrange(len(responses.unlurk_responses))
        unlurk_response = responses.unlurk_responses[randnum].replace("{NAME}", f"@{ctx.author.name}")
        lurk_users.remove(ctx.author.name)
    else:
        randnum = randrange(len(responses.re_unlurk_responses))
        unlurk_response = responses.re_unlurk_responses[randnum].replace("{NAME}", f"@{ctx.author.name}")

    await ctx.send(unlurk_response)


def send_greeting(name):
    randnum = randrange(len(responses.greet_responses))

    greet_response = responses.greet_responses[randnum].replace("{NAME}", f"@{name}")

    return greet_response


if __name__ == "__main__":
    bot.run()
