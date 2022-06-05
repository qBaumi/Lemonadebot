import datetime
import json
import time
from config import watcher



async def err_msg(err, ctx):
    if err.response.status_code == 404:
        await ctx.send(f"@{ctx.author.name} Summoner is currently not ingame")
    elif err.response.status_code == 429:
        await ctx.send(f'@{ctx.author.name} Connection error')
    elif err.response.status_code == 404:
        await ctx.send(f'@{ctx.author.name} We couldnt find this summoner')
    elif err.response.status_code == 503:
        await ctx.send(f'@{ctx.author.name} Riot API server down. Sadge')
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
    summoner = watcher.summoner.by_name("kr", getChannelSummoner("lol_nemesis")[2])
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
        with open("./json/account.json", "r") as f:
            data = json.load(f)
        summonername = data["name"]
    return my_region, match_region, summonername

def getNemesisAccountName():
    with open("./json/account.json", "r") as f:
        data = json.load(f)
    return data["name"]

def getDate():
    return datetime.datetime.now().strftime("%d-%m-%Y")


def getMatchesOfToday(match_region, me):
    date = datetime.datetime.now().strftime("%d/%m/%Y")
    todayzeroam = time.mktime(datetime.datetime.strptime(f"{date}/00/00",
                                                         "%d/%m/%Y/%H/%M").timetuple())  # Get the timestamp of start of the day
    matches = watcher.match.matchlist_by_puuid(match_region, me['puuid'], type="ranked",
                                               start_time=int(todayzeroam))
    return matches
