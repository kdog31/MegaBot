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

async def generateLog(self, ctx):
    if AdminCheck.admin(ctx):
        self.logging = True
        print("Generating logs for channel {} in server {}".format(ctx.channel.id, ctx.guild.id))
        await ctx.send("Generating log, this may take a minute...")
        print(self.log)
        if ctx.guild.id not in self.log:
            self.log[ctx.guild.id] = {}
            print("channel id created")
        self.log[ctx.guild.id][ctx.channel.id] = {}
        print("channel id set to empty dict")
        loggedmessages = 0
        print("logged messages set to 0")
        async for message in ctx.channel.history(limit=None, oldest_first=True):
            print("begin iteration")
            print(self.optouts)
            print(message.author.id)
            if ctx.guild.id in self.optouts:
                if message.author.id in self.optouts[ctx.guild.id]:
                    print("opted out")
                    a = {'author':{'author_id': 'Opted out', 'author_displayname': 'Opted Out'}, 'content': message.clean_content, 'attachments': {}}
                else:
                    print("not opted out")
                    a = {'author':{'author_id': message.author.id, 'author_displayname': message.author.display_name}, 'content': message.clean_content, 'attachments': {}}
            else:
                print("not opted out")
                a = {'author':{'author_id': message.author.id, 'author_displayname': message.author.display_name}, 'content': message.clean_content, 'attachments': {}}
            print("author set to {}".format(a))
            if message.attachments:
                for attachment in message.attachments:
                    dt_str = str(message.created_at.date()) + "/" + str(message.created_at.time())
                    dlpath = "logs/{}/{}/images/{}-{}".format(ctx.guild.id, ctx.channel.id, dt_str, attachment.filename)
                    await run("curl --create-dirs {} -o {}".format(attachment.url, dlpath))
                    await run("chmod -R 777 logs")
                    b = {'filename': attachment.filename, 'url': "{}/{}/{}/images/{}-{}".format(logurl, ctx.guild.id, ctx.channel.id, dt_str, attachment.filename)}
                    a["attachments"][attachment.id] = b
            self.log[ctx.guild.id][ctx.channel.id][message.id] = a
            loggedmessages += 1
            print("Logged messages {}".format(loggedmessages))
            
        with open('logs/log.json', 'w') as outfile:
            json.dump(self.log, outfile)
        print("Log Generation complete.")
        self.logging = False
        await ctx.send("Log generation complete, logged {} messages".format(loggedmessages))
        #print(self.log[ctx.guild.id][ctx.channel.id])
    else:
        await ctx.send("Only Administrators can create a backdated log")

class logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.optouts = {}
        self.log = {}
        self.logging = False
        self.newmessage = False
        if os.path.exists('optouts/optouts.pickle'):
            with open('optouts/optouts.pickle', 'rb') as handle:
                self.optouts = pickle.load(handle)
        if os.path.exists('logs/log.json'):
            with open('logs/log.json', 'rb') as json_data:
                self.log = json.load(json_data)
            with open('logs/log.json', 'w') as outfile:
                json.dump(self.log, outfile)
        if not os.path.exists('logs'):
            os.makedirs('logs')

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if self.logging == False:
            if ctx.guild:
                message = ctx
                channel = ctx.channel.id
                guild = ctx.guild.id
                user = ctx.author.id
                
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
                with open('logs/log.json', 'w') as outfile:
                    json.dump(self.log, outfile)
            else:
                pass
        else:
            self.newmessage = True
    
    @commands.command()
    async def makelog(self, ctx):
        await generateLog(self, ctx)

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