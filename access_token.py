import base64
import json
import logging
import requests


def get_access_token(client_id, client_secret):
    """Gets a new access token from spotify
    :param client_id: String, Spotify Application client id
    :param client_secret: String, Sptify Application client secret

    :returns: String, Spotify access token
    """
    auth_code = f"{client_id}:{client_secret}"
    encoded_auth_code = base64.standard_b64encode(bytearray(auth_code, 'utf-8')).decode("utf-8")
   
    headers = {
        "Authorization": f"Basic {encoded_auth_code}",
    }

    spotify_access_token_endpoint = "https://accounts.spotify.com/api/token"

    data = {
        "grant_type": "client_credentials",
    }

    try:
        resp = requests.post(spotify_access_token_endpoint, headers=headers, data=data)
        if not resp.ok:
            logging.error(resp.reason, resp.content, resp.status_code)
        return json.loads(resp.content.decode())["access_token"]
    except Exception:
        logging.exception("Failed to get access token")

