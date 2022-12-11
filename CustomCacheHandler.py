
import json

import spotipy


class CustomCacheHandler(spotipy.CacheHandler):
    """
    An abstraction layer for handling the caching and retrieval of
    authorization tokens.

    Custom extensions of this class must implement get_cached_token
    and save_token_to_cache methods with the same input and output
    structure as the CacheHandler class.
    """

    def get_cached_token(self):
        """
        Get and return a token_info dictionary object.
        """
        # return token_info
        with open("./json/token.json", "r") as f:
            token = json.load(f)
        print(token)

        return token
        #raise NotImplementedError()

    def save_token_to_cache(self, token_info):
        """
        Save a token_info dictionary object to the cache and return None.
        """

        with open("./json/token.json", "w") as f:
            json.dump(token_info, f, indent=4)
        print(token_info)

        #raise NotImplementedError()
        return None
