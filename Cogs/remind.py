import parsedatetime as pd
import discord
from discord.ext import commands, tasks
from datetime import datetime
from Cogs import Settings

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
                print("loaded")
                self.reminders = self.settings['reminders']
            else:
                print("else")
                self.reminders = []
                self.settings['reminders'] = []
                await Settings.setting.save(self.settings)
        except KeyError:
            print("keyerror")
            self.settings = await Settings.setting.load()
            self.settings['reminders'] = []
            await Settings.setting.save(self.settings)
            self.reminders = []
        self.reminder_loop.start()
        print(self.settings)

    @commands.command(name="remind")
    async def remind(self, ctx, *, text):
        cal = pd.Calendar()
        time_struct, parse_status = cal.parse(text)
        a = datetime(*time_struct[:6])
        self.settings = await Settings.setting.load()
        self.reminders.append([[a.year, a.month, a.day, a.hour, a.minute, a.second], ctx.author.id, ctx.channel.id, text])
        self.settings['reminders'] = self.reminders
        await Settings.setting.save(self.settings)

    @tasks.loop(seconds=1)
    async def reminder_loop(self):
        now = datetime.now()
        for i in self.reminders:
            a_load = i[0]
            b = datetime(a_load[0], a_load[1], a_load[2], a_load[3], a_load[4], a_load[5])
            if now > b:
                channel = self.bot.get_channel(i[2])
                await channel.send("Hey <@{}>, you asked me to remind you to: {}".format(i[1], i[3]))
                self.reminders.remove(i)
                await Settings.setting.save(self.settings)
        

