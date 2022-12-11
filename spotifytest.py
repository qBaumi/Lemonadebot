import spotipy
from spotipy.oauth2 import SpotifyOAuth

from CustomCacheHandler import CustomCacheHandler
from config import client_id, client_secret

scope = ["playlist-modify-private", "playlist-modify-public"]

playlist_id = "2FfICVgwwXBuqbsKaoFbK5"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(cache_handler=CustomCacheHandler(), scope=scope, client_id=client_id,
                                                           client_secret=client_secret,
                                               redirect_uri="http://127.0.0.1:9090"))

playlists = sp.current_user_playlists()
print(playlists)

results = sp.playlist_add_items(playlist_id, ["spotify:track:52LJ3hyknOijCrE5gCD0rE"])



