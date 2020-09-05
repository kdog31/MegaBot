import discord
from discord.ext import commands
from Cogs import AdminCheck, Settings
from mcstatus import MinecraftServer
import os
from dotenv import load_dotenv
load_dotenv()

client = discord.Client()
def setup(bot):
    bot.add_cog(mcstatus(bot))
    print("MegaBot Minecraft module loaded")


class mcstatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        #self.servers = os.getenv('MC_SERVERS').split(" ")
        self.message = ""

    @commands.command()
    async def mcstatus(self, ctx):
        self.settings = await Settings.setting.load()
        if 'Minecraft' in self.settings[ctx.guild.id]:
            self.servers = self.settings[ctx.guild.id]['Minecraft']
            for i in self.servers:
                server = MinecraftServer.lookup(i)
                try:
                    status = server.status()
                    send = "`the server {2} has {0} players and replied in {1} ms`\n".format(status.players.online, status.latency, i)
                    self.message = self.message + send
                except ConnectionRefusedError:
                    send = "`the server {} refused to connect.`\n".format(i)
                    self.message = self.message + send
                except:
                    send = "`There was an unknown error connecting to {}`\n".format(i)
                    self.message = self.message + send
            await ctx.send(self.message)
        else:
            await ctx.send("No Minecraft servers configured")
        self.message = ""
    
    @commands.command()
    async def mcadd(self, ctx):
        if AdminCheck.admin(ctx):
            i = ctx.message.content.split(' ')
            if len(i) == 3:
                settings = await Settings.setting.load()
                if 'Minecraft' not in settings[ctx.guild.id]:
                    settings[ctx.guild.id]['Minecraft'] = []
                if i[2] not in settings[ctx.guild.id]['Minecraft']:
                    settings[ctx.guild.id]['Minecraft'].append(i[2])
                    await Settings.setting.save(settings)
                    await ctx.send("Minecraft server {} added.".format(i[2]))
                else:
                    await ctx.send('The server {} already exists'.format(i[2]))

    @commands.command()
    async def mcrm(self, ctx):
        if AdminCheck.admin(ctx):
            i = ctx.message.content.split(' ')
            if len(i) == 3:
                settings = await Settings.setting.load()
                if i[2] in settings[ctx.guild.id]['Minecraft']:
                    settings[ctx.guild.id]['Minecraft'].remove(i[2])
                    print(settings)
                    await Settings.setting.save(settings)
                    await ctx.send("Minecraft server {} removed.".format(i[2]))


