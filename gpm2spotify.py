import asyncio
import gpm_file_parser
import json
import logging
import os
import queue
import requests
import threading

class Gpm2Spotify:
    def __init__(self, filepath="", authorization_header=""):
        self._filepath = "/Users/aman23091998/Downloads/Takeout/Google Play Music"
        self._auth_header = authorization_header
        self._songs = dict()
        self._parser_lock = asyncio.Lock()
        self._gpm_file_parser = gpm_file_parser.GpmFileParser()

    def _get_song_id(self, song):
        spotify_get_song_info_endpoint = "https://api.spotify.com/v1/search"
        query_track = f"{song.title}"
        query_album = f"album:{song.album}"
        query_artist = f"artist:{song.artist}"

        query = f"?q={query_track} {query_album} {query_artist}&type=track"
        try:
            resp = requests.get(spotify_get_song_info_endpoint + query, headers=self._auth_header)

            if not resp.ok:
                logging.error(f"Unable to find {song} on Spotify errcode={resp.status_code} errmsg={resp.content}")
                return

            output = json.loads(resp.content.decode())
            return output["tracks"]["items"][0]["id"]
        except Exception as e:
            logging.exception(f"Failed to retrieve {song}")
            return None


    def _add_songs_to_spotify_thread(self, read_queue, callback):
        song_ids = []
        
        while True:
            song = read_queue.get()
            if not song:
                break
           
            if song not in self._songs:
                id = self._get_song_id(song)
                self._songs[song] = id
            id = self._songs[song]
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

        print(f"Found {len(song_ids_list)} songs")

    async def _parse_library(self):
        tracks_filepath = self._filepath + "/Playlists/Thumbs Up/"
        
        async with self._parser_lock:
            await self._parse_song_files(tracks_filepath, self._post_library)

    def parse_songs():
        return None

