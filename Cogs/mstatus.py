import discord
from discord.ext import commands
from Cogs import AdminCheck
from mcstatus import MinecraftServer
import os

client = discord.Client()
def setup(bot):
    bot.add_cog(mcstatus(bot))
    print("MegaBot Minecraft module loaded")


class mcstatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.servers = ["survival.hal9k.dev", "creative.hal9k.dev"]
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
