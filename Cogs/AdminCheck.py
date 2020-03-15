import discord
from discord.ext import commands

def setup(bot):
    bot.add_cog(whoami(bot))
    print("MegaBot AdminCheck module loaded.")

def admin(ctx):
    if ctx.message.author.guild_permissions.administrator or ctx.message.author.id == 253457602908913674:
        return True
    elif not ctx.message.author.guild_permissions.administrator:
        return False

class whoami(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def whoami(self, ctx):
        if ctx.message.author.guild_permissions.administrator:
            await ctx.send("You are {}, you are and admin.".format(ctx.message.author.name))
        else:
            await ctx.send("You are {}.".format(ctx.message.author.name))