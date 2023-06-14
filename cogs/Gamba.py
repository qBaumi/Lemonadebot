import twitchio
from twitchio.ext import commands

import dbutils
from config import cooldown, gamba_token
import utils, json


class Gamba(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.current_prediction = None
    """
        -- MOD COMMANDS
        whitelist
        whitelist add @user
        whitelist remove @user
        wrong whitelist arg | displays help for whitelist
        -- WHITELISTED COMMANDS
        gamba | displays help for gamba
        gamba start
        gamba start
        gamba end win/lose
    """

    @commands.command()
    async def gamba(self, ctx: commands.Context, action: str = "", outcome: str = ""):
        if not utils.isWhitelisted(ctx):
            return
        if action == "":
            # send help
            await ctx.send(f"examples: 'gamba start', 'gamba end win', 'gamba end lose'")
        elif action == "start":
            # start gamba
            user = await ctx.channel.user()
            if self.current_prediction is None:
                self.current_prediction = user.create_prediction(gamba_token, "WIN OR LOSE", "win", "lose", 120)
            else:
                await ctx.send("There is already a predction going on")
        elif action == "end" and outcome == "win" or action == "end" and outcome == "lose":
            # end gamba
            if self.current_prediction is not None:
                user = await ctx.channel.user()
                await user.end_prediction(gamba_token, self.current_prediction.id, "HmmSwing ", outcome)
                self.current_prediction = None
            else:
                await ctx.send("There is no predction going on")

        else:
            await ctx.send(f"examples: 'gamba start', 'gamba end win', 'gamba end lose'")




def prepare(bot: commands.Bot):
    bot.add_cog(Gamba(bot))
