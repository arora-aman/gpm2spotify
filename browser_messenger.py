import asyncio
import logging
import queue
import threading
import websockets

class BrowserMessenger(logging.Handler):

    class Formatter(logging.Formatter):
        def __init__(self):
            logging.Formatter.__init__(
                    self,
                    fmt="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )


    def __init__(self, host, port):
        logging.Handler.__init__(self)
        self.setFormatter(BrowserMessenger.Formatter())

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


    def emit(self, record):
        self._log_queue.put(record)


    async def _log_message(self, socket, request_uri):
        while True:
            record = self._log_queue.get()
            await socket.send(self.format(record))

