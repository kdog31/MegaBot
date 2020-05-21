import discord
from discord.ext import commands
from Cogs import Logger
from aiohttp import web
import os
from dotenv import load_dotenv
import asyncio

client = discord.Client()
load_dotenv()
if os.getenv('PORT') != None:
    port = int(os.getenv('PORT'))
else:
    port = 80
def setup(bot):
    bot.add_cog(API(bot))
    print("MegaBot API module loaded")

async def handle(request):
    server = request.match_info.get('server')
    rchannel = request.match_info.get('channel')
    query = request.query
    #print(query['len'])
    if not query['len']:
        length = 10
    else:
        length = int(query['len'])
    #text = "hello, {}".format(server)
    if server == None:
        a = []
        for guild in gbot.guilds:
            a.append([guild.id, guild.name])
        text = str(a)
        return web.Response(text=text)
    elif server != None and rchannel == None:
        for guild in gbot.guilds:
            if str(guild.id) or str(guild.name) == server:
                a = []
                b = []
                for member in guild.members:
                    a.append([member.id, member.display_name])
                for channel in guild.channels:
                    b.append([channel.id, channel.name])
                return web.Response(text=str(a) + "\n" + str(b))
            else:
                return web.HTTPNotFound()
    elif server != None and rchannel != None:
        for guild in gbot.guilds:
            if str(guild.id) or str(guild.name) == server:
                for channel in guild.channels:
                    if str(channel.id) == rchannel:
                        #return web.Response(text="YEA")
                        a = []
                        try:
                            async for message in channel.history(limit=int(length)):
                                a.append(message.content)
                            return web.Response(text=str(a))
                        except AttributeError:
                            return web.Response(text='No history avalable')
                    else:
                        continue
async def landing(request):
    return web.Response(text="MegaBot API landing page")
                    
    #a = []
    #for guild in gbot.guilds:
    #    a.append(guild.members)
    #text = str(a)
    #return web.Response(text=text)

app = web.Application()
app.add_routes([web.get('/', landing),
                web.get('/api', handle),
                web.get('/api/{server}', handle),
                web.get('/api/{server}/{channel}', handle)])

async def APIstart(bot):
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, None, port)
    try:
        await site.start()
        print("API started on port {}".format(port))
    except PermissionError:
        print("Unable to start API, check ports and try again")

class API(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        global gbot
        gbot = bot