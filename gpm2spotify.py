import gpm_file_parser
import json
import logging
import os
import queue
import song_finder
import spotify_song_adder
import threading


class Gpm2Spotify:
    def __init__(self,
            filepath="",
            spotify_app=None,
            spotify_user=None,
            thumbs_up_is_library=True,
            browser_messenger = None):
        self._filepath = "/Users/aman23091998/Downloads/Takeout/Google Play Music"
        self._song_finder = song_finder.SongFinder(spotify_app, browser_messenger)
        self._spotify_adder = spotify_song_adder.SpotifyAdder(spotify_user)
        self._thumbs_up_is_library = thumbs_up_is_library
        self._browser_messenger = browser_messenger

        self._parser_lock = threading.Lock()
        self._gpm_file_parser = gpm_file_parser.GpmFileParser()
        self._logger = logging.getLogger("gpm2spotify")


    def _add_songs_to_spotify_thread(self, read_queue, add_to_spotify):
        """Thread to batch add songs to spotify
        :param read_queue: Queue, Contians songs that need to be added to spotify
        :param add_to_spotify: Function(ids), Add upto 50 ids to spotify. Function handles
                               library or playlist.
        """
        song_ids = []

        while True:
            if len(song_ids) == 50:
                add_to_spotify(song_ids)
                song_ids = []

            song = read_queue.get()

            if not song:
                break

            id = self._song_finder.get_song_id(song)

            if id:
                song_ids.append(id)

        add_to_spotify(song_ids)


    def _parse_song_files(self, tracks_filepath, add_to_spotify):
        """Reads songs from Google Takeout and adds them to spotify
        :param tracks_filepath: Path to songs that need to be added
        :param add_to_spotify: Function(ids), Add upto 50 ids to spotify. Function handles
                               library or playlist.
        """
        files = os.listdir(tracks_filepath)

        read_queue = queue.Queue() # Files read from tracks_filepath

        thread_count = 10

        threads = []

        for x in range(thread_count):
            threads.append(
                    threading.Thread(target=self._add_songs_to_spotify_thread, args=(read_queue, add_to_spotify))
                )

        for x in range(thread_count):
            threads[x].start()

        for file in files:
             read_queue.put(
                     self._gpm_file_parser.parse_file(os.path.join(tracks_filepath, file))
                    )

        for x in range(thread_count):
            read_queue.put(None)

        for x in range(thread_count):
            threads[x].join()


    def _post_library(self, song_ids_list):
        """Adds songs to Spotify Library
        :param song_ids_list: Array of ids, (Max 50) ids of songs that need to be added to the library
        """

        song_count = len(song_ids_list)

        if song_count == 0:
            return

        if song_count > 50:
            self._logger.info(f"ID list should be less than 50, found:{song_count}, handling gracefully...")

        while song_count > 0:
            selected = 50 if song_count >= 50 else song_count

            if  self._spotify_adder.add_to_library(song_ids_list[song_count - selected: song_count -1]):
                self._logger.info(f"Added {selected} songs to library")
                self._browser_messenger.songs_added("Library", selected)
            else:
                self._logger.error(f"Failed to add {song_count} to library")
                self._browser_messenger.songs_add_failed("Library", selected)

            song_count -= selected

    def parse_library(self):
        """Adds songs from GPM to spotify library
        """
        if self._thumbs_up_is_library:
            tracks_filepath = self._filepath + "/Playlists/Thumbs Up/"

        self._parser_lock.acquire()
        self._parse_song_files(tracks_filepath, self._post_library)
        self._parser_lock.release()

    def _post_playlist(self, id, song_ids):
        """Adds songs to a Spotify Playlist
        :param id: String, Spotify ID of the Playlist
        :param song_ids_list: Array of ids, (Max 50) ids of songs that need to be added to the library
        """
        # post upto 50 songs
        return

    def _parse_playlist(self, name, playlist_file_path):
        # Create Playlist

        tracks_filepath = playlist_file_path + ("/Tracks" if name is not "Thumbs Up" else "")
        print(name, tracks_filepath)

    def parse_playlists(self):
        """Adds playlists from GPM to Spotify
        """
        playlists_filepath = self._filepath + "/Playlists"

        self._parser_lock.acquire()

        playlists = os.listdir(playlists_filepath)

        if self._thumbs_up_is_library and "Thumbs Up" in playlists:
            playlists.remove("Thumbs Up")

        for playlist in playlists:
            self._parse_playlist(playlist, playlists_filepath + f"/{playlist}")

        self._parser_lock.release()
