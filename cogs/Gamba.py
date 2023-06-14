import twitchio
from twitchio.ext import commands

import dbutils
from config import cooldown, gamba_token, token
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
        action = action.lower()
        outcome = outcome.lower()
        if not utils.isWhitelisted(ctx):
            return
        if action == "":
            # send help
            await ctx.send(f"examples: 'gamba start', 'gamba end win', 'gamba end lose'")
        elif action == "start":
            # start gamba
            user = await ctx.channel.user()
            if self.current_prediction is None:
                print("START GAMBA")
                self.current_prediction = await user.create_prediction(gamba_token, "WIN OR LOSE", "win", "lose", 120)
                print(self.current_prediction.prediction_id)
                print(self.current_prediction.outcomes)
                print(self.current_prediction)
            else:
                await ctx.send("There is already a prediction going on")
        elif action == "end" and outcome == "win" or action == "end" and outcome == "lose":
            # end gamba
            if self.current_prediction is not None:
                """[<PredictionOutcome outcome_id=ec65046d-68d0-4a1a-b2ce-f175b2ad16d9 title=win channel_points=0 color=BLUE>, 
                <PredictionOutcome outcome_id=c2f20e08-6ee0-4499-afc2-54c5e06ca76f title=lose channel_points=0 color=PINK>]
                <Prediction user=<PartialUser id=86131599, name=lol_nemesis> prediction_id=9a29696f-20fe-4597-90de-9ad688bfefcb winning_outcome_id=None title=WIN OR LOSE>"""
                user = await ctx.channel.user()
                for item in self.current_prediction.outcomes:
                    if item.title == "win":
                        win_outcome_id = item.outcome_id
                    else:
                        lose_outcome_id = item.outcome_id
                if outcome == "win":
                    outcome_id = win_outcome_id
                else:
                    outcome_id = lose_outcome_id
                print(f"outcome id = {outcome_id}")
                await user.end_prediction(gamba_token, self.current_prediction.prediction_id, "RESOLVED", outcome_id)
                self.current_prediction = None
            else:
                await ctx.send("There is no prediction going on")

        else:
            await ctx.send(f"examples: 'gamba start', 'gamba end win', 'gamba end lose'")




def prepare(bot: commands.Bot):
    bot.add_cog(Gamba(bot))
