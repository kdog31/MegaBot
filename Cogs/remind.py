import parsedatetime as pd
import discord
from discord.ext import commands, tasks
from datetime import datetime
from Cogs import Settings, processor

def setup(bot):
    bot.add_cog(remind(bot))
    print("MegaBot remind module loaded")

class remind(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            self.settings = await Settings.setting.load()
            if self.settings['reminders']:
                print("Reminders loaded")
                self.reminders = self.settings['reminders']
            else:
                print("No Reminders to load")
                self.reminders = []
                self.settings['reminders'] = []
                await Settings.setting.save(self.settings)
        except KeyError:
            print("Reminders not in settings, fixing")
            self.settings = await Settings.setting.load()
            self.settings['reminders'] = []
            await Settings.setting.save(self.settings)
            self.reminders = []
        self.reminder_loop.start()

    @commands.command(name="remind")
    async def remind(self, ctx, *, text):
        cal = pd.Calendar()
        time_struct, parse_status = cal.parse(text)
        a = datetime(*time_struct[:6])
        self.settings = await Settings.setting.load()
        reminder = await processor.get_reminder("remind {}".format(text))
        if reminder != False:
            self.reminders.append([[a.year, a.month, a.day, a.hour, a.minute, a.second], ctx.author.id, ctx.channel.id, reminder])
            self.settings['reminders'] = self.reminders
            await Settings.setting.save(self.settings)
            await ctx.send("I'll remind you {} at {}".format(reminder, a))
        else:
            await ctx.send("Could not parse reminder, try wording like this ``remind me to do something at some time```")

    @tasks.loop(seconds=1)
    async def reminder_loop(self):
        now = datetime.now()
        for i in self.reminders:
            a_load = i[0]
            b = datetime(a_load[0], a_load[1], a_load[2], a_load[3], a_load[4], a_load[5])
            if now > b:
                channel = self.bot.get_channel(i[2])
                await channel.send("Hey <@{}>, you asked me to remind you {}.".format(i[1], i[3]))
                self.reminders.remove(i)
                await Settings.setting.save(self.settings)
        

