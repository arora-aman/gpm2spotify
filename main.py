import asyncio
import access_token
import auth_api
import gpm2spotify
import logging
import sys

from flask import Flask, request


app = Flask(
    __name__,
)

app.register_blueprint(auth_api.auth_api)

def config_logger():
    """Configures a logger for the app
    """
    formatter = logging.Formatter(
            fmt="[%(asctime)s] :: %(levelname)s :: %(module)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            )

    file_handler = logging.FileHandler("gpm2spotify.log")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    logger = logging.getLogger("gpm2spotify")
    logger.handlers = [file_handler,]
    logger.setLevel(logging.INFO)


def main():
    config_logger()

    app.run(host="localhost", port=8000, threaded=True)

    # token = access_token.get_access_token(sys.argv[1], sys.argv[2])

    # if not token:
    #     raise RuntimeError("Access Token Not Available")

    # auth_header = {
    #     "Authorization": f"Bearer {token}"
    # }
    # parser = gpm2spotify.Gpm2Spotify("", auth_header)

    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(parser.parse_library())


if __name__ == "__main__":
    main()
