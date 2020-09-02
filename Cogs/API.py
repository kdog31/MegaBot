import discord
from discord.ext import commands
from Cogs import Logger, RichPresence
from aiohttp import web
import os
from dotenv import load_dotenv
import asyncio
import json

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
    log = await loadlog()
    if not "len" in query:
        length = 10
    else:
        try:
            length = int(query['len'])
        except ValueError:
            length = 1
    if server == None:
        json = {}
        for i in log:
            json[log[i]['name']] = str(i)
        return web.json_response(json)
    elif server != None and rchannel == None:
        for i in log:
            if str(i) == server:
                json = {"channels":{}}
                for channel in log[server]['channels']:
                    json['channels'][channel] = log[server]['channels'][channel]['name']
                return web.json_response(json)
            else:
                continue
        return web.HTTPNotFound()
    elif server != None and rchannel != None:
        for guild in log:
            if str(guild) == server:
                for channel in log[server]['channels']:
                    if channel == rchannel:
                        json = {'messages':{}}
                        try:
                            logged = 0
                            for message in reversed(list(log[server]['channels'][channel]['messages'])):
                                if logged == length:
                                    break
                                a = {'author':{'author_id': log[server]['channels'][channel]['messages'][message]['author']['author_id'], 'author_displayname': log[server]['channels'][channel]['messages'][message]['author']['author_displayname']}, 'content': log[server]['channels'][channel]['messages'][message]['content'], 'attachments': {}}
                                if log[server]['channels'][channel]['messages'][message]['attachments']:
                                    for attachment in log[server]['channels'][channel]['messages'][message]['attachments']:
                                        b = {'filename': log[server]['channels'][channel]['messages'][message]['attachments'][attachment]['filename'], 'url': log[server]['channels'][channel]['messages'][message]['attachments'][attachment]['url']}
                                        a["attachments"][attachment] = b
                                json["messages"][message] = a
                                logged += 1
                            return web.json_response(json)
                        except AttributeError:
                            print(type(channel))
                            return web.Response(text='No history avalable')
                    else:
                        continue
        return web.HTTPNotFound()

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

async def files(request):
    return web.FileResponse('./logs/{}/{}/{}/{}/{}'.format(request.match_info.get('server'), request.match_info.get('channel'), request.match_info.get('folder'), request.match_info.get('date'), request.match_info.get('file')))

app = web.Application()
app.add_routes([web.get('/', landing),
                web.get('/CSS/{stylesheet}', css),
                web.get('/JS/{script}', js),
                web.get('/logs/{server}/{channel}/{folder}/{date}/{file}', files),
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

async def loadlog():
    if os.path.exists('logs/log.json'):
        with open('logs/log.json', 'rb') as json_data:
            log = json.load(json_data)
            return log

class API(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        global gbot
        gbot = bot