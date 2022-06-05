from twitchio.ext import commands
from config import cooldown


class Other(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @commands.cooldown(rate=1, per=cooldown, bucket=commands.Bucket.user)
    @commands.command()
    async def inem(self, ctx: commands.Context):
        await ctx.send(f'No.')

    @commands.cooldown(rate=1, per=cooldown, bucket=commands.Bucket.user)
    @commands.command()
    async def language(self, ctx: commands.Context):
        await ctx.send(f'Only english Habibi')

    @commands.cooldown(rate=1, per=cooldown, bucket=commands.Bucket.user)
    @commands.command(aliases=["dankHug", "nemeHug"])
    async def hug(self, ctx: commands.Context):
        await ctx.send(f'@{ctx.author.name} dankHug')

def prepare(bot: commands.Bot):
    bot.add_cog(Other(bot))
