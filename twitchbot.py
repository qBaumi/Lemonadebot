import datetime

from twitchio.ext import commands, routines
import utils
from config import token, lastfm_api_key, lastfm_api_secret, watcher, cooldown



class Bot(commands.Bot):

    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...
        super().__init__(token=token, prefix=['lem ', 'LEM ', 'LeM ', 'LEm ', 'Lem ', 'lEM ', 'leM '],
                         initial_channels=['lol_nemesis', 'qbaumi2004', 'deceiver_euw', 'thedisconnect', 'rango235', 'lemonadebot_'],
                         nick="Lemon Bot", case_insensitive=True)
        # Now get the champions loaded
        versions = watcher.data_dragon.versions_for_region("kr")
        champions_version = versions['n']['champion']
        self.champions = watcher.data_dragon.champions(champions_version)["data"]
        self.runes = watcher.data_dragon.runes_reforged(champions_version)



    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')
        # start the routine // in the cog now
        self.update_matches_loop.start(stop_on_error=False)
        #channel = await self.fetch_channel("qbaumi2004")
        #print(channel)

    async def event_message(self, message):
        # Messages with echo set to True are messages sent by the bot...
        if message.echo:
            return

        if message.content.startswith("lem "):
            print(f"{message.author.name}: {message.content}")
            command = message.content.lower()[4:len(message.content)]
            # [
            #   {"command" : command, "user" : message.author.name, "userid" : message.author.id, "date" : utils.getDate(), "timestamp" : datetime.datetime.now()}
            # ]
            # {
            #   message.author.id : { "username" : message.author.name, command : data[message.author.id][command] + 1
            # }
            data = utils.getCommandStats()
            try:
                data[message.author.id]
            except:
                data[message.author.id] = {"username": message.author.name}
            try:
                data[message.author.id][command] = data[message.author.id][command] + 1
            except:
                data[message.author.id][command] = 1
            utils.saveCommandStats(data)
        # Since we have commands and are overriding the default `event_message`
        # We must let the bot know we want to handle and invoke our commands...
        await self.handle_commands(message)




    @commands.cooldown(rate=1, per=cooldown, bucket=commands.Bucket.user)
    @commands.command()
    async def account(self, ctx: commands.Context):
        acc = utils.getNemesisAccountName()
        await ctx.send(f"{ctx.author.mention} {acc}")


    @commands.cooldown(rate=1, per=cooldown, bucket=commands.Bucket.user)
    @commands.command()
    async def help(self, ctx: commands.Context):
        await ctx.send(
            f'@{ctx.author.name} This is a list of commands, you need to type lem before them e.g. lem rank, lem song, lem lastgame, lem winrate, lem players, lem runes')

    @routines.routine(minutes=5)
    async def update_matches_loop(self):
        # Get summoner, ranked stats and match history
        summoner = watcher.summoner.by_name("kr", utils.getNemesisAccountName())
        ranked_stats = watcher.league.by_summoner("kr", summoner['id'])
        matches = utils.getMatchesOfToday("asia", summoner)

        date = utils.getDate()
        savedMatches = utils.getMatches()
        lp = utils.getLP(ranked_stats)

        matches.reverse()  # reverse matches so that 0 is first match and x is last match
        try:
            savedMatches[date]
        except:
            savedMatches[date] = {}
            savedMatches[date]["startlp"] = lp
            savedMatches[date]["matches"] = []

        for i, matchid in enumerate(matches):
            # print(f"{i} {matchid}")
            # check if matchid in list
            isInList = False
            for match in savedMatches[date]["matches"]:
                if match["matchid"] == matchid:
                    isInList = True

            if not isInList:
                if i - 1 == -1:
                    lpgain = lp - savedMatches[date]["startlp"]
                    # print("first game")
                    # print(f'{lp} - {savedMatches[date]["startlp"]}')
                else:
                    lpgain = lp - savedMatches[date]["matches"][i - 1]["new_lp"]
                    # print(f'{lp} - {savedMatches[date]["matches"][i - 1]["new_lp"]}')
                savedMatches[date]["matches"].append({"matchid": matchid, "new_lp": lp, "lpgain": lpgain})

        utils.saveMatches(savedMatches)

bot = Bot()
bot.load_module("cogs.Other")
bot.load_module("cogs.Song")
bot.load_module("cogs.League")
bot.load_module("cogs.Mods")
bot.load_module("cogs.Gamba")
bot.run()
