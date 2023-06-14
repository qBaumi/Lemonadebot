from twitchio.ext import commands
import pylast
from config import lastfm_api_key, lastfm_api_secret, cooldown


class Song(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.cooldown(rate=1, per=cooldown, bucket=commands.Bucket.user)
    @commands.command()
    async def song(self, ctx: commands.Context):
        network = pylast.LastFMNetwork(
            api_key=lastfm_api_key,
            api_secret=lastfm_api_secret,
            # username=username,
            # password_hash=password_hash,
        )
        user = network.get_user("lolnemesis")
        print(user)
        try:
            current_track = user.get_now_playing()
        except:
            await ctx.send("The website with which the song gets tracked is currently dead.")
            return
        print(type(current_track))
        print(current_track)
        if current_track is None:
            out = f"@{ctx.author.name} No song currently playing or Streamer is playing local files"
        else:
            out = f"{current_track.title} - {current_track.artist}"
        await ctx.send(out)





def prepare(bot: commands.Bot):
    bot.add_cog(Song(bot))
