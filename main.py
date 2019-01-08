import asyncio
import access_token
import gpm2spotify 
import logging

def config_logger():
    """Configures a logger for the app
    :returns: logging.Logger
    """
    logger = logging.getLogger("gpm2spotify")
    logger.setLevel(level=logging.DEBUG)

    return logger

def main():
    logger = config_logger() 
    
    token = access_token.get_access_token("", "")

    if not token:
        raise RuntimeError("Access Token Not Available")

    auth_header = {
        "Authorization": f"Bearer {token}"
    }
    parser = gpm2spotify.Gpm2Spotify("", auth_header, logger)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(parser.parse_library())

if __name__ == "__main__":
    main()
