import discord
from discord.ext import commands
from Cogs import AdminCheck
import os, datetime, time, pickle

client = discord.Client()
def setup(bot):
    bot.add_cog(settings(bot))
    print("MegaBot Settings module loaded")


class settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if os.path.exists('optouts/settings.pickle'):
            with open('optouts/settings.pickle', 'rb') as options:
                self.settings = pickle.load(options)
        else:
            for i in bot.guilds:
                self.settings[i.id] = []

    @commands.command()
    async def currentsettings(self, ctx):
        await ctx.send("```{}```".format(self.settings[ctx.guild.id]))