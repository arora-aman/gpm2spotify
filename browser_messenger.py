import asyncio
import datetime
import json
import logging
import queue
import threading
import websockets

class BrowserMessenger():
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._log_queue = queue.Queue()


    def _run_loop(self):
        """Runs the event loop for the websocket
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        self._server = websockets.serve(self._log_message, self._host, self._port)

        loop.run_until_complete(self._server)
        loop.run_forever()


    def run_in_background(self):
        """Runs the messenger in background
        """
        threading.Thread(target=self._run_loop).start()


    def _get_time(self):
        """
        :returns: String, Local time
        """
        curr_time = datetime.datetime.now()
        return curr_time.strftime("%Y-%m-%d %H:%M:%S")


    def song_found(self, searched_song, result, exact):
        """Log successful song find query to the browser
        :param searched_song: Song object, The song that was searched
        :param result: JSON Object, The JSON response with the song information
        :param exact: Boolean, If the result has matching title, album AND artist
        """
        message = {
            "timestamp": self._get_time(),
            "level": "INFO",
            "type": "SONG_FOUND",
            "searched_song": json.dumps(searched_song.to_dict()),
            "result": json.dumps(result),
            "exact": exact,
        }

        self._log_queue.put(json.dumps(message))


    def song_not_found(self, song):
        """Log unsuccessful song search
        :param song: Song object, The song that was searched
        """
        message = {
            "timestamp": self._get_time(),
            "level": "ERROR",
            "type": "SONG_NOT_FOUND",
            "song": json.dumps(song.to_dict()),
        }

        self._log_queue.put(json.dumps(message))


    def songs_added(self, destination, song_count):
        """Log successful song additions to user's spotify account
        :param destination: String, Library or Playlist the songs were added to
        :param song_count: Integer, Number of songs that were added
        """
        message = {
            "timestamp": self._get_time(),
            "level": "INFO",
            "type": "SONGS_ADDED",
            "dest": destination,
            "song_count": song_count,
        }

        self._log_queue.put(json.dumps(message))


    def songs_add_failed(self, destination, song_count):
        """Log unsuccessful song additions to user's spotify account
        :param destination: String, Library or Playlist the songs were being added to
        :param song_count: Integer, Number of songs that were being added
        """
        message = {
            "timestamp": self._get_time(),
            "level": "ERROR",
            "type": "SONGS_ADD_FAILED",
            "dest": destination,
            "song_count":  song_count,
        }

        self._log_queue.put(json.dumps(message))


    def playlist_created(self, playlist):
        """Log successful creation of a playlist
        :param name: JSON Object, Complete info about the playlist
        """
        message = {
            "timestamp": self._get_time(),
            "level": "INFO",
            "type": "PLAYLIST_CREATED",
            "playlist": json.dumps(playlist),
        }

        self._log_queue.put(json.dumps(message))


    def playlist_create_failed(self, name):
        """Log unsuccessful attempt at creating  a playlist
        :param name: Name of the playlist
        """
        message = {
            "timestamp": self._get_time(),
            "level": "ERROR",
            "type": "PLAYLIST_CREATE_FAILED",
            "name": name,
        }

        self._log_queue.put(json.dumps(message))


    async def _log_message(self, socket, request_uri):
        while True:
            record = self._log_queue.get()
            await socket.send(record)

