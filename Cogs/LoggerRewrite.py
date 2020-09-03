import discord
from discord.ext import commands
import os
import subprocess
import asyncio
import re
from dotenv import load_dotenv
from datetime import datetime
import pickle
import json
from Cogs import AdminCheck
import aiofiles

load_dotenv()
logurl = os.getenv('LOG_URL')
panic_word = os.getenv('PANIC_WORD')
bot_name = os.getenv('BOT_NAME')
if os.getenv('PANIC_LOG_LEN') != None:
    panic_length = int(os.getenv('PANIC_LOG_LEN'))
else:
    print("Panic log length not set, defaulting to 50.")
    panic_length = 50

def setup(bot):
    bot.add_cog(logging(bot))
    print("Megabot Logging module loaded")
    if logurl == "/logs":
        print("   WARN: Log URL not set, defaulting to internal HTTP server.")
    if panic_word == "":
        print("   WARN: Panic word not set, unable to create panic logs.")

async def run(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()

async def optcheck(self, ctx):
    try:
        if ctx.author.id in self.optouts[ctx.guild.id]:
            return True
        else:
            return False
    except KeyError:
        return False

async def logcheck(self, ctx=None, channel=None, guild=None):
    if ctx != None:
        try:
            if ctx.channel.id in self.nolog[ctx.guild.id]:
                return True
            else:
                return False
        except KeyError:
            return False
    else:
        try:
            if channel.id in self.nolog[guild.id]:
                return True
            else:
                return False
        except KeyError:
            return False

async def generateLog(self, mode, ctx=None, channel=None, after=None,):
    loggedMessages = 0

    async def savelog():
        try:
            async with aiofiles.open(f'logs/log.json', 'w') as outfile:
                await outfile.write(json.dumps(self.log))
            with open('optouts/lastlogged.json', 'w') as outfile:
                json.dump(self.lastlogged, outfile)
            return True
        except Exception as e:
            print("Error saving logs: {}".format(e))
            return False

    async def livelog(self, ctx):
        if await logcheck(self, ctx):
            return
        message = ctx
        channel = str(ctx.channel.id)
        guild = str(ctx.guild.id)
        
        dt_str = str(datetime.now().date()) + "/" + str(datetime.now().time())
        
        if not guild in self.log.keys():
            self.log[guild] = {'name': ctx.guild.name, 'channels': {}}
        if not channel in self.log[guild]['channels'].keys():
            self.log[guild]['channels'][channel] = {'name': ctx.channel.name, 'messages': {}}
        if not str(message.id) in self.log[guild]['channels'][channel]['messages'].keys():
            self.log[guild]['channels'][channel]['messages'][str(ctx.id)] = {}
            if not await optcheck(self, ctx):
                self.log[guild]['channels'][channel]['messages'][str(ctx.id)]["author"] = {"author_id": ctx.author.id, "author_displayname": ctx.author.name}
            else:
                self.log[guild]['channels'][channel]['messages'][str(ctx.id)]["author"] = {"author_id": "Opted out", "author_displayname": "Opted out"}
            self.log[guild]['channels'][channel]['messages'][str(ctx.id)]["content"] = ctx.clean_content
            self.log[guild]['channels'][channel]['messages'][str(ctx.id)]["created_at"] = ctx.created_at.timestamp()
            self.log[guild]['channels'][channel]['messages'][str(ctx.id)]["attachments"] = {}
            if ctx.attachments:
                if not os.path.exists("logs/{}/{}/images".format(guild, channel)):
                    os.makedirs("logs/{}/{}/images".format(guild, channel))
                for attachment in ctx.attachments:
                    dlpath = "logs/{}/{}/images/{}-{}".format(guild, channel, dt_str, attachment.filename)
                    await run("curl --create-dirs {} -o {}".format(attachment.url, dlpath))
                    await run("chmod -R 777 logs")
                    b = {'filename': attachment.filename, 'url': "{}/{}/{}/images/{}-{}".format(logurl, guild, channel, dt_str, attachment.filename)}
                    self.log[guild]['channels'][channel]['messages'][str(ctx.id)]["attachments"][attachment.id] = b
        if str(ctx.guild.id) not in self.lastlogged:
            self.lastlogged[str(ctx.guild.id)] = {}
        self.lastlogged[str(ctx.guild.id)][str(ctx.channel.id)] = {}
        self.lastlogged[str(ctx.guild.id)][str(ctx.channel.id)] = ctx.id
        with open('optouts/lastlogged.json', 'w') as outfile:
            try:
                json.dump(self.lastlogged, outfile)
            except:
                raise

    async def makelog(self, channel, mode, guild, after=None, sender=None):
        loggedMessages = 0
        tolog = 0
        try:
            if mode == 1:
                self.log[str(guild.id)]['channels'][str(channel.id)]['messages'] = {}
                tolog = await channel.history(limit=None, oldest_first=True, after=after).flatten()
                await sender.send("{} messages to log.".format(len(tolog)))
            async for message in channel.history(limit=None, oldest_first=True, after=after):
                if guild.id in self.optouts and message.author.id in self.optouts[guild.id]:
                    a = {'author':{'author_id': 'Opted out', 'author_displayname': 'Opted Out'}, 'content': message.clean_content, 'created_at': message.created_at.timestamp(), 'attachments': {}}
                else:
                    a = {'author':{'author_id': message.author.id, 'author_displayname': message.author.display_name}, 'content': message.clean_content, 'created_at': message.created_at.timestamp(), 'attachments': {}}
                if message.attachments:
                    for attachment in message.attachments:
                        dt_str = str(message.created_at.date()) + "/" + str(message.created_at.time())
                        dlpath = "logs/{}/{}/images/{}-{}".format(guild.id, channel.id, dt_str, attachment.filename)
                        if not os.path.exists(dlpath):
                            await run("curl --create-dirs {} -o {}".format(attachment.url, dlpath))
                            await run("chmod -R 777 logs")
                        else:
                            print("file exists in local cache")
                        b = {'filename': attachment.filename, 'url': "{}/{}/{}/images/{}-{}".format(logurl, guild.id, channel.id, dt_str, attachment.filename)}
                        a["attachments"][attachment.id] = b
                self.log[str(guild.id)]['channels'][str(channel.id)]['messages'][message.id] = a
                self.lastlogged[str(guild.id)][str(channel.id)] = message.id
                loggedMessages += 1
                print ("logged {} message(s) from channel {}.".format(loggedMessages, channel.name))
                if mode == 1:
                    if loggedMessages == 1:
                        completion = await sender.send("```.................................................. 0%```")
                    if loggedMessages == round(len(tolog)*0.1):
                        await completion.edit(content="```#####............................................. 10%```")
                    if loggedMessages == round(len(tolog)*0.2):
                        await completion.edit(content="```##########........................................ 20%```")
                    if loggedMessages == round(len(tolog)*0.3):
                        await completion.edit(content="```###############................................... 30%```")
                    if loggedMessages == round(len(tolog)*0.4):
                        await completion.edit(content="```####################.............................. 40%```")
                    if loggedMessages == round(len(tolog)*0.5):
                        await completion.edit(content="```#########################......................... 50%```")
                    if loggedMessages == round(len(tolog)*0.6):
                        await completion.edit(content="```##############################.................... 60%```")
                    if loggedMessages == round(len(tolog)*0.7):
                        await completion.edit(content="```###################################............... 70%```")
                    if loggedMessages == round(len(tolog)*0.8):
                        await completion.edit(content="```########################################.......... 80%```")
                    if loggedMessages == round(len(tolog)*0.9):
                        await completion.edit(content="```#############################################..... 90%```")
                    if loggedMessages == round(len(tolog)*1):
                        await completion.edit(content="```################################################## 100%```", delete_after=10)
                if loggedMessages % 100000 == 0:
                    await savelog()
            if loggedMessages > 0:
                await savelog()
        except discord.errors.Forbidden:
            print("Forbidden")
            return False
        except:
            raise
    
    if mode == 0:
        for i in self.bot.guilds:
            for channel in i.channels:
                if not type(channel) == discord.channel.CategoryChannel and not type(channel) == discord.channel.VoiceChannel:
                    if not await logcheck(self, channel=channel, guild=i):
                        #check if server and channel exist in the log, create if not.
                        if str(i.id) not in self.log:
                            self.log[str(i.id)] = {'name': i.name, 'channels': {}}
                        if str(channel.id) not in self.log[str(i.id)]['channels']:
                            self.log[str(i.id)]['channels'][str(channel.id)] = {'name': channel.name, 'messages': {}}

                        #check if server and channel exist in lastlogged, create if not.
                        if str(i.id) in self.lastlogged:
                            if str(channel.id) in self.lastlogged[str(i.id)]:
                                after = discord.Object(self.lastlogged[str(i.id)][str(channel.id)])
                            else:
                                after = None
                        else:
                            self.lastlogged[str(i.id)] = {}
                            after = None
                        self.logging = channel.id
                        print("Catching up on channel {} in server {}.".format(channel.name, i.name))
                        await makelog(self, channel, mode, guild=i, after=after)
                        self.logging = False
                    else:
                        print("Logs disabled for channel {}, skipping.".format(channel.name))
        print("Catchup complete")

    if mode == 1:
        if AdminCheck.admin(ctx):
            if ctx.guild:
                if ctx.message.channel_mentions:
                    for i in ctx.message.channel_mentions:
                        if ctx.guild.id not in self.nolog:
                            self.logging = i.id
                            await ctx.send("Generating log for channel {}, this may take a few minutes.".format(i.name))
                            print("Generating log for channel {}, this may take a few minutes.".format(i.name))
                            await makelog(self, i, 1, ctx.guild, sender=ctx.channel)
                            self.logging = False
                            await ctx.send("Log Generation complete.")
                        elif i.id not in self.nolog[ctx.guild.id]:
                            self.logging = i.id
                            await ctx.send("Generating log for channel {}, this may take a few minutes.".format(i.name))
                            print("Generating log for channel {}, this may take a few minutes.".format(i.name))
                            await makelog(self, i, 1, ctx.guild, sender=ctx.channel)
                            self.logging = False
                            await ctx.send("Log Generation complete.")
                        else:
                            await ctx.send("Log generation denied, Logs disabled for {}.".format(i.name))
                else:
                    await ctx.send("Please specify a channel to log.")
            else:
                await ctx.send("Log generation denied, logs can only be created for guilds.")
        else:
            await ctx.send("Only administrators can generate full channel logs.")
    
    if mode == 2:
        if ctx.guild:
            if self.logging == False:
                await livelog(self, ctx)
                await savelog()
            else:
                if ctx.channel.id != self.logging:
                    await livelog(self, ctx)
                else:
                    pass

async def loadlog(self):
    if os.path.exists('logs/log.json'):
        async with aiofiles.open('logs/log.json', 'r') as json_data:
            self.log = json.loads(await json_data.read())

class logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.optouts = {}
        self.log = {}
        self.logging = False
        self.newmessage = False
        self.nolog = {}
        self.lastlogged = {}
        self.disconnecttime = None
        if os.path.exists('optouts/optouts.pickle'):
            with open('optouts/optouts.pickle', 'rb') as handle:
                self.optouts = pickle.load(handle)


        if os.path.exists('optouts/lastlogged.json'):
            with open('optouts/lastlogged.json', 'rb') as json_data:
                self.lastlogged = json.load(json_data)
            with open('optouts/lastlogged.json', 'w') as outfile:
                json.dump(self.lastlogged, outfile)

        if os.path.exists('optouts/nolog.pickle'):
            with open('optouts/nolog.pickle', 'rb') as no_log:
                self.nolog = pickle.load(no_log)

        if not os.path.exists('logs'):
            os.makedirs('logs')
        
    @commands.Cog.listener()
    async def on_ready(self):
        await loadlog(self)
        await asyncio.sleep(2)
        await generateLog(self, 0)
    
    @commands.Cog.listener()
    async def on_message(self, ctx):
        await generateLog(self, 2, ctx)

    @commands.command()
    async def makelog(self, ctx):
        await generateLog(self, 1, ctx)

    @commands.command()
    async def disablelog(self, ctx):
        if AdminCheck.admin(ctx):
            if ctx.guild:
                try:    
                    if ctx.guild.id not in self.nolog:
                        self.nolog[ctx.guild.id] = []
                        for i in ctx.message.channel_mentions:
                            self.nolog[ctx.guild.id].append(i.id)
                            await ctx.send("Logs disabled for {}.".format(i.name))
                    else:
                        for i in ctx.message.channel_mentions:
                            if i.id not in self.nolog[ctx.guild.id]:
                                self.nolog[ctx.guild.id].append(i.id)
                                await ctx.send("Logs disabled for {}.".format(i.name))
                            else:
                                await ctx.send("Logs already disabled for {}.".format(i.name))
                    with open('optouts/nolog.pickle', 'wb') as handle:
                        pickle.dump(self.nolog, handle, protocol=pickle.HIGHEST_PROTOCOL)
                except Exception as e:
                    await ctx.send("There was an error opting out. please try again later. \n Here is the exception details\n ```{}```".format(e))
        else:
            await ctx.send("Only admins can disable logs.")

    @commands.command()
    async def enablelog(self, ctx):
        if AdminCheck.admin(ctx):
            if ctx.guild:
                try:    
                    if ctx.guild.id not in self.nolog:
                        self.nolog[ctx.guild.id] = []
                    for i in ctx.message.channel_mentions:
                        if i.id in self.nolog[ctx.guild.id]:
                            self.nolog[ctx.guild.id].remove(i.id)
                            await ctx.send("Logs enabled for {}.".format(i.name))
                        else:
                            await ctx.send("Logs already enabled for {}.".format(i.name))
                    with open('optouts/nolog.pickle', 'wb') as handle:
                        pickle.dump(self.nolog, handle, protocol=pickle.HIGHEST_PROTOCOL)
                except Exception as e:
                    await ctx.send("There was an error opting out. please try again later. \n Here is the exception details\n ```{}```".format(e))
        else:
            await ctx.send("Only admins can enable logs.")

    @commands.command()
    async def optout(self, ctx):
        try:    
            print("optout triggered")
            print(ctx.guild.id)
            if ctx.guild.id not in self.optouts:
                self.optouts[ctx.guild.id] = []
            print(self.optouts)
            self.optouts[ctx.guild.id].append(ctx.author.id)
            print(self.optouts)
            await ctx.send("You have successfully opted out")
            with open('optouts/optouts.pickle', 'wb') as handle:
                pickle.dump(self.optouts, handle, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            await ctx.send("There was an error opting out. please try again later. \n Here is the exception details\n ```{}```".format(e))

    @commands.command()
    async def optin(self, ctx):
        try:
            if ctx.guild.id in self.optouts:
                if ctx.author.id in self.optouts[ctx.guild.id]:
                    self.optouts[ctx.guild.id].remove(ctx.author.id)
                    await ctx.send("You have successfully opted back in.")
                    with open('optouts/optouts.pickle', 'wb') as handle:
                        pickle.dump(self.optouts, handle, protocol=pickle.HIGHEST_PROTOCOL)
                else:
                    await ctx.send("You were never opted out on this server.")
            else:
                await ctx.send("You were never opted out on this server.")
        except Exception as e:
            await ctx.send("There was an error opting in. please try again later. \n Here is the exception details\n ```{}```".format(e))
    @commands.command()
    async def logs(self, ctx):
        if not ctx.guild:
            await ctx.send("I do not log messages sent in DMs")
        else:
            if logurl != "":
                await ctx.send("My recordings can be found at {0}".format(logurl))
            else:
                await ctx.send("Public viewing of logs is not enabled. Contact the administrator for more information")

    @commands.command()
    async def channellog(self, ctx):
        if not ctx.guild:
            await ctx.send("I do not log messages sent in DMs")
        else:
            if logurl != "":
                await ctx.send("My recordings for the channel '{0}' can be found at {1}".format(ctx.channel.name, logurl))
            else:
                await ctx.send("Public viewing of logs is not enabled. Contact the administrator for more information")