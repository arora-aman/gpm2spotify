import json
import logging
import requests
import urllib.parse


class SongFinder:
    def __init__(self, spotify_application, browser_messenger = None):
        self._spotify_app = spotify_application
        self._songs = dict()
        self._logger = logging.getLogger("gpm2spotify")
        self._browser_messenger = browser_messenger

    def _search_song(self, query_track, query_album="", query_artist=""):
        """Runs a specific track, albim and artist query
        :param query_track: String, Title of the song to be searched for
        :param query_album: String, Formatted as "album:{specific album}"
        :param query_artist: String, Formatted as "artist:{specific artist}"

        :returns: dict, Response to the query

        """
        spotify_get_song_info_endpoint = "https://api.spotify.com/v1/search"
        query = f"{query_track} {query_album} {query_artist}"

        encoded_query = urllib.parse.quote(query)

        resp = self._spotify_app.make_request(
                "GET",
                spotify_get_song_info_endpoint + "?q=" + encoded_query + "&type=track&limit=1",
            )

        if not resp:
            return

        songs = resp["tracks"]["items"]

        if len(songs) > 0:
            return songs[0]

        self._logger.debug(f"Song not found for query={query}")

    def _add_song_to_dict(self, query_song, song, exact=True):
        """Memoize same song search result
        :param query_song: Song, song object searched
        :param song: JSON Object, object returned after the query
        :param exact: Bool, true if title, album and artist of the query and result match

        :return: JSON Object, returns the query result back
        """

        self._songs[query_song] = {
                "song": song,
                "exact": exact,
        }

        if song:
            self._logger.debug(f"""{query_song} found at {song["external_urls"]["spotify"]}""")
            self._browser_messenger.song_found(str(query_song), exact, song["external_urls"]["spotify"])

        return song


    def _get_song(self, query_song):
        """Searches for a specific song on spotify
        :param query_song: Song, Song to be searched for

        :returns: JSON Object, The song with the closest match

        """
        if query_song in self._songs:
            return self._songs[query_song]["song"]

        query_track = f"\"{query_song.title}\""
        query_album = f"album:\"{query_song.album}\""
        query_artist = f"artist:\"{query_song.artist}\""

        song = self._search_song(query_track, query_album, query_artist)

        if song:
            return self._add_song_to_dict(query_song, song)

        song =  self._search_song(query_track, query_album=query_album)

        if song:
            return self._add_song_to_dict(query_song, song, False)

        song =  self._search_song(query_track, query_artist=query_artist)

        if song:
            return self._add_song_to_dict(query_song, song, False)

        self._add_song_to_dict(query_song, None, False)

        self._logger.error(f"Couldn't find {query_song} on Spotify")
        self._browser_messenger.song_not_found(query_song)


    def get_song_id(self, song):
        """Searches for a specific song on spotify
        :param song: Song, Song to be searched for

        :returns: JSON Object, The ID of the song with the closest match

        """
        result = self._get_song(song)

        if result:
            return result["id"]
