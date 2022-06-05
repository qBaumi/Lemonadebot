import datetime
import math

from riotwatcher import ApiError
from twitchio.ext import commands
from config import cooldown
import utils, json
from twitchio.ext import routines
from config import watcher

class League(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.cooldown(rate=1, per=cooldown, bucket=commands.Bucket.user)
    @commands.command(aliases=["players"])
    async def player(self, ctx: commands.Context):

        region, match_region, summonername = utils.getChannelSummoner(ctx.channel.name)

        def getChampFromId(id):
            for champ in self.champions:
                if self.champions[champ]["key"] == str(id):
                    # print(dicts[champ]["id"])
                    return self.champions[champ]["id"]

        try:
            me = watcher.summoner.by_name(region, summonername)
            game = watcher.spectator.by_summoner(region, me["id"])
            out = f""
            for participant in game["participants"]:
                name = participant["summonerName"]
                champ = getChampFromId(participant["championId"])
                out += f"{name}({champ}), "
            out = out[0:len(out) - 2]
            await ctx.send(out)
        except ApiError as err:
            await utils.err_msg(err, ctx)

    @commands.cooldown(rate=1, per=cooldown, bucket=commands.Bucket.user)
    @commands.command(aliases=["rune"])
    async def runes(self, ctx: commands.Context):

        region, match_region, summonername = utils.getChannelSummoner(ctx.channel.name)

        def getRuneFromId(id):
            for tree in self.runes:
                for something in tree["slots"]:
                    for rune in something["runes"]:
                        name = rune["name"]
                        runeid = rune["id"]
                        if id == runeid:
                            return name

        def getShardRune(id):
            if id == 5005:
                return "AS"
            elif id == 5008:
                return "DMG"
            elif id == 5002:
                return "ARM"
            elif id == 5007:
                return "CDR"
            elif id == 5003:
                return "MR"
            elif id == 5001:
                return "HP"

        try:
            me = watcher.summoner.by_name(region, summonername)
            game = watcher.spectator.by_summoner(region, me["id"])
            out = f""
            for participant in game["participants"]:
                name = participant["summonerName"]
                if name == summonername:
                    runes = participant["perks"]["perkIds"]
                    out = f'{getRuneFromId(runes[0])}: {getRuneFromId(runes[1])}, {getRuneFromId(runes[2])}, {getRuneFromId(runes[3])} | {getRuneFromId(runes[4])}, {getRuneFromId(runes[5])} | {getShardRune(runes[6])}, {getShardRune(runes[7])}, {getShardRune(runes[8])}'
            await ctx.send(out)
        except ApiError as err:
            await utils.err_msg(err, ctx)

    @commands.cooldown(rate=1, per=cooldown, bucket=commands.Bucket.user)
    @commands.command(aliases=["lp"])
    async def rank(self, ctx: commands.Context):

        my_region, match_region, summonername = utils.getChannelSummoner(ctx.channel.name)

        try:
            me = watcher.summoner.by_name(my_region, summonername)
            my_ranked_stats = watcher.league.by_summoner(my_region, me['id'])

            i = 0

            for queuetype in my_ranked_stats:

                if my_ranked_stats[i]['queueType'] == 'RANKED_SOLO_5x5':
                    rank = my_ranked_stats[i]['tier'].lower()
                    rank = rank.capitalize()
                    out = f"@{ctx.author.name} {rank} {my_ranked_stats[i]['leaguePoints']}lp {my_ranked_stats[i]['wins']} wins {my_ranked_stats[i]['losses']} losses"

                i = i + 1
            await ctx.send(out)
        except ApiError as err:
            await utils.err_msg(err, ctx)
            return

    @commands.cooldown(rate=1, per=cooldown, bucket=commands.Bucket.user)
    @commands.command(aliases=["winrate", "losses", "daily", "wins"])
    async def stats(self, ctx: commands.Context):
        my_region, match_region, summonername = utils.getChannelSummoner(ctx.channel.name)

        try:

            me = watcher.summoner.by_name(my_region, summonername)
            matches = utils.getMatchesOfToday(match_region, me)
            savedMatches = utils.getMatches()
            date = utils.getDate()
            wins = 0
            losses = 0

            for matchid in matches:

                # Check if match is saved and then get the win/lose by the lp
                isInList = False
                try:
                    for smatch in savedMatches[date]["matches"]:
                        if smatch["matchid"] == matchid:
                            isInList = True
                            if smatch["lpgain"] < 0:
                                losses += 1
                            else:
                                wins += 1
                except:
                    pass

                # fetch the match otherwise
                if not isInList:
                    match = watcher.match.by_id(match_region, matchid)
                    for participant in match["info"]["participants"]:
                        if participant["puuid"] == me["puuid"]:
                            if participant["win"] == True:
                                wins += 1
                            else:
                                losses += 1
                            break

            if losses == 0 and wins > 0:
                out = f"@{ctx.author.name} Todays wins/losses {wins}/{losses}, winrate: 100%"
            elif losses == 0 and wins == 0:
                out = f"@{ctx.author.name} No ranked games played today :/"
            else:
                out = f"@{ctx.author.name} Todays wins/losses {wins}/{losses}, winrate: {int((wins / (wins + losses)) * 100)}%"

            # Get LP Gain if channel is nemesis
            if ctx.channel.name == "lol_nemesis" and not out.endswith(":/"):
                try:
                    startlp, lpgain = utils.getDailyLPGain()
                    if lpgain < 0:
                        s = "lost"
                    else:
                        s = "gained"
                    out += f", started with {startlp} LP, {s} {lpgain}LP in total today"
                except:
                    pass

            await ctx.send(out)
        except ApiError as err:
            await utils.err_msg(err, ctx)
            return

    @commands.cooldown(rate=1, per=cooldown, bucket=commands.Bucket.user)
    @commands.command()
    async def lastgame(self, ctx: commands.Context):
        my_region, match_region, summonername = utils.getChannelSummoner(ctx.channel.name)

        try:
            summoner = watcher.summoner.by_name(my_region, summonername)
            current_timestamp = datetime.datetime.now().timestamp() * 1000
            matches = watcher.match.matchlist_by_puuid(match_region, summoner['puuid'])
            lastgame = watcher.match.by_id(match_region, matches[0])
            gameEndTimeStamp = lastgame["info"]["gameEndTimestamp"]
            type = utils.getGameType(lastgame)

            # Get win or loss
            for participant in lastgame["info"]["participants"]:
                if participant["puuid"] == summoner["puuid"]:
                    if participant["win"] == True:
                        win = "won"
                    else:
                        win = "lost"
                    champ = participant["championName"]
                    kda = f'{participant["kills"]}/{participant["deaths"]}/{participant["assists"]}'
                    break

            # timestamp into minutes
            mins = int((current_timestamp - gameEndTimeStamp) / 60000)
            # transform mins into hours + mins
            if mins > 60:
                hours = math.floor(mins / 60)
                mins = mins / 60 - hours
                mins = int(mins * 60)
                out = f"{hours} hours and {mins} minutes"
            else:
                out = f"{mins} minutes"

            await ctx.send(f"@{ctx.author.name} Last game ({type}, {champ}, {kda}) was played {out} ago and was {win}")
        except ApiError as err:
            await utils.err_msg(err, ctx)




def prepare(bot: commands.Bot):
    bot.add_cog(League(bot))
