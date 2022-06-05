from twitchio.ext import commands
from config import cooldown
import utils, json

class Template(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @commands.cooldown(rate=1, per=cooldown, bucket=commands.Bucket.default)
    @commands.command()
    async def template(self, ctx: commands.Context):
        await ctx.send(f'test')


def prepare(bot: commands.Bot):
    bot.add_cog(Template(bot))
