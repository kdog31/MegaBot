import discord
from discord.ext import commands
from Cogs import AdminCheck
from mcstatus import MinecraftServer
import os
version = '1.0'

client = discord.Client()
def setup(bot):
    bot.add_cog(mcstatus(bot))
    print("mcstatus Version {}.".format(version))


class mcstatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.servers = ["mc1.kainentechtips.com:25565"]
        self.message = ""

    @commands.command()
    async def mcstatus(self, ctx):
        for i in self.servers:
            server = MinecraftServer.lookup(i)
            status = server.status()
            send = "`the server {2} has {0} players and replied in {1} ms`\n".format(status.players.online, status.latency, i)
            self.message = self.message + send
        await ctx.send(self.message)
        self.message = ""
