import discord
from discord.ext import commands
from Cogs import AdminCheck
import os, datetime, time, pickle

client = discord.Client()
def setup(bot):
    bot.add_cog(setting(bot))
    print("MegaBot Settings module loaded")

class setting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def initialize(bot):
        servers = bot.guilds
        if not os.path.exists('optouts/settings.pickle'):
            settings = {}
            for i in servers:
                if i.id not in settings:
                    settings[i.id] = {}
            with open('optouts/settings.pickle', 'wb') as handle:
                pickle.dump(settings, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    async def load():
        with open('optouts/settings.pickle', 'rb') as handle:
            settings = pickle.load(handle)
        return settings

    async def save(settings):
        with open('optouts/settings.pickle', 'wb') as handle:
            pickle.dump(settings, handle, protocol=pickle.HIGHEST_PROTOCOL)

    @commands.command()
    async def currentsettings(self, ctx):
        await ctx.send("```{}```".format(settings[ctx.guild.id]))

