import datetime
import json
import time

import requests

import dbutils
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


def getLP(ranked_stats):
    # Get the LP of SOLO_DUO
    i = 0
    for queuetype in ranked_stats:
        if ranked_stats[i]['queueType'] == 'RANKED_SOLO_5x5':
            return ranked_stats[i]['leaguePoints']
        i = i + 1


def update_matches():
    # Get summoner, ranked stats and match history
    account = getNemesisAccountName()
    summoner = watcher.summoner.by_name("kr", account)
    ranked_stats = watcher.league.by_summoner("kr", summoner['id'])
    matches = getMatchesOfToday("asia", summoner)
    lp = getLP(ranked_stats)
    if matches:
        dbutils.savematch(matches[0], lp, account)


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
        summonername = getNemesisAccountName()
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


def isWhitelisted(ctx):
    with open("./json/whitelist.json", "r") as f:
        whitelist = json.load(f)

    if int(ctx.author.id) in whitelist or ctx.author.name == "qbaumi2004":
        print("Whitelisted")
        return True
    print("Not Whitelisted")
    return False


def getAllEmotes():
    # ENDPOINTS
    # https://api.frankerfacez.com/v1/room/lol_nemesis
    # https://7tv.io/v2/users/612b5f7cfef79a90b279bda7/emotes
    # https://api.betterttv.net/3/cached/users/twitch/86131599
    # https://api.betterttv.net/3/cached/emotes/global
    # https://api.7tv.app/v2/emotes/global

    emotes = []
    bttv = requests.get("https://api.betterttv.net/3/cached/users/twitch/86131599")
    bttvglobal = requests.get("https://api.betterttv.net/3/cached/emotes/global")
    ffz = requests.get("https://api.frankerfacez.com/v1/room/lol_nemesis")
    seventv = requests.get("https://7tv.io/v2/users/612b5f7cfef79a90b279bda7/emotes")
    seventvglobal = requests.get("https://api.7tv.app/v2/emotes/global")
    for emote in bttv.json()["channelEmotes"]:
        emotes.append(emote["code"])
    for emote in bttvglobal.json():
        emotes.append(emote["code"])
    for emote in bttv.json()["sharedEmotes"]:
        emotes.append(emote["code"])
    for emote in ffz.json()["sets"]["575523"]["emoticons"]:
        emotes.append(emote["name"])
    for emote in seventv.json():
        emotes.append(emote["name"])
    for emote in seventvglobal.json():
        emotes.append(emote["name"])
    return emotes
