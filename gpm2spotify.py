import asyncio
import gpm_file_parser
import json
import logging
import os
import queue
import song_finder
import threading

class Gpm2Spotify:
    def __init__(self, filepath="", authorization_header=""):
        self._filepath = "/Users/aman23091998/Downloads/Takeout/Google Play Music"
        self._song_finder = song_finder.SongFinder(authorization_header)
        self._parser_lock = asyncio.Lock()
        self._gpm_file_parser = gpm_file_parser.GpmFileParser()


    def _add_songs_to_spotify_thread(self, read_queue, callback):
        song_ids = []

        while len(song_ids) < 50:
            song = read_queue.get()

            if not song:
                break

            id = self._song_finder.get_song_id(song)

            if id:
                song_ids.append(id)
                print(f"{song.title} found at https://open.spotify.com/track/{id}")

        callback(song_ids)

    async def _parse_song_files(self, tracks_filepath, callback):
        files = os.listdir(tracks_filepath)

        read_queue = queue.Queue() # Files read from tracks_filepath
        thread_count = max(10, (len(files) / 50))

        loop = asyncio.get_event_loop()
        futures = [
                loop.run_in_executor(
                    None,
                    self._add_songs_to_spotify_thread,
                    read_queue,
                    callback
                    )

                #for x in range(thread_count)
                ]

        for file in files:
             read_queue.put(
                     self._gpm_file_parser.parse_file(os.path.join(tracks_filepath, file))
                     )

        for x in range(thread_count):
            read_queue.put(None)

        for response in await asyncio.gather(*futures):
            pass

    def _post_library(self, song_ids_list):
        if len(song_ids_list) > 50:
            logging.error(f"ID list should be less than 50, found:{len(song_ids_list)}, handling gracefully...")
        return

        print(f"Found {len(song_ids_list)} id")

    async def _parse_library(self):
        tracks_filepath = self._filepath + "/Playlists/Thumbs Up/"

        async with self._parser_lock:
            await self._parse_song_files(tracks_filepath, self._post_library)

    def parse_songs():
        return None

