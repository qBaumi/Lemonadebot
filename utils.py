import datetime
import json
import time

import requests

import dbutils
from config import watcher, riotwatcher


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

def getAccounts():
    with open("./json/accounts.json", "r") as f:
        data = json.load(f)
    return data["accounts"]

def update_matches():
    # Get summoner, ranked stats and match history
    accounts = getAccounts()
    for account in accounts:
        puuid = riotwatcher.account.by_riot_id("europe", account.split("#")[0], account.split("#")[1])["puuid"]
        summoner = watcher.summoner.by_puuid("euw1", puuid)
        ranked_stats = watcher.league.by_summoner("euw1", summoner['id'])
        matches = getMatchesOfToday("europe", summoner)
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
    else:
        my_region = "euw1"
        match_region = "europe"
        summonername = getCurrentAccountName()
    return my_region, match_region, summonername


def getCurrentAccountName():
    with open("./json/accounts.json", "r") as f:
        data = json.load(f)
    return data["currentAccount"]


def getDate():
    return datetime.datetime.now().strftime("%d-%m-%Y")


def getMatchesOfToday(match_region, me):
    date = datetime.datetime.now().strftime("%d/%m/%Y")
    todayzeroam = time.mktime(datetime.datetime.strptime(f"{date}/00/00",
                                                         "%d/%m/%Y/%H/%M").timetuple())  # Get the timestamp of start of the day
    matches = watcher.match.matchlist_by_puuid(match_region, me['puuid'], type="ranked",
                                               start_time=int(todayzeroam))
    return matches

def getWintradesOfToday(match_region, me, summonername):
    matches = getMatchesOfToday(match_region, me)
    failed_wintrade = 0
    succesfull_wintrade = 0

    for matchid in matches:
        match = watcher.match.by_id(match_region, matchid)
        for participant in match["info"]["participants"]:
            if participant["summonerName"] == summonername:
                kda = ((participant["kills"]+participant["assists"])/max(participant["deaths"], 1))
                if participant["win"] and kda < 2:
                    failed_wintrade += 1
                elif not participant["win"] and kda < 2:
                    succesfull_wintrade += 1
                break

    return failed_wintrade, succesfull_wintrade

def isWhitelisted(ctx):
    whitelist = getWhitelist()
    if int(ctx.author.id) in whitelist or ctx.author.name.lower() == "qbaumi" or ctx.author.is_mod:
        return True
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
    try:
        seventv = requests.get("https://7tv.io/v2/users/612b5f7cfef79a90b279bda7/emotes")
        seventvglobal = requests.get("https://api.7tv.app/v2/emotes/global")
    except:
        pass
    for emote in bttv.json()["channelEmotes"]:
        emotes.append(emote["code"])
    for emote in bttvglobal.json():
        emotes.append(emote["code"])
    for emote in bttv.json()["sharedEmotes"]:
        emotes.append(emote["code"])
    for emote in ffz.json()["sets"]["575523"]["emoticons"]:
        emotes.append(emote["name"])
    try:
        for emote in seventv.json():
            emotes.append(emote["name"])
        for emote in seventvglobal.json():
            emotes.append(emote["name"])
    except:
        pass
    return emotes

def getTopRank(region, summonerName):
    response = watcher.league.challenger_by_queue(region, "RANKED_SOLO_5x5")
    playerlist = response["entries"]
    playerlist = sorted(playerlist, key=lambda d: d["leaguePoints"], reverse=True)
    for i, player in enumerate(playerlist):
        if player["summonerName"] == summonerName:
            return i+1

async def useTextCommand(command, message):
    print(command)
    textcommands = getTextCommands()
    for textcommand in textcommands.keys():
        if command.lower().startswith(textcommand.lower()) or command.lower() == textcommand.lower():
            command = textcommand
            await message.channel.send(str(textcommands[command]).replace("@user", message.author.mention))


def getWhitelist():
    whitelist = []
    tuplelist = dbutils.sql_select("SELECT * FROM whitelist")
    for item in tuplelist:
        whitelist.append(item[0])
    return whitelist

def getTextCommands():
    with open("./json/textcommands.json", "r") as f:
        data = json.load(f)
    return data
def saveTextCommands(textcommands):
    with open("./json/textcommands.json", "w") as f:
        json.dump(textcommands, f, indent=4)