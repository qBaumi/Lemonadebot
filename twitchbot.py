import datetime

from twitchio.ext import commands, routines

import dbutils
import utils
from config import token, lastfm_api_key, lastfm_api_secret, watcher, cooldown


class Bot(commands.Bot):

    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...
        super().__init__(token=token, prefix=['lem ', 'LEM ', 'LeM ', 'LEm ', 'Lem ', 'lEM ', 'leM '],
                         initial_channels=['lol_nemesis', 'qbaumi', 'deceiver_euw', 'thedisconnect'],
                         nick="Lemon Bot", case_insensitive=True)
        # Now get the champions loaded
        versions = watcher.data_dragon.versions_for_region("kr")
        champions_version = versions['n']['champion']
        self.champions = watcher.data_dragon.champions(champions_version)["data"]
        self.runes = watcher.data_dragon.runes_reforged(champions_version)
        self.emotes = []

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')
        # start the routine // in the cog now
        self.update_matches_loop.start(stop_on_error=False)
        self.update_emotes_loop.start(stop_on_error=False)
        # channel = await self.fetch_channel("qbaumi2004")
        # print(channel)

    async def event_message(self, message):
        # Messages with echo set to True are messages sent by the bot...
        if message.echo:
            return

        if message.content.startswith("lem "):
            # print(f"{message.author.name}: {message.content}")
            command = message.content.lower()[4:len(message.content)]
            try:
                dbutils.addcommandtostats(message.author.id, message.author.name, command)
            except:
                pass
        # Since we have commands and are overriding the default `event_message`
        # We must let the bot know we want to handle and invoke our commands...
        await self.handle_commands(message)

        if message.channel.name.lower() != "lol_nemesis":
            return
        emotesinmessage = []
        for word in str(message.content).split():
            if word in self.emotes and word not in emotesinmessage:
                emotesinmessage.append(word)
        dbutils.addemotes(emotesinmessage)

    @commands.cooldown(rate=1, per=cooldown, bucket=commands.Bucket.user)
    @commands.command()
    async def help(self, ctx: commands.Context):
        await ctx.send(
            f'@{ctx.author.name} https://lemonadebot.pages.dev')

    @routines.routine(minutes=5)
    async def update_matches_loop(self):
        # Get summoner, ranked stats and match history
        accounts = [utils.getNemesisAccountName()]
        for account in accounts:
            summoner = watcher.summoner.by_name("euw1", account)
            ranked_stats = watcher.league.by_summoner("euw1", summoner['id'])
            matches = utils.getMatchesOfToday("europe", summoner)
            lp = utils.getLP(ranked_stats)
            if matches:
                dbutils.savematch(matches[0], lp, account)

    @routines.routine(minutes=15)
    async def update_emotes_loop(self):
        self.emotes = utils.getAllEmotes()
        print("Emotes loaded")


bot = Bot()
bot.load_module("cogs.Other")
bot.load_module("cogs.Song")
bot.load_module("cogs.League")
bot.load_module("cogs.Mods")
bot.load_module("cogs.Gamba")
bot.run()
