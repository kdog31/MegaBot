import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound
from dotenv import load_dotenv
from Cogs import AdminCheck, Exit, Logger, RichPresence, Ping, mstatus, term
import os
import time
import asyncio
import signal
import sys
version = '2.0.1'

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
botid = os.getenv('DISCORD_ID')
bname = os.getenv('BOT_NAME')
if __name__ == "__main__":
    if token == "":
        print("Bot token missing, check docker config.")
        exit()
    elif botid == "":
        print("Bot ID missing, check docker config.")
        exit()
    elif bname == "":
        print("Bot Name missing, check docker config.")
        exit()
    else:
        print("Initializing {}...".format(bname))
        print("Running {} version {}".format(bname, version))
        print("------------------------------")
        print("Cog Versions:")
else:
    print("Bot.py not running as main instance. exiting.")
    exit()

client = discord.Client()
bot = commands.Bot(command_prefix="<@!{}> ".format(botid))


AdminCheck.setup(bot)
Exit.setup(bot)
Logger.setup(bot)
RichPresence.setup(bot)
Ping.setup(bot)
mstatus.setup(bot)
term.setup(bot)

@bot.event
async def on_ready():
    count = 0
    activeservers = bot.guilds
    for s in activeservers:
        count += len(s.members)
    print('\n{} active in {} servers with {} users.'.format(bname, len(bot.guilds), count))
    await bot.change_presence(activity=discord.Game(name="System Ready."))
    await RichPresence.main(bot)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.send("Command not found.")

def sigterm_handler(_signo, _stack_frame):
    # Raises SystemExit(0):
    sys.exit(0)

signal.signal(signal.SIGTERM, sigterm_handler)

try:
    bot.run(token)
finally:
    print("Exiting gracefully")
    exit(0)