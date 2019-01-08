import asyncio
import access_token
import gpm2spotify
import logging

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

    token = access_token.get_access_token("", "")

    if not token:
        raise RuntimeError("Access Token Not Available")

    auth_header = {
        "Authorization": f"Bearer {token}"
    }
    parser = gpm2spotify.Gpm2Spotify("", auth_header)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(parser.parse_library())

if __name__ == "__main__":
    main()
