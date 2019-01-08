import json
import logging
import requests


class SongFinder:
    def __init__(self, authorization_header):
        self._auth_header = authorization_header
        self._songs = dict()


    def _search_song(self, query_track, query_album="", query_artist=""):
        """Runs a specific track, albim and artist query
        :param query_track: String, Title of the song to be searched for
        :param query_album: String, Formatted as "album:{specific album}"
        :param query_artist: String, Formatted as "artist:{specific artist}"

        :returns: dict, Response to the query

        """
        spotify_get_song_info_endpoint = "https://api.spotify.com/v1/search"
        query = f"{query_track} {query_album} {query_artist}&type=track&limit=1"

        try:
            resp = requests.get(spotify_get_song_info_endpoint + "?q=" + query, headers=self._auth_header)

            if not resp.ok:
                logging.debug(
                        f"Query={query} failed"
                        f" errcode={resp.status_code}"
                        f" errmsg={resp.content}"
                    )
                return

            output = json.loads(resp.content.decode())
            songs = output["tracks"]["items"]

            if len(songs) > 0:
                return songs[0]

            logging.debug(f"Song not found for query={query}")
        except Exception as e:
            logging.exception(f"query={query} failed")


    def _get_song(self, query_song):
        """Searches for a specific song on spotify
        :param query_song: Song, Song to be searched for

        :returns: JSON Object, The song with the closest match

        """
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
            return song

        song =  self._search_song(query_track, query_album=query_album)

        if song:
            self._songs[query_song] = {
                    "song": song,
                    "exact": False,
            }
            return song

        song =  self._search_song(query_track, query_artist=query_artist)

        if song:
            self._songs[query_song] = {
                    "song": song,
                    "exact": False,
            }
            return song

        self._songs[query_song] = {
                "song": None,
                "exact": False,
        }

        logging.error(f"Couldn't find {query_song} on Spotify")

    def get_song_id(self, song):
        """Searches for a specific song on spotify
        :param song: Song, Song to be searched for

        :returns: JSON Object, The ID of the song with the closest match

        """
        result = self._get_song(song)

        if result:
            return result["id"]
