# Run: pipenv run python charity_bot.py
# Ensure you're in the same directory as this script!

import os
import datetime
import asyncio

from twitchio.ext import commands
from twitchAPI.twitch import Twitch

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


###### Event handling ######

@bot.event
async def event_ready():
    'Called once when the bot goes online.'
    print(f"{os.environ['BOT_NICK']} is online!")
    ws = bot._ws  # this is only needed to send messages within event_ready
    await ws.send_privmsg(os.environ['CHANNEL'], f"/me is ready for charity hype dnkabsSpecialEffect")

@bot.event
async def event_message(ctx):
    'Runs every time a message is sent in chat.'

    # make sure the bot ignores itself
    if ctx.author.name.lower() == bot_name.lower():
        print(f"{datetime.datetime.now()} Returned message:\n\t{ctx.content}")
        return

    print(f"{datetime.datetime.now()} Received from {ctx.author.name}:\n\t{ctx.content}")

    await bot.handle_commands(ctx)


###### Commands ######

@bot.command(name="donate")
async def donate(ctx):

    await ctx.send("https://tiltify.com/+dk-crew/dnkabs-specialeffect-2025")

# Ensure this part stays at the bottom of the script!
preset_commands = []
for key, value in list(locals().items()):
    if isinstance(value, commands.core.Command):
        preset_commands.append(key)

if __name__ == "__main__":
    bot.run()
