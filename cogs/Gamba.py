import twitchio
from twitchio.ext import commands
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
    async def whitelist(self, ctx: commands.Context, action: str = None, user: twitchio.User = None):
        if not ctx.author.is_mod and ctx.author.name.lower() != "qbaumi":
            return
        # load whitelist
        with open("./json/whitelist.json", "r") as f:
            whitelist = json.load(f)
        if action is None:
            # send whitelist
            print(whitelist)
            print(type(whitelist))
            users = await self.bot.fetch_users(ids=whitelist)
            s = f"whitelist: "
            for user in users:
                s += user.display_name + ", "
            await ctx.send(s)
            return
        elif action == "add" and user is not None:
            if user.id in whitelist:
                await ctx.send("User is already whitelisted!")
                return
            whitelist.append(user.id)
            await ctx.send(f"{user.display_name} was successfully added to the whitelist")
        elif action == "remove" and user is not None:
            if user.id not in whitelist:
                await ctx.send("User was never whitelisted in the first place!")
                return
            whitelist.remove(user.id)
            await ctx.send(f"{user.display_name} was successfully removed from the whitelist")
        else:
            await ctx.send(f"examples: 'whitelist'(sends all whitelisted users), 'whitelist add @user', 'whitelist removed @user'")
            return
        # save and close whitelist
        with open("./json/whitelist.json", "w") as f:
            json.dump(whitelist, f, indent=4)
        f.close()

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
