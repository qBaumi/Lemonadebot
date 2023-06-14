import twitchio
from twitchio.ext import commands

import dbutils
from config import cooldown
import utils, json

class Mods(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @commands.command()
    async def whitelist(self, ctx: commands.Context, action: str = None, user: twitchio.User = None):
        if not ctx.author.is_mod and ctx.author.name.lower() != "qbaumi":
            return
        whitelist = utils.getWhitelist()
        if action == "" or action is None:

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
            dbutils.sql_exec(f"INSERT INTO whitelist VALUES({user.id});")
            await ctx.send(f"{user.display_name} was successfully added to the whitelist")
        elif action == "remove" and user is not None:
            if user.id not in whitelist:
                await ctx.send("User was never whitelisted in the first place!")
                return
            dbutils.sql_exec(f"DELETE FROM whitelist WHERE id = {user.id};")

            await ctx.send(f"{user.display_name} was successfully removed from the whitelist")
        else:
            await ctx.send(f"examples: 'whitelist'(sends all whitelisted users), 'whitelist add @user', 'whitelist removed @user'")
            return

    @commands.command()
    async def addcommand(self, ctx: commands.Context, command: str, *, response: str):
        if not ctx.author.is_mod and ctx.author.name.lower() != "qbaumi":
            return
        print(f"command: {command}")
        print(f"response: {response}")
        textcommands = utils.getTextCommands()
        textcommands[command] = response
    @commands.command()
    async def removecommand(self, ctx: commands.Context, command: str):
        if not ctx.author.is_mod and ctx.author.name.lower() != "qbaumi":
            return
        print(f"command: {command}")
        textcommands = utils.getTextCommands()
        textcommands.remove(command)

    @commands.cooldown(rate=1, per=cooldown, bucket=commands.Bucket.user)
    @commands.command()
    async def change_account(self, ctx: commands.Context, *, new_account_name):
        print(new_account_name)
        print(ctx.author.id)

        if not utils.isWhitelisted(ctx):
            return
        with open("./json/accounts.json", "w") as f:
            json.dump({"currentAccount": new_account_name}, f, indent=4)
        await ctx.send(f"{ctx.author.mention} successfully changed Account to {new_account_name}")

def prepare(bot: commands.Bot):
    bot.add_cog(Mods(bot))
