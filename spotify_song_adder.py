import logging
import requests


class SpotifyAdder:
    def __init__(self, auth_header):
        self._auth_header = auth_header
        self._logger = logging.getLogger("gpm2spotify")


    def add_to_library(self, song_ids):
        """Add a list of song's to the users library
        :param song_ids: Array of Strings, (Max 50) List of song ids that are added to Spotify Library.
        """
        endpoint = "https://api.spotify.com/v1/me/tracks"
        #concatenated_ids = ",".join(song_ids)

        data = {
            "ids": song_ids 
        }

        try:
            resp = requests.put(endpoint,  headers=self._auth_header, data=data)
            
            if not resp.ok:
                self._logger.exception(
                        f"Failed to add songs to Spotify"
                        f" errcode={resp.status_code}"
                        f" errmsg={resp.content}"
                    )
                
                return False

            return True
        except Exception:
            self._logger.exception("Failed to make request to add songs")
