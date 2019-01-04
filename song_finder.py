import json
import logging
import requests


class SongFinder:
    def __init__(self, authorization_header):
        self._auth_header = authorization_header
        self._songs = dict()


    def _search_song(self, query_track, query_album="", query_artist=""):
        spotify_get_song_info_endpoint = "https://api.spotify.com/v1/search"
        query = f"?q={query_track} {query_album} {query_artist}&type=track&limit=1"

        try:
            resp = requests.get(spotify_get_song_info_endpoint + query, headers=self._auth_header)

            if not resp.ok:
                logging.error(
                        f"Unable to find {song} on Spotify"
                        f" errcode={resp.status_code}"
                        f" errmsg={resp.content}"
                        f" query={query}"
                    )
                return

            output = json.loads(resp.content.decode())
            return output["tracks"]["items"][0]
        except Exception as e:
            logging.exception(f"query={query} failed")


    def get_song_id(self, query_song):
        if query_song in self._songs:
            return self._songs[query_song]["song"]

        query_track = f"{query_song.title}"
        query_album = f"album:{query_song.album}"
        query_artist = f"artist:{query_song.artist}"

        song = self._search_song(query_track, query_album, query_artist)

        if song:
            self._songs[query_song] = {
                    "song": song,
                    "exact": True,
            }
            return song["id"]

        song =  self._search_song(query_track, query_album=query_album)

        if song:
            self._songs[query_song] = {
                    "song": song,
                    "exact": False,
            }
            return song["id"]

        song =  self._search_song(query_track, query_artist=query_artist)

        if song:
            self._songs[query_song] = {
                    "song": song,
                    "exact": False,
            }
            return song["id"]

        self._songs[query_song] = {
                "song": None,
                "exact": False,
        }
        
        logging.error(f"Couldn't find {song} on Spotify")
