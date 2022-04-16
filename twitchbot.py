import math

from twitchio.ext import commands
from config import token, api_key
from riotwatcher import LolWatcher, ApiError
import datetime, time




class Bot(commands.Bot):

    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...
        super().__init__(token=token, prefix=['lem ', 'LEM' , 'LeM' , 'LEm' , 'Lem' , 'lEM' , 'leM' ], initial_channels=['lol_nemesis', 'qbaumi2004', 'deceiver_euw', 'thedisconnect'], nick="Lemon Bot", case_insensitive=True)
        self.counter = 0
    async def event_ready(self):
        # Notify us when everything is ready!
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')
        user = await self.fetch_users(["lol_nemesis"])
        print(user)

    async def event_message(self, message):
        # Messages with echo set to True are messages sent by the bot...
        # For now we just want to ignore them...
        if message.echo:
            return

        # Print the contents of our message to console...
        print(message.content)
        print(message.author.name)
        #if message.author.name == "azarusio" and self.counter < 3:
        #    await message.channel.send("I use Azarusio everyday and it changed my life!")
        #    self.counter+=1
        # Since we have commands and are overriding the default `event_message`
        # We must let the bot know we want to handle and invoke our commands...
        await self.handle_commands(message)

    @commands.command()
    async def icant(self, ctx: commands.Context):
        # Here we have a command hello, we can invoke our command with our prefix and command name
        # e.g ?hello
        # We can also give our commands aliases (different names) to invoke with.

        # Send a hello back!
        # Sending a reply back to the channel is easy... Below is an example.
        await ctx.send(f'ICANT')

    @commands.command()
    async def language(self, ctx: commands.Context):
        await ctx.send(f'Only english Habibi')

    @commands.command()
    async def help(self, ctx: commands.Context):
        await ctx.send(f'@{ctx.author.name} You tell me what I can do, I have barely any features yet Sadge')

    @commands.command()
    async def rank(self, ctx: commands.Context):

        watcher = LolWatcher(api_key)
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

    @commands.command(aliases=["winrate", "losses", "daily", "stats"])
    async def wins(self, ctx: commands.Context):
        watcher = LolWatcher(api_key)
        my_region, match_region, summonername = getChannelSummoner(ctx.channel.name)


        try:
            me = watcher.summoner.by_name(my_region, summonername)
            date = datetime.datetime.now().strftime("%d/%m/%Y")
            todayzeroam = time.mktime(datetime.datetime.strptime(f"{date}/00/00", "%d/%m/%Y/%H/%M").timetuple()) # Get the timestamp of start of the day
            matches = watcher.match.matchlist_by_puuid(match_region, me['puuid'], type="ranked",
                                                       start_time=int(todayzeroam))  #
            wins = 0
            losses = 0
            for matchid in matches:
                match = watcher.match.by_id(match_region, matchid)
                print(match)
                for participant in match["info"]["participants"]:
                    if participant["puuid"] == me["puuid"]:
                        print(participant["win"])
                        if participant["win"] == True:
                            wins += 1
                        else:
                            losses += 1
                        break

            print(f"wins/losses {wins}/{losses}")
            if losses == 0 and wins > 0:
                winrate = 1
                out = f"@{ctx.author.name} Todays wins/losses {wins}/{losses}, winrate: {int(winrate * 100)}%"
            elif losses == 0 and wins == 0:
                winrate = 0
                out = f"@{ctx.author.name} No ranked games played today :/"
            else:
                winrate =  wins / (wins+losses)
                out = f"@{ctx.author.name} Todays wins/losses {wins}/{losses}, winrate: {int(winrate * 100)}%"
            print(out)
            await ctx.send(out)
        except ApiError as err:
            if err.response.status_code == 429:
                await ctx.send(f'@{ctx.author.name} Connection error')
            elif err.response.status_code == 404:
                await ctx.send(f'@{ctx.author.name} We couldnt find this summoner')
            else:
                raise

    @commands.command()
    async def lastgame(self, ctx : commands.Context):
        watcher = LolWatcher(api_key)

        my_region, match_region, summonername = getChannelSummoner(ctx.channel.name)

        try:
            me = watcher.summoner.by_name(my_region, summonername)
            now = datetime.datetime.now().timestamp()*1000
            matches = watcher.match.matchlist_by_puuid(match_region, me['puuid'])
            lastgame = watcher.match.by_id(match_region, matches[0])
            gameEndTimeStamp = lastgame["info"]["gameEndTimestamp"]
            type = getGameType(lastgame)

            # Get win or loss
            for participant in lastgame["info"]["participants"]:
                if participant["puuid"] == me["puuid"]:
                    print(participant["win"])
                    if participant["win"] == True:
                        win = "won"
                    else:
                        win = "lost"
                    champ = participant["championName"]
                    kda = f'{participant["kills"]}/{participant["deaths"]}/{participant["assists"]}'
                    break

            # Get mins into hours + mins
            mins = int((now-gameEndTimeStamp)/60000)
            if mins > 60:
                hours = math.floor(mins/60)
                mins = mins/60-hours
                mins = int(mins*60)
                out = f"{hours} hours and {mins} minutes"
            else:
                out = f"{mins} minutes"

            await ctx.send(f"@{ctx.author.name} Last game ({type}, {champ}, {kda}) was played {out} ago and was {win}")
        except ApiError as err:
            if err.response.status_code == 429:
                await ctx.send(f'@{ctx.author.name} Connection error')
            elif err.response.status_code == 404:
                await ctx.send(f'@{ctx.author.name} We couldnt find this summoner')
            else:
                raise

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
        return "Practice Tool"

def getChannelSummoner(name):
    if name == "deceiver_euw":
        my_region = "euw1"
        match_region = "europe"
        summonername = "Deceiv3dDeceiv3r"
    elif name == "thedisconnect":
        my_region = "euw1"
        match_region = "europe"
        summonername = "TheDisconnect"
    else:
        my_region = "kr"
        match_region = "asia"
        summonername = "Leminem"
    return my_region, match_region, summonername

bot = Bot()
bot.run()
# bot.run() is blocking and will stop execution of any below code here until stopped or closed.