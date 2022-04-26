import json
import pylast
import math
from twitchio.ext import commands
from config import token, api_key, lastfm_api_key, lastfm_api_secret
from riotwatcher import LolWatcher, ApiError
import datetime, time
from twitchio.ext import routines

watcher = LolWatcher(api_key)


class Bot(commands.Bot):

    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...
        super().__init__(token=token, prefix=['lem ', 'LEM', 'LeM', 'LEm', 'Lem', 'lEM', 'leM'],
                         initial_channels=['lol_nemesis', 'qbaumi2004', 'deceiver_euw', 'thedisconnect', 'rango235'],
                         nick="Lemon Bot", case_insensitive=True)
        # Now get the champions loaded
        versions = watcher.data_dragon.versions_for_region("kr")
        champions_version = versions['n']['champion']
        self.champions = watcher.data_dragon.champions(champions_version)["data"]
        self.runes = watcher.data_dragon.runes_reforged(champions_version)

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')
        # start the routine
        self.update_matches_loop.start()


    async def event_message(self, message):
        # Messages with echo set to True are messages sent by the bot...
        if message.echo:
            return

        if message.content.startswith("lem "):
            print(f"{message.author.name}: {message.content}")

        # Since we have commands and are overriding the default `event_message`
        # We must let the bot know we want to handle and invoke our commands...
        await self.handle_commands(message)

    @commands.command()
    async def inem(self, ctx: commands.Context):
        await ctx.send(f'No.')

    @commands.command()
    async def language(self, ctx: commands.Context):
        await ctx.send(f'Only english Habibi')

    @commands.command()
    async def song(self, ctx: commands.Context):
        network = pylast.LastFMNetwork(
            api_key=lastfm_api_key,
            api_secret=lastfm_api_secret,
            # username=username,
            # password_hash=password_hash,
        )
        user = network.get_user("qBaumi")
        print(user)
        current_track = user.get_now_playing()
        print(type(current_track))
        print(current_track)
        if current_track is None:
            out = "No song currently playing"
        else:
            out = f"{current_track.title} - {current_track.artist}"
        await ctx.send(out)

    @commands.command()
    async def help(self, ctx: commands.Context):
        await ctx.send(
            f'@{ctx.author.name} This is a list of commands, you need to type lem before them e.g. lem rank, lem lastgame, lem winrate, lem players, lem runes, (lem song coming soon™)')

    @commands.command(aliases=["players"])
    async def player(self, ctx: commands.Context):

        region, match_region, summonername = getChannelSummoner(ctx.channel.name)

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
            out = out[0:len(out)-2]
            await ctx.send(out)
        except ApiError as err:
            await err_msg(err, ctx)

    @commands.command(aliases=["rune"])
    async def runes(self, ctx: commands.Context):

        region, match_region, summonername = getChannelSummoner(ctx.channel.name)

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
            await err_msg(err, ctx)

    @commands.command(aliases=["lp"])
    async def rank(self, ctx: commands.Context):

        my_region, match_region, summonername = getChannelSummoner(ctx.channel.name)

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
            if err.response.status_code == 429:
                await ctx.send(f'@{ctx.author.name} Connection error')
            elif err.response.status_code == 404:
                await ctx.send(f'@{ctx.author.name} We couldnt find this summoner')
            else:
                raise

    @commands.command(aliases=["winrate", "losses", "daily", "wins"])
    async def stats(self, ctx: commands.Context):
        my_region, match_region, summonername = getChannelSummoner(ctx.channel.name)

        try:

            me = watcher.summoner.by_name(my_region, summonername)
            matches = getMatchesOfToday(match_region, me)
            savedMatches = getMatches()
            date = getDate()
            wins = 0
            losses = 0

            for matchid in matches:

                # Check if match is saved and then get the win/lose by the lp
                isInList = False
                for smatch in savedMatches[date]["matches"]:
                    if smatch["matchid"] == matchid:
                        isInList = True
                        if smatch["lpgain"] < 0:
                            losses += 1
                        else:
                            wins += 1

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
            if losses != 0 and wins != 0 and ctx.channel.name == "lol_nemesis":
                try:
                    startlp, lpgain = getDailyLPGain()
                    if lpgain < 0:
                        s = "lost"
                    else:
                        s = "gained"
                    out += f", started with {startlp} LP, {s} {lpgain}LP in total today"
                except:
                    pass

            await ctx.send(out)
        except ApiError as err:
            await err_msg(err, ctx)
            return

    @commands.command()
    async def lastgame(self, ctx: commands.Context):
        my_region, match_region, summonername = getChannelSummoner(ctx.channel.name)

        try:
            summoner = watcher.summoner.by_name(my_region, summonername)
            current_timestamp = datetime.datetime.now().timestamp() * 1000
            matches = watcher.match.matchlist_by_puuid(match_region, summoner['puuid'])
            lastgame = watcher.match.by_id(match_region, matches[0])
            gameEndTimeStamp = lastgame["info"]["gameEndTimestamp"]
            type = getGameType(lastgame)

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
            await err_msg(err, ctx)

    @routines.routine(minutes=5)
    async def update_matches_loop(self):

        # Get summoner, ranked stats and match history
        summoner = watcher.summoner.by_name("kr", "Leminem")
        ranked_stats = watcher.league.by_summoner("kr", summoner['id'])
        matches = getMatchesOfToday("asia", summoner)

        date = getDate()
        savedMatches = getMatches()
        lp = getLP(ranked_stats)

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

        saveMatches(savedMatches)


async def err_msg(err, ctx):
    if err.response.status_code == 404:
        await ctx.send(f"@{ctx.author.name} Summoner is currently not ingame")
    elif err.response.status_code == 429:
        await ctx.send(f'@{ctx.author.name} Connection error')
    elif err.response.status_code == 404:
        await ctx.send(f'@{ctx.author.name} We couldnt find this summoner')
    else:
        raise


def saveMatches(matches):
    with open("./json/matches.json", "w") as f:
        json.dump(matches, f, indent=4)


def getMatches():
    with open("./json/matches.json", "r") as f:
        return json.load(f)


def getLP(ranked_stats):
    # Get the LP of SOLO_DUO
    i = 0
    for queuetype in ranked_stats:
        if ranked_stats[i]['queueType'] == 'RANKED_SOLO_5x5':
            return ranked_stats[i]['leaguePoints']
        i = i + 1


def getDailyLPGain():
    date = getDate()
    matches = getMatches()
    summoner = watcher.summoner.by_name("kr", "Leminem")
    ranked_stats = watcher.league.by_summoner("kr", summoner['id'])
    current_lp = getLP(ranked_stats)
    lp = current_lp - matches[date]["startlp"]
    return matches[date]["startlp"], lp


def getGameType(match):
    queueId = match["info"]["queueId"]
    if queueId == 1020:
        return "One for all"
    if queueId == 700:
        return "Clash"
    if queueId == 450:
        return "Aram"
    if queueId == 440:
        return "Ranked Flex"
    if queueId == 420:
        return "Ranked Solo/Duo"
    if queueId == 400:
        return "Normal"
    if queueId == 0:
        return "Custom"


def getChannelSummoner(name):
    if name == "deceiver_euw":
        my_region = "euw1"
        match_region = "europe"
        summonername = "Deceiv3dDeceiv3r"
    elif name == "thedisconnect":
        my_region = "euw1"
        match_region = "europe"
        summonername = "TheDisconnect"
    elif name == "rango235":
        my_region = "euw1"
        match_region = "europe"
        summonername = "I love Fullclear"
    else:
        my_region = "kr"
        match_region = "asia"
        summonername = "Leminem"
    return my_region, match_region, summonername


def getDate():
    return datetime.datetime.now().strftime("%d-%m-%Y")


def getMatchesOfToday(match_region, me):
    date = datetime.datetime.now().strftime("%d/%m/%Y")
    todayzeroam = time.mktime(datetime.datetime.strptime(f"{date}/00/00",
                                                         "%d/%m/%Y/%H/%M").timetuple())  # Get the timestamp of start of the day
    matches = watcher.match.matchlist_by_puuid(match_region, me['puuid'], type="ranked",
                                               start_time=int(todayzeroam))
    return matches


bot = Bot()
bot.run()
