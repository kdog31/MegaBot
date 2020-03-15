import discord
from discord.ext import commands
from Cogs import AdminCheck
import os, datetime, time
from Cogs import AdminCheck
import asyncio

client = discord.Client()
def setup(bot):
    bot.add_cog(megaterm(bot))
    print("MegaBot Terminal module loaded")

async def run(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()
    return stdout

class megaterm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.author = None
        self.active = False

    @commands.command()
    async def termstart(self, ctx):
        if ctx.message.author.id == 253457602908913674:
            if self.active == False:
                self.author = ctx.author
                self.active = True
                await ctx.send("MegaTerm Active, controlling user: {}".format(self.author))
            else:
                await ctx.send("Terminal session already running.")

    @commands.command()
    async def termstop(self, ctx):
        if ctx.message.author.id == 253457602908913674:
            if self.active == True:
                self.author = None
                self.active = False
                await ctx.send("MegaTerm Deactivated")
            else:
                await ctx.send("Terminal session not running")
    
    @commands.Cog.listener()
    async def on_message(self, ctx):
        if self.active == True:
            if ctx.author == self.author:
                await ctx.channel.send("```" + str(await run(ctx.content), 'ascii') + "```", delete_after=20)
