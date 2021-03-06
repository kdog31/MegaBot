import discord
from discord.ext import commands
import os
import subprocess
import asyncio
import re
from dotenv import load_dotenv
from datetime import datetime
import pickle

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

async def tail(f, lines=1, _buffer=4098):
    """Tail a file and get X lines from the end"""
    # place holder for the lines found
    lines_found = []

    # block counter will be multiplied by buffer
    # to get the block size from the end
    block_counter = -1

    # loop until we find X lines
    while len(lines_found) < lines:
        try:
            f.seek(block_counter * _buffer, os.SEEK_END)
        except IOError:  # either file is too small, or too many lines requested
            f.seek(0)
            lines_found = f.readlines()
            break

        lines_found = f.readlines()

        # we found enough lines, get out
        # Removed this line because it was redundant the while will catch
        # it, I left it for history
        # if len(lines_found) > lines:
        #    break

        # decrement the block counter to get the
        # next X bytes
        block_counter -= 1
    #print(lines_found[-lines:])
    return lines_found[-lines:]

async def listToString(s):  
    
    # initialize an empty string 
    str1 = " " 
    
    # return string   
    return (str1.join(s))

async def optcheck(self, ctx):
    try:
        if ctx.author.id in self.optouts[ctx.guild.id]:
            return True
        else:
            return False
    except KeyError:
        return False

class logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.optouts = {}
        if os.path.exists('optouts/optouts.pickle'):
            with open('optouts/optouts.pickle', 'rb') as handle:
                self.optouts = pickle.load(handle)

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.guild:
            message = ctx.content
            channel = ctx.channel.name
            guild = ctx.guild.name
            user = ctx.author.name
            
            dt_str = now.strftime("%Y/%m/%d/%H:%M:%S")
            
            if not await optcheck(self, ctx):
                if os.path.exists("logs/{}/{}".format(guild, channel)):
                    open("logs/{}/{}/chat.log".format(guild, channel), "a").write(dt_str + ":" + user + ":" + message + "\n")
                else:
                    os.makedirs("logs/{}/{}".format(guild, channel))
                    open("logs/{}/{}/chat.log".format(guild, channel), "a").write(dt_str + ":" + user + ":" + message + "\n")

                if ctx.attachments:
                    if not os.path.exists("logs/{}/{}/images".format(guild, channel)):
                        os.makedirs("logs/{}/{}/images".format(guild, channel))
                    
                    open("logs/{}/{}/chat.log".format(guild, channel), "a").write("\tattachment stored at https://logs.hal9k.dev/{}/{}/images/{}-{}\n".format(guild, channel, dt_str, ctx.attachments[0].filename))
                    dlpath = "logs/{}/{}/images/{}-{}".format(guild, channel, dt_str, ctx.attachments[0].filename)
                    await run("curl --create-dirs {} -o {}".format(ctx.attachments[0].url, dlpath))
                await run("chown -R 33:33 logs")
            else:
                if os.path.exists("logs/{}/{}".format(guild, channel)):
                    open("logs/{}/{}/chat.log".format(guild, channel), "a").write("An opted out user sent a message. \n")
                else:
                    os.makedirs("logs/{}/{}".format(guild, channel))
                    open("logs/{}/{}/chat.log".format(guild, channel), "a").write("An opted out user sent a message. \n")
            
            if panic_word != "":
                if panic_word in message and ctx.author.bot == False:
                    await ctx.channel.send("Panic word '**{}**' detected, compiling log for download.".format(panic_word))
                    log = open("logs/{}/{}/chat.log".format(guild, channel), "r")
                    paniclog = await tail(log, panic_length, 4098)
                    if not os.path.exists("logs/{}/{}/panic".format(guild, channel)):
                        os.makedirs("logs/{}/{}/panic".format(guild, channel))
                    output = await listToString(paniclog)
                    open("logs/{}/{}/panic/panic.log".format(guild, channel), "w").write(output)
                    await ctx.channel.send("Panic log completed, you may view it at {1}/{2}/{0}/panic/panic.log".format(ctx.channel.name, logurl, ctx.guild.name))
        else:
            pass

    @commands.command()
    async def logs(self, ctx):
        if not ctx.guild:
            await ctx.send("I do not log messages sent in DMs")
        else:
            if logurl != "":
                await ctx.send("My recordings can be found at {0}/{1}".format(logurl, ctx.guild.name))
            else:
                await ctx.send("Public viewing of logs is not enabled. Contact the administrator for more information")

    @commands.command()
    async def channellog(self, ctx):
        if not ctx.guild:
            await ctx.send("I do not log messages sent in DMs")
        else:
            if logurl != "":
                await ctx.send("My recordings for the channel '{0}' can be found at {1}/{2}/{0}".format(ctx.channel.name, logurl, ctx.guild.name))
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

    @commands.command()
    async def createlogs(self, ctx, limit: int=5):
        print("creating logs")
        messages = []
        async for message in ctx.channel.history(limit=limit, before=None, after=None, around=None, oldest_first=None):
            messages.append([message.content, message.author.display_name])
        messages.reverse()
        print(messages)
        await ctx.send("check the logs!")