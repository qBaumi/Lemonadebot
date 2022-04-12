from twitchio.ext import commands
from config import token, api_key
from riotwatcher import LolWatcher, ApiError

class Bot(commands.Bot):

    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...
        super().__init__(token=token, prefix='lem ', initial_channels=['lol_nemesis', 'qbaumi2004'], nick="Lemon Bot", case_insensitive=True)

    async def event_ready(self):
        # Notify us when everything is ready!
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    async def event_message(self, message):
        # Messages with echo set to True are messages sent by the bot...
        # For now we just want to ignore them...
        if message.echo:
            return

        # Print the contents of our message to console...
        print(message.content)
        print(message.author.name)
        if message.author.name == "azarusio":
            await message.channel.send("I use Azarusio everyday and it changed my life!")
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
    async def rank(self, ctx: commands.Context):
        # Here we have a command hello, we can invoke our command with our prefix and command name
        # e.g ?hello
        # We can also give our commands aliases (different names) to invoke with.

        # Send a hello back!
        # Sending a reply back to the channel is easy... Below is an example.
        watcher = LolWatcher(api_key)
        my_region = "kr"
        summonername = "Leminem"

        try:
            me = watcher.summoner.by_name(my_region, summonername)
            my_ranked_stats = watcher.league.by_summoner(my_region, me['id'])

            i = 0

            for queuetype in my_ranked_stats:

                if my_ranked_stats[i]['queueType'] == 'RANKED_SOLO_5x5':
                    rank = my_ranked_stats[i]['tier'].lower()
                    rank = rank.capitalize()
                    out = f"{rank} {my_ranked_stats[i]['leaguePoints']}lp {my_ranked_stats[i]['wins']} wins {my_ranked_stats[i]['losses']} losses"


                i = i + 1
            await ctx.send(out)
        except ApiError as err:
            if err.response.status_code == 429:
                await ctx.send('Connection error')
            elif err.response.status_code == 404:
                await ctx.send('We couldnt find this summoner')
            else:
                raise


bot = Bot()
bot.run()
# bot.run() is blocking and will stop execution of any below code here until stopped or closed.