import discord
from discord.ext import commands
from Cogs import AdminCheck
import os

client = discord.Client()
def setup(bot):
    bot.add_cog(quit(bot))
    print("MegaBot Exit module loaded.")


class quit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def restart(self, ctx):
        if AdminCheck.admin(ctx):
            await self.bot.change_presence(activity=discord.Game(name="System Offline."))
            await ctx.send("You are an administrator, restarting bot.")
            print('bot exit requested')
            await client.logout()
            await exit()
        else:
            await ctx.send("You are not an administrator. Contact your local administrator if there are issues with my functionality.")