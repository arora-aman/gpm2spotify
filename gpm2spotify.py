import gpm_file_parser
import json
import logging
import os
import queue
import song_finder
import spotify_song_adder
import threading


class Gpm2Spotify:
    def __init__(self, filepath="", spotify_app=None, spotify_user=None):
        print("Parser created")
        self._filepath = "/Users/aman23091998/Downloads/Takeout/Google Play Music"
        self._song_finder = song_finder.SongFinder(spotify_app)
        self._spotify_adder = spotify_song_adder.SpotifyAdder(spotify_user)
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

        if len(song_ids_list) > 50:
            self._logger.error(f"ID list should be less than 50, found:{len(song_ids_list)}, handling gracefully...")
            return

        if  self._spotify_adder.add_to_library(song_ids_list):
            self._logger.info(f"Added {len(song_ids_list)} songs to library")
        else:
            self._logger.error(f"Failed to add {len(song_ids_list)} to library")


    def parse_library(self):
        """Adds songs from GPM to spotify library
        """
        tracks_filepath = self._filepath + "/Playlists/Thumbs Up/"

        self._parser_lock.acquire()
        self._parse_song_files(tracks_filepath, self._post_library)
        self._parser_lock.release()

