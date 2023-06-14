import requests
from twitchio.ext import commands
from config import cooldown


class Other(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot



    @commands.cooldown(rate=1, per=cooldown, bucket=commands.Bucket.user)
    @commands.command()
    async def valorank(self, ctx: commands.Context):
        r = requests.get(url="https://api.henrikdev.xyz/valorant/v2/mmr/eu/NemesisLol/LOL")
        data = r.json()
        elo = str(data["data"]["current_data"]["elo"])
        await ctx.send(f'@{ctx.author.name} {data["data"]["current_data"]["currenttierpatched"]} with {str(elo)[len(elo)-2:len(elo)]} RR/LP')



def prepare(bot: commands.Bot):
    bot.add_cog(Other(bot))
