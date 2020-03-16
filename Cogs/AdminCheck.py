import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
load_dotenv()

superadmin = os.getenv('SUPER_ADMIN').split(" ")

def setup(bot):
    bot.add_cog(whoami(bot))
    print("MegaBot AdminCheck module loaded.")
    print("    SuperAdmins: {}".format(superadmin))

def admin(ctx):
    if ctx.message.author.guild_permissions.administrator or str(ctx.message.author.id) in superadmin:
        return True
    elif not ctx.message.author.guild_permissions.administrator:
        return False

def sudo(ctx):
    if str(ctx.message.author.id) in superadmin:
        return True
    else:
        return False

class whoami(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def whoami(self, ctx):
        if admin(ctx):
            await ctx.send("You are {}, you are and admin.".format(ctx.message.author.name))
        else:
            await ctx.send("You are {}.".format(ctx.message.author.name))