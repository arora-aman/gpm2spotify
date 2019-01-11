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
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        self._server = websockets.serve(self._log_message, self._host, self._port)

        loop.run_until_complete(self._server)
        loop.run_forever()


    def run_in_background(self):
        threading.Thread(target=self._run_loop).start()


    def _get_time(self):
        curr_time = datetime.datetime.now()
        return curr_time.strftime("%Y-%m-%d %H:%M:%S")


    def song_found(self, song, exact, uri):
        message = {
            "timestamp": self._get_time(),
            "level": "INFO",
            "type": "SONG_FOUND",
            "song": str(song),
            "exact": exact,
            "uri": uri,
        }

        self._log_queue.put(json.dumps(message))


    def song_not_found(self, song):
        message = {
            "timestamp": self._get_time(),
            "level": "ERROR",
            "type": "SONG_NOT_FOUND",
            "song": str(song),
        }

        self._log_queue.put(json.dumps(message))


    def songs_added(self, destination, song_count):
        message = {
            "timestamp": self._get_time(),
            "level": "INFO",
            "type": "SONGS_ADDED",
            "dest": destination,
            "song_count": song_count,
        }

        self._log_queue.put(json.dumps(message))


    def songs_add_failed(self, destination, song_count):
        message = {
            "timestamp": self._get_time(),
            "level": "ERROR",
            "type": "SONGS_ADD_FAILED",
            "dest": destination,
            "song_count":  song_count,
        }

        self._log_queue.put(json.dumps(message))


    async def _log_message(self, socket, request_uri):
        while True:
            record = self._log_queue.get()
            await socket.send(record)

