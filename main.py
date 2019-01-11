import auth_api
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

    app_logger = logging.getLogger("gpm2spotify")
    app_logger.handlers = [file_handler,]
    app_logger.setLevel(logging.INFO)

def main():
    config_logger()

    app.run(host="localhost", port=8000)


if __name__ == "__main__":
    main()
