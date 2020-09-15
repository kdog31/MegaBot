import discord
from discord.ext import commands, tasks
from Cogs import Logger, RichPresence, AdminCheck, Settings
from aiohttp import web
import os
from dotenv import load_dotenv
import asyncio
import json
import aiofiles
import random
import string
import datetime

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
    log = await API.loadlog()
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
                                a = {'author':{'author_id': log[server]['channels'][channel]['messages'][message]['author']['author_id'], 'author_displayname': log[server]['channels'][channel]['messages'][message]['author']['author_displayname']}, 'content': log[server]['channels'][channel]['messages'][message]['content'], 'attachments': {}, 'links': {}}
                                if log[server]['channels'][channel]['messages'][message]['attachments']:
                                    for attachment in log[server]['channels'][channel]['messages'][message]['attachments']:
                                        b = {'filename': log[server]['channels'][channel]['messages'][message]['attachments'][attachment]['filename'], 'url': log[server]['channels'][channel]['messages'][message]['attachments'][attachment]['url']}
                                        a["attachments"][attachment] = b
                                if log[server]['channels'][channel]['messages'][message]['links']:
                                    for i in log[server]['channels'][channel]['messages'][message]['links']:
                                        for n in i:
                                            a["links"][i] = log[server]['channels'][channel]['messages'][message]['links'][n]
                                json["messages"][message] = a
                                logged += 1
                            return web.json_response(json)
                        except AttributeError:
                            print(type(channel))
                            return web.Response(text='No history avalable')
                    else:
                        continue
        return web.HTTPNotFound()

async def consoleAPI(request):
    query = request.query
    if request.method == "GET":
        if "token" in query.keys():
            for i in API.validCodes:
                if query['token'] in i:
                    settings = await Settings.setting.load()
                    a = int(i[2])
                    return web.json_response(settings[a])
            else:
                return web.HTTPNotFound()
        else:
            return web.HTTPUnauthorized()
    elif request.method == "POST":
        if "token" in query.keys():
            for i in API.validCodes:
                if query['token'] in i:
                    try:
                        newSettings = await request.json()
                        settings = await Settings.setting.load()
                        settings[int(i[2])] = newSettings
                        await Settings.setting.save(settings)
                        return web.HTTPOk()
                    except:
                        return web.HTTPInternalServerError()
    else:
        return web.HTTPMethodNotAllowed


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

async def admin(request):
    return web.FileResponse('./web/admin/index.html')

async def console(request):
    return web.FileResponse('./web/admin/console.html')

async def token(request):
    data = await request.json()
    token = data['token']
    if API.validCodes:
        for i in API.validCodes:
            if i[1] == token:
                return web.HTTPOk()
            else:
                return web.HTTPUnauthorized()
    else:
        return web.HTTPUnauthorized()
    
    

async def files(request):
    if os.path.exists('./logs/{}/{}/{}/{}/{}'.format(request.match_info.get('server'), request.match_info.get('channel'), request.match_info.get('folder'), request.match_info.get('date'), request.match_info.get('file'))):
        return web.FileResponse('./logs/{}/{}/{}/{}/{}'.format(request.match_info.get('server'), request.match_info.get('channel'), request.match_info.get('folder'), request.match_info.get('date'), request.match_info.get('file')))
    else:
        return web.HTTPNotFound()

app = web.Application()
app.add_routes([web.get('/', landing),
                web.get('/CSS/{stylesheet}', css),
                web.get('/JS/{script}', js),
                web.get('/logs/{server}/{channel}/{folder}/{date}/{file}', files),
                web.get('/log', logs),
                web.get('/admin', admin),
                web.post('/admin/token', token),
                web.get('/admin/console', console),
                web.get('/admin/console/api', consoleAPI),
                web.post('/admin/console/api', consoleAPI),
                web.get('/api/stats', stats),
                web.get('/api/servers', handle),
                web.get('/api/servers/{server}', handle),
                web.get('/api/servers/{server}/{channel}', handle)])

async def get_random_alphanumeric_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    return result_str

async def APIstart(self):
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
        API.size = 0
        API.log = {}
        API.validCodes = []
    
    async def loadlog():
        if os.path.exists('logs/log.json'):
            newsize = os.path.getsize('logs/log.json')
            #try:
            if newsize > API.size:
                API.size = newsize
                async with aiofiles.open('logs/log.json', 'rb') as json_data:
                    API.log = json.loads(await json_data.read())
                    return API.log
            else:
                return API.log
            #except UnboundLocalError:
            #    print('this', newsize)
            #    size = os.path.getsize('logs/log.json')
            #    async with aiofiles.open('logs/log.json', 'rb') as json_data:
            #        log = json.loads(await json_data.read())
            #        return log
    
    @commands.Cog.listener()
    async def on_ready(self):
        await APIstart(self)
        self.code_loop.start()

    @commands.command()
    async def getcode(self, ctx):
        if AdminCheck.admin(ctx):
            code = await get_random_alphanumeric_string(10)
            now = datetime.datetime.now()
            expire = now + datetime.timedelta(minutes=30)
            API.validCodes.append([[expire.year, expire.month, expire.day, expire.hour, expire.minute, expire.second], code, str(ctx.guild.id)])
            await ctx.author.send('```Your passcode is: {}\nIt will expire in 30 minutes.```'.format(code))
        else:
            await ctx.send('Only Administrators may request codes.')
        
    @tasks.loop(seconds=1)
    async def code_loop(self):
        now = datetime.datetime.now()
        for i in API.validCodes:
            a_load = i[0]
            b = datetime.datetime(a_load[0], a_load[1], a_load[2], a_load[3], a_load[4], a_load[5])
            if now > b:
                API.validCodes.remove(i)