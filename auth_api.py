import client
import gpm2spotify
import threading

from browser_messenger import BrowserMessenger
from flask import Blueprint, current_app, jsonify, redirect, request, url_for


BROWSER_MESSENGER_HOST = "127.0.0.1"
BROWSER_MESSENGER_PORT = 8001

auth_api = Blueprint("auth", __name__, url_prefix="")

spotify_client = None
spotify_user = None
spotify_app = None

browser_messenger = BrowserMessenger(
        BROWSER_MESSENGER_HOST,
        BROWSER_MESSENGER_PORT,
    )

browser_messenger.run_in_background()

def start_parser():
    global spotify_user
    global spotify_app


    parser = gpm2spotify.Gpm2Spotify("", spotify_app, spotify_user, True, browser_messenger)
    parser.parse_playlists()

@auth_api.route("/on_auth", methods=["GET"])
def on_authenticated():
    """Endpoint to receive spotify authentication redirect
    """
    on_success = f"""
    <html>
        <script>
            const socket = new WebSocket('ws://{BROWSER_MESSENGER_HOST}:{BROWSER_MESSENGER_PORT}');

            // Listen for messages
            socket.addEventListener('message', function (event) {{
                console.log(JSON.parse(event.data));
            }});
        </script>

        <body>
            Doing work now!
        </body>
    </html>
    """, 200

    on_failure = f"""
        <html>
            <body>
                An error occured!
                <a href={url_for("auth.login_show")}> Click here to retry</a>
            </body>

    """, 403

    args = request.args.to_dict()
    success = spotify_user.on_auth_request_return(
            args["code"] if "code" in args else None,
            args["error"] if "error" in args else None,
        )

    if not success:
        return on_failure

    success = spotify_user.get_user_id()

    if success:
        parser_thread = threading.Thread(target=start_parser)
        parser_thread.start()

    return on_success


@auth_api.route("/login", methods=["GET"])
def login_show():
    """Show user the login page
    """
    return """
    <html>
        <body>
            <form method="post">
                <input type="text" name="client_id" placeholder="Client id" required /> <br />
                <input type="text" name="client_secret" placeholder="Client secret" required /> <br />
                <button type="submit">
                    Submit
                </button>
            </form>
        </body>
    </html>
    """, 200

@auth_api.route("/login", methods=["POST"])
def login_create():
    """Attempts to authorize the user
    """
    global spotify_client
    global spotify_user
    global spotify_app

    spotify_client = client.SpotifyClient(request.form["client_id"], request.form["client_secret"])

    spotify_app = client.SpotifApplication(spotify_client)
    valid_client_creds = spotify_app.get_access_token()

    if not valid_client_creds:
        return f"""
        <html>
            <body>
                An error occured, make sure that the credentials are correct <br />
                <a href={url_for("auth.login_show")}> Click here to retry</a>
            </body>
        </html>
        """, 401

    spotify_user = client.SpotifyUser(spotify_client, "http://localhost:8000")
    return redirect(spotify_user.get_access_token_url(), code=302)
