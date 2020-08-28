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

load_dotenv()
logurl = os.getenv('LOG_URL')
panic_word = os.getenv('PANIC_WORD')
bot_name = os.getenv('BOT_NAME')
if os.getenv('PANIC_LOG_LEN') != None:
    panic_length = int(os.getenv('PANIC_LOG_LEN'))
else:
    print("Panic log length not set, defaulting to 50.")
    panic_length = 50

now = datetime.now()

def setup(bot):
    bot.add_cog(logging(bot))
    print("MegaBot Logging module loaded")
    if logurl == "":
        print("   WARN: Log URL not set, automatic log publishing disabled.")
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

async def logcheck(self, ctx):
    try:
        if ctx.channel.id in self.nolog[ctx.guild.id]:
            return True
        else:
            return False
    except KeyError:
        return False

async def generateLog(self, ctx, mentions=None, after=None):
    loggedmessages = 0
    self.logging = mentions.id
    print("Generating logs for channel {} in server {}".format(mentions.id, ctx.guild.id))
    await ctx.send("Generating log for channel {}, this may take a minute...".format(mentions.name))
    if ctx.guild.id not in self.log:
        self.log[ctx.guild.id] = {}
    self.log[ctx.guild.id][mentions.id] = {}
    if str(ctx.guild.id) not in self.lastlogged:
        self.lastlogged[str(ctx.guild.id)] = {}
    self.lastlogged[str(ctx.guild.id)][str(mentions.id)] = {}
    async for message in mentions.history(limit=None, oldest_first=True, after=after):
        if ctx.guild.id in self.optouts:
            if message.author.id in self.optouts[ctx.guild.id]:
                a = {'author':{'author_id': 'Opted out', 'author_displayname': 'Opted Out'}, 'content': message.clean_content, 'created_at': message.created_at.timestamp(), 'attachments': {}}
            else:
                a = {'author':{'author_id': message.author.id, 'author_displayname': message.author.display_name}, 'content': message.clean_content, 'created_at': message.created_at.timestamp(), 'attachments': {}}
        else:
            a = {'author':{'author_id': message.author.id, 'author_displayname': message.author.display_name}, 'content': message.clean_content, 'created_at': message.created_at.timestamp(), 'attachments': {}}
        if message.attachments:
            for attachment in message.attachments:
                dt_str = str(message.created_at.date()) + "/" + str(message.created_at.time())
                dlpath = "logs/{}/{}/images/{}-{}".format(ctx.guild.id, mentions.id, dt_str, attachment.filename)
                if not os.path.exists(dlpath):
                    await run("curl --create-dirs {} -o {}".format(attachment.url, dlpath))
                    await run("chmod -R 777 logs")
                else:
                    print("file already exists in local cache")
                b = {'filename': attachment.filename, 'url': "{}/{}/{}/images/{}-{}".format(logurl, ctx.guild.id, mentions.id, dt_str, attachment.filename)}
                a["attachments"][attachment.id] = b
        self.log[ctx.guild.id][mentions.id][message.id] = a
        self.lastlogged[str(ctx.guild.id)][str(mentions.id)] = message.id
        loggedmessages += 1
        print("Logged {} message(s)".format(loggedmessages))
        if loggedmessages % 1000 == 0:
            with open('logs/log.json', 'w') as outfile:
                json.dump(self.log, outfile)
                print("log dumped")
            with open('optouts/lastlogged.json', 'w') as outfile:
                json.dump(self.lastlogged, outfile)
                print("lastlogged saved")
        
    with open('logs/log.json', 'w') as outfile:
        try:
            json.dump(self.log, outfile)
        except:
            raise
    with open('optouts/lastlogged.json', 'w') as outfile:
        try:
            json.dump(self.lastlogged, outfile)
        except:
            raise
    print("Log Generation complete.")
    self.logging = False
    await ctx.send("Log generation complete, logged {} messages".format(loggedmessages))

async def livelog(self, ctx):
    if await logcheck(self, ctx):
        return
    message = ctx
    channel = ctx.channel.id
    guild = ctx.guild.id
    
    dt_str = str(datetime.now().date()) + "/" + str(datetime.now().time())
    
    if not guild in self.log.keys():
        self.log[guild] = {}
    if not channel in self.log[guild].keys():
        self.log[guild][channel] = {}
    if not message.id in self.log[guild][channel].keys():
        self.log[guild][channel][ctx.id] = {}
        if not await optcheck(self, ctx):
            self.log[guild][channel][ctx.id]["author"] = {"author_id": ctx.author.id, "author_displayname": ctx.author.name}
        else:
            self.log[guild][channel][ctx.id]["author"] = {"author_id": "Opted out", "author_displayname": "Opted out"}
        self.log[guild][channel][ctx.id]["content"] = ctx.clean_content
        self.log[guild][channel][ctx.id]["created_at"] = ctx.created_at.timestamp()
        self.log[guild][channel][ctx.id]["attachments"] = {}
        if ctx.attachments:
            if not os.path.exists("logs/{}/{}/images".format(guild, channel)):
                os.makedirs("logs/{}/{}/images".format(guild, channel))
            for attachment in ctx.attachments:
                dlpath = "logs/{}/{}/images/{}-{}".format(guild, channel, dt_str, attachment.filename)
                await run("curl --create-dirs {} -o {}".format(attachment.url, dlpath))
                await run("chmod -R 777 logs")
                b = {'filename': attachment.filename, 'url': "{}/{}/{}/images/{}-{}".format(logurl, guild, channel, dt_str, attachment.filename)}
                self.log[guild][channel][ctx.id]["attachments"][attachment.id] = b
    if str(ctx.guild.id) not in self.lastlogged:
        self.lastlogged[str(ctx.guild.id)] = {}
    self.lastlogged[str(ctx.guild.id)][str(ctx.channel.id)] = {}
    self.lastlogged[str(ctx.guild.id)][str(ctx.channel.id)] = ctx.id
    with open('optouts/lastlogged.json', 'w') as outfile:
        try:
            json.dump(self.lastlogged, outfile)
        except:
            raise

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

        if os.path.exists('logs/log.json'):
            with open('logs/log.json', 'rb') as json_data:
                self.log = json.load(json_data)
            with open('logs/log.json', 'w') as outfile:
                json.dump(self.log, outfile)

        if os.path.exists('optouts/lastlogged.json'):
            with open('optouts/lastlogged.json', 'rb') as json_data:
                self.lastlogged = json.load(json_data)
            with open('optouts/lastlogged.json', 'w') as outfile:
                json.dump(self.lastlogged, outfile)
            print(self.lastlogged)

        if os.path.exists('optouts/nolog.pickle'):
            with open('optouts/nolog.pickle', 'rb') as no_log:
                self.nolog = pickle.load(no_log)

        if not os.path.exists('logs'):
            os.makedirs('logs')

    @commands.Cog.listener()
    async def on_disconnect(self):
        if self.disconnecttime == None:
            self.disconnecttime = datetime.now()
            print("Offline")
        else:
            pass

    @commands.Cog.listener()
    async def on_ready(self):
        for i in self.bot.guilds:
            for channel in i.channels:
                if channel.id not in self.nolog[i.id]:
                    n = 0
                    if not type(channel) == discord.channel.CategoryChannel and not type(channel) == discord.channel.VoiceChannel:
                        if i.id not in self.log:
                            self.log[i.id] = {}
                        if channel.id not in self.log[i.id]:
                            self.log[i.id][channel.id] = {}
                        
                        if str(i.id) not in self.lastlogged:
                            self.lastlogged[str(i.id)] = {}
                        if str(i.id) in self.lastlogged:
                            #print(self.lastlogged[str(i.id)])
                            if str(channel.id) in self.lastlogged[str(i.id)]:
                                after = discord.Object(self.lastlogged[str(i.id)][str(channel.id)])
                            else:
                                after = None
                        else:
                            after = None
                        async for message in channel.history(limit=None, oldest_first=True, after=after):
                            if i.id in self.optouts:
                                if message.author.id in self.optouts[i.id]:
                                    a = {'author':{'author_id': 'Opted out', 'author_displayname': 'Opted Out'}, 'content': message.clean_content, 'created_at': message.created_at.timestamp(), 'attachments': {}}
                                else:
                                    a = {'author':{'author_id': message.author.id, 'author_displayname': message.author.display_name}, 'content': message.clean_content, 'created_at': message.created_at.timestamp(), 'attachments': {}}
                            else:
                                a = {'author':{'author_id': message.author.id, 'author_displayname': message.author.display_name}, 'content': message.clean_content, 'created_at': message.created_at.timestamp(), 'attachments': {}}
                            if message.attachments:
                                for attachment in message.attachments:
                                    dt_str = str(message.created_at.date()) + "/" + str(message.created_at.time())
                                    dlpath = "logs/{}/{}/images/{}-{}".format(i.id, channel.id, dt_str, attachment.filename)
                                    if not os.path.exists(dlpath):
                                        await run("curl --create-dirs {} -o {}".format(attachment.url, dlpath))
                                        await run("chmod -R 777 logs")
                                    else:
                                        print("file already exists in local cache")
                                    b = {'filename': attachment.filename, 'url': "{}/{}/{}/images/{}-{}".format(logurl, i.id, channel.id, dt_str, attachment.filename)}
                                    a["attachments"][attachment.id] = b
                            self.log[i.id][channel.id][message.id] = a
                            self.lastlogged[str(i.id)][str(channel.id)] = message.id
                            if n % 100 == 0:
                                with open('optouts/lastlogged.json', 'w') as outfile:
                                    json.dump(self.lastlogged, outfile)
                                with open('logs/log.json', 'w') as outfile:
                                    json.dump(self.log, outfile)
            with open('optouts/lastlogged.json', 'w') as outfile:
                json.dump(self.lastlogged, outfile)
            with open('logs/log.json', 'w') as outfile:
                json.dump(self.log, outfile)
            print("Logs updated")



    @commands.Cog.listener()
    async def on_message(self, ctx):
        if self.logging == False:
            if ctx.guild:
                await livelog(self, ctx)
                with open('logs/log.json', 'w') as outfile:
                    json.dump(self.log, outfile)
            else:
                pass
        else:
            if ctx.channel.id != self.logging:
                if ctx.guild:
                    await livelog(self, ctx)
            else:
                pass
    
    @commands.command()
    async def makelog(self, ctx):
        if AdminCheck.admin(ctx):
            if ctx.guild:
                if ctx.message.channel_mentions:
                    for i in ctx.message.channel_mentions:
                        if ctx.guild.id not in self.log:
                            print(i)
                            await generateLog(self, ctx, i)
                        if i.id not in self.nolog[ctx.guild.id]:
                            print(i)
                            await generateLog(self, ctx, i)
                        else:
                            await ctx.send("Log generation denied, Logs disabled for channel {}.".format(i.name))
                else:
                    await ctx.send("Please specify a channel to log")
            else:
                await ctx.send("Log generation denied, Logs may only be created for servers.")
        else:
            await ctx.send("Only admins can generate backdated logs")

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