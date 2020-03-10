import discord
from discord.ext import commands
from time import sleep
import asyncio
from dotenv import load_dotenv
import os
version = '1.0.1'

load_dotenv()
bname = os.getenv('BOT_NAME')

def setup(bot):
    bot.add_cog(servers(bot))
    print("RichPresence Version {}.".format(version))

def getusers(bot):
    onlineusers = 0
    activeservers = bot.guilds
    for s in activeservers:
        onlineusers += len(s.members)
    return onlineusers, len(activeservers)

async def main(bot):
    while True:
        count = 0
        activeservers = bot.guilds
        for s in activeservers:
            count += len(s.members)
        servers.users = count
        servers.servers = len(activeservers)
        await bot.change_presence(activity=discord.Game(name='in {} servers with {} users'.format(len(activeservers), count)))
        await asyncio.sleep(10)

class servers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.users = int
        self.servers = int

    @commands.command()
    async def servers(self, bot):
        await bot.send("{} is managing {} servers with {} users.".format(bname, servers.servers, servers.users))