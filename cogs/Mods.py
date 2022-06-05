from twitchio.ext import commands
from config import cooldown
import utils, json

class Mods(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @commands.cooldown(rate=1, per=cooldown, bucket=commands.Bucket.user)
    @commands.command()
    async def changeAccount(self, ctx: commands.Context, *, newAccountName):
        print(newAccountName)

        if not ctx.author.is_mod and str(ctx.author.name) != "qbaumi2004":
            print("return")
            return
        with open("./json/account.json", "w") as f:
            json.dump({"name" : newAccountName}, f, indent=4)
        await ctx.send(f"{ctx.author.mention} successfully changed Account to {newAccountName}")

def prepare(bot: commands.Bot):
    bot.add_cog(Mods(bot))
