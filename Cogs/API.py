import discord
from discord.ext import commands
from Cogs import Logger, RichPresence
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
    if not "len" in query:
        length = 10
    else:
        length = int(query['len'])
    if server == None:
        json = {}
        for guild in gbot.guilds:
            json[guild.name] = str(guild.id)
        return web.json_response(json)
    elif server != None and rchannel == None:
        for guild in gbot.guilds:
            if str(guild.id) == server:
                #a = []
                #b = []
                #for member in guild.members:
                #    a.append([member.id, member.display_name])
                #for channel in guild.channels:
                #    b.append([channel.id, channel.name])
                #return web.Response(text=str(a) + "\n" + str(b))
                json = {"members":{}, "channels":{}}
                for member in guild.members:
                    json['members'][str(member.id)] = member.display_name
                for channel in guild.channels:
                    if type(channel) != discord.channel.CategoryChannel and type(channel) != discord.channel.VoiceChannel:
                        json['channels'][str(channel.id)] = channel.name
                return web.json_response(json)
            else:
                continue
        return web.HTTPNotFound()
    elif server != None and rchannel != None:
        for guild in gbot.guilds:
            if str(guild.id) == server:
                for channel in guild.channels:
                    if str(channel.id) == rchannel:
                        json = {'messages':{}}
                        try:
                            async for message in channel.history(limit=int(length)):
                                a = {'author':{'author_id': message.author.id, 'author_displayname': message.author.display_name}, 'content': message.content, 'attachments': {}}
                                if message.attachments:
                                    for attachment in message.attachments:
                                        b = {'filename': attachment.filename, 'url': attachment.url}
                                        a["attachments"][attachment.id] = b
                                json["messages"][message.id] = a
                            return web.json_response(json)
                        except AttributeError:
                            print(type(channel))
                            return web.Response(text='No history avalable')
                    else:
                        continue
async def landing(request):
    return web.FileResponse('./web/index.html')

async def stats(request):
    users, servers = RichPresence.getusers(gbot)
    json = {"users": users, "servers": servers}
    return web.json_response(json)

async def css(request):
    stylesheet = request.match_info.get('stylesheet')
    if os.path.exists('./web/CSS/{}'.format(stylesheet)):
        return web.FileResponse('./web/CSS/{}'.format(stylesheet))
    else:
        return web.HTTPNotFound()

async def js(request):
    javascript = request.match_info.get('script')
    if os.path.exists('./web/JS/{}'.format(javascript)):
        return web.FileResponse('./web/JS/{}'.format(javascript))
    else:
        return web.HTTPNotFound()

async def logs(request):
    return web.FileResponse('./web/log/index.html')

app = web.Application()
app.add_routes([web.get('/', landing),
                web.get('/CSS/{stylesheet}', css),
                web.get('/JS/{script}', js),
                web.get('/log', logs),
                web.get('/api/stats', stats),
                web.get('/api/servers', handle),
                web.get('/api/servers/{server}', handle),
                web.get('/api/servers/{server}/{channel}', handle)])


async def APIstart(bot):
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, None, port)
    try:
        await site.start()
        print("API started on port {}\n".format(port))
    except PermissionError:
        print("Unable to start API, check ports and try again")
    except OSError:
        pass

class API(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        global gbot
        gbot = bot