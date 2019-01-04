import asyncio
import pprint
import access_token
import csv2json
import json
import logging
import os
import queue
import requests
import threading

class Song:
    def __init__(self, title, artist, album):
        self._title = title
        self._artist = artist
        self._album = album

    def __str__(self):
        return f"{self._title} - {self._album} by {self._artist}"


class GpmFileParser:
    def __init__(self, filepath="", authorization_header=""):
        self._filepath = "/Users/aman23091998/Downloads/Takeout/Google Play Music"
        self._auth_header = authorization_header
        self._songs = dict()
        self._parserLock = asyncio.Lock()

    def _get_song_id(self, song):
        spotify_get_song_info_endpoint = "https://api.spotify.com/v1/search"
        query_track = f"{song._title}"
        query_album = f"album:{song._album}"
        query_artist = f"artist:{song._artist}"

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


    def _add_songs_to_spotify_thread(self, readQueue, callback):
        song_ids = []
        
        while True:
            song = readQueue.get()
            if not song:
                break
           
            if song not in self._songs:
                id = self._get_song_id(song)
                self._songs[song] = id
            id = self._songs[song]
            if id:
                song_ids.append(id)
                print(f"{song._title} found at https://open.spotify.com/track/{id}")

        callback(song_ids)

    async def _parse_song_files(self, tracks_filepath, callback):
        files = os.listdir(tracks_filepath)

        readQueue = queue.Queue() # Files read from tracks_filepath
        thread_count = max(10, (len(files) / 50))

        loop = asyncio.get_event_loop()
        futures = [
                loop.run_in_executor(
                    None, 
                    self._add_songs_to_spotify_thread,
                    readQueue,
                    callback
                    )
                ]

        for file in files:
            try:
                song = csv2json.csv2json(os.path.join(tracks_filepath, file))
                song = json.loads(song)[0]
           
                readQueue.put(Song(song["Title"], song["Artist"], song["Album"]))
            except Exception as e:
                logging.exception(f"Can't parse {file}")
       
        for x in range(thread_count):
            readQueue.put(None)

        for response in await asyncio.gather(*futures):
            pass

    def _post_library(self, song_ids_list):
        if len(song_ids_list) > 50:
            logging.error(f"ID list should be less than 50, found:{len(song_ids_list)}, handling gracefully...")
        return

        print(f"Found {len(song_ids_list)} songs")

    async def _parse_library(self):
        tracks_filepath = self._filepath + "/Playlists/Thumbs Up/"
        
        async with self._parserLock:
            await self._parse_song_files(tracks_filepath, self._post_library)

    def parse_songs():
        return None

