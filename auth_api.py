import access_token

from flask import Blueprint, current_app, jsonify, redirect, request, url_for


auth_api = Blueprint("auth", __name__, url_prefix="")

spotify_client = None
spotify_user = None

@auth_api.route("/on_auth", methods=["GET"])
def on_authenticated():
    """Endpoint to receive spotify authentication redirect
    """
    args = request.args.to_dict()
    success = spotify_user.on_auth_request_return(
            args["code"] if "code" in args else None,
            args["error"] if "error" in args else None,
        )

    on_success = """
    <html>
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
    
    return on_success if success else on_failure


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
    
    spotify_client= access_token.SpotifyClient(request.form["client_id"], request.form["client_secret"])

    spotify_user = access_token.SpotifyUser(spotify_client, "http://localhost:8000")
    spotify_user.get_access_token()

    return"""
    <html>
        <body>
            Contacting Spotify for your info!
        </body>
    </html>
    """, 200
