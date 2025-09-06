import spotipy
from spotipy import SpotifyOAuth
import asyncio

from twitchAPI.eventsub.websocket import EventSubWebsocket
from twitchAPI.helper import first
from twitchAPI.eventsub.base import Twitch, EventSubBase
from twitchAPI.oauth import UserAuthenticationStorageHelper
from twitchAPI.object.eventsub import ChannelPointsCustomRewardRedemptionAddEvent
from twitchAPI.type import AuthScope

from CustomCacheHandler import CustomCacheHandler
from config import client_secret, client_id, APP_ID, EVENTSUB_URL, APP_SECRET

import logging
logging.basicConfig(filename="log.txt", level=logging.DEBUG)

TARGET_USERNAME = 'lol_nemesis'

async def on_follow(data: dict):
    print("follow")





async def on_redemption(data: ChannelPointsCustomRewardRedemptionAddEvent):
    # our event happend, lets do things with the data we got!
    print(data.event.user_input)
    # {'subscription': {'id': '416a2c42-0b83-41f7-a1d4-29c1525f80c1', 'status': 'enabled', 'type': 'channel.channel_points_custom_reward_redemption.add',
    # 'version': '1', 'condition': {'broadcaster_user_id': '86131599', 'reward_id': ''},
    # 'transport': {'method': 'webhook', 'callback': 'https://194a-77-119-194-152.eu.ngrok.io/callback'},
    # 'created_at': '2022-12-10T16:03:53.399679943Z', 'cost': 0},
    # 'event': {'broadcaster_user_id': '86131599', 'broadcaster_user_login': 'lol_nemesis',
    # 'broadcaster_user_name': 'lol_nemesis', 'id': '9f4c9b0c-92ec-4e81-a5e0-c82cf74ae751', 'user_id': '29821947', 'user_login': 'saintshing',
    # 'user_name': 'saintshing', 'user_input': 'https://open.spotify.com/track/3IBSro9H1RYkMWpLsx7XYN', 'status': 'unfulfilled',
    # 'redeemed_at': '2022-12-10T16:04:27.733458706Z', 'reward': {'id': 'b74d3b2e-dbc0-4e84-a3de-0d6333fafa09', 'title': 'Song Request',
    # 'prompt': 'Only spotify links. ', 'cost': 15000}}}
    link = data.event.user_input
    original_link = link
    print("REDEEM SONG")
    print(link)
    uri = ""
    if link.startswith("https://open.spotify.com/track/"):
        link = link.split("https://open.spotify.com/track/")[-1]
        link = link.split("?")[0]
        uri = "spotify:track:" + link
    elif link.startswith("https://open.spotify.com/album/") and "?highlight=spotify:track:" in link:
        link = link.split("highlight=")[1]
        link = link.split("?")[0]
        uri = link

    else:
        print("ERROR: WRONG URI " + link)
        logging.debug("WRONG URI " + link)
        return

    scope = ["playlist-modify-private", "playlist-modify-public"]
    playlist_id = "2FfICVgwwXBuqbsKaoFbK5"

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(cache_handler=CustomCacheHandler(), scope=scope, client_id=client_id,
                                                   client_secret=client_secret,
                                                   redirect_uri="http://127.0.0.1:9090"))

    results = sp.playlist_add_items(playlist_id, [uri])
    logging.debug("ADDED SONG " + original_link)

async def user_refresh(token, refresh_token):
    print("here")
    print(token)
    print(refresh_token)


async def eventsub_example():
    # create the api instance and get the ID of the target user
    twitch = await Twitch(APP_ID, APP_SECRET)
    twitch.user_auth_refresh_callback = user_refresh
    user = await first(twitch.get_users(logins=TARGET_USERNAME))

    await twitch.refresh_used_token()
    # basic setup, will run on port 8080 and a reverse proxy takes care of the https and certificate
    event_sub = EventSubBase(EVENTSUB_URL, APP_ID, 8080, twitch)

    target_scope = [AuthScope.CHANNEL_READ_REDEMPTIONS]
    # auth = UserAuthenticator(twitch, target_scope, force_verify=False)
    # this will open your default browser and prompt you with the twitch verification website
    # token, refresh_token = await auth.authenticate()
    #await twitch.set_user_authentication(token, target_scope, refresh_token)

    # unsubscribe from all old events that might still be there
    # this will ensure we have a clean slate
    await event_sub.unsubscribe_all()
    # start the eventsub client
    event_sub.start()
    # subscribing to the desired eventsub hook for our user
    # the given function will be called every time this event is triggered
    #await event_sub.listen_channel_follow(user.id, on_follow)
    await event_sub.listen_channel_points_custom_reward_redemption_add(user.id, on_redemption, reward_id="b74d3b2e-dbc0-4e84-a3de-0d6333fafa09")

    # eventsub will run in its own process
    # so lets just wait for user input before shutting it all down again
    try:
        input('press Enter to shut down...')
    finally:
        # stopping both eventsub as well as gracefully closing the connection to the API
        await event_sub.stop()
        await twitch.close()
    print('done')


TARGET_SCOPES = [AuthScope.CHANNEL_READ_REDEMPTIONS]
async def run():
    # create the api instance and get user auth either from storage or website
    twitch = await Twitch(APP_ID, APP_SECRET)
    await twitch.refresh_used_token()
    #await twitch.set_user_authentication("token", TARGET_SCOPES, "refresh_token")
    helper = UserAuthenticationStorageHelper(twitch, TARGET_SCOPES)
    await helper.bind()
    # get the currently logged in user
    user = await first(twitch.get_users())

    # create eventsub websocket instance and start the client.
    eventsub = EventSubWebsocket(twitch)
    eventsub.start()
    # subscribing to the desired eventsub hook for our user
    # the given function (in this example on_follow) will be called every time this event is triggered
    # the broadcaster is a moderator in their own channel by default so specifying both as the same works in this example
    # We have to subscribe to the first topic within 10 seconds of eventsub.start() to not be disconnected.
    await eventsub.listen_channel_points_custom_reward_redemption_add(user.id, on_redemption, reward_id="b74d3b2e-dbc0-4e84-a3de-0d6333fafa09")

    # eventsub will run in its own process
    # so lets just wait for user input before shutting it all down again
    try:
        input('press Enter to shut down...')
    except KeyboardInterrupt:
        pass
    finally:
        # stopping both eventsub as well as gracefully closing the connection to the API
        await eventsub.stop()
        await twitch.close()


asyncio.run(run())
#asyncio.run(eventsub_example())
