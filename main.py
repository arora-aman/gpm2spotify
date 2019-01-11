import auth_api
import browser_messenger
import logging

from flask import Flask


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

    browser_handler = browser_messenger.BrowserMessenger("127.0.0.1", 8002)
    browser_handler.setLevel(logging.DEBUG)

    logger = logging.getLogger("gpm2spotify")
    logger.handlers = [file_handler, browser_handler,]
    logger.setLevel(logging.DEBUG)

    browser_handler.run_in_background()

def main():
    config_logger()

    app.run(host="localhost", port=8000)


if __name__ == "__main__":
    main()
