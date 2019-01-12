import logging
import requests


class SpotifyAdder:
    def __init__(self, spotify_user):
        self._spotify_user = spotify_user
        self._logger = logging.getLogger("gpm2spotify")


    def add_to_library(self, song_ids):
        """Add a list of song's to the users library
        :param song_ids: Array of Strings, (Max 50) List of song ids that are added to Spotify Library.
        """
        endpoint = "https://api.spotify.com/v1/me/tracks"

        return self._spotify_user.make_request("PUT", endpoint, json=song_ids) is not None

    def create_playlist(self, name, public=False):
        """Creates a new playlist
        :param name: String, Name of the playlist
        :return: JSON Object, created playlist object
        """

        user_id = None # get user id
        endpoint = f"https://api.spotify.com/v1/users/{user_id}/playlists"

        json = {
            "name": name,
            "public": public
        }

        return self._spotify_user.make_request("POST", endpoint, json=json)
