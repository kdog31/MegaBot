import discord
from discord.ext import commands
from Cogs import AdminCheck
import os, datetime, time
version = '1.0'

client = discord.Client()
def setup(bot):
    bot.add_cog(ping(bot))
    print("Ping Version {}.".format(version))


class ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        created = ctx.message.created_at
        current = datetime.datetime.now()
        compared = current - created 
        if compared.microseconds < 1000:
            t =  str(compared.microseconds) + "μs"
        else:
            t =  str(compared.microseconds / 1000) + "ms"
        await ctx.send("Pong {}".format(t))
    @commands.command()
    async def source(self, ctx):
        await ctx.send("Source Code is avalable at https://github.com/kdog31/MegaBot")