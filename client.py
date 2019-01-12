import base64
import json
import logging
import requests
import time
import webbrowser


class SpotifyClient:
    def __init__(self, client_id, client_secret):
        self._client_id = client_id
        self._client_secret = client_secret
        self._logger = logging.getLogger("gpm2spotify")

    @property
    def client_id(self):
        return self._client_id

    def authorization_header(self):
        """Header required to make unscoped requests
        :returns: Dictionary, containing authorization information
        """
        client_credentials = f"{self._client_id}:{self._client_secret}"
        encoded_client_credentials = base64.standard_b64encode(bytearray(client_credentials, 'utf-8')).decode("utf-8")
        headers = {
            "Authorization": f"Basic {encoded_client_credentials}",
        }

        return headers

    def make_request(self, method, endpoint, headers=None, data=None, json_data=None):
        """Helper to abstract making HTTP request and error handling
        :param method: String, "GET" or "PUT" or "POST" or "PATCH"
        :param endpoint: String, endpoint to make the request
        :param headers: Dictionary, headers passed with the request
        :param data: Dictionary, data to be appeneded to the request
        :returns: Dictoniary, response; None if non 2XX status or if making request failed
        :note: Use `response is not None` to check for success in case on empty response
        """
        method_to_function = {
            "GET": requests.get,
            "PUT": requests.put,
            "POST": requests.post,
            "PATCH": requests.patch,
        }

        try:
            resp = method_to_function[method](endpoint, headers=headers, data=data, json=json_data)

            if not resp.ok:
                if resp.status_code == 429:
                    time.sleep(int(resp.headers["Retry-After"]))
                    return self.make_request(method, endpoint, headers, data, json_data)

                self._logger.error(
                    f"{method} {endpoint} Failed"
                    f" data={data}"
                    f" errcode={resp.status_code}"
                    f" errmsg={resp.content}"
                )
                return None

            content = resp.content.decode()
            if not content:
                return dict()
            else:
                return json.loads(content)

        except Exception:
            self._logger.exception(f"{method} {endpoint} Failed data={data}")


class SpotifyUser:
    def __init__(self, spotify_client, flask_server):
        self._client = spotify_client
        self._flask_server = flask_server

        self._access_token = ""
        self._logger = logging.getLogger("gpm2spotify")


    def make_request(self, method, endpoint, data=None, json=None):
        """Makes a request with user authorisation
        :param method: String, "GET" or "PUT" or "POST" or "PATCH"
        :param endpoint: String, endpoint to make the request
        :param data: Dictionary, data to me appeneded to the request
        """
        if not self._access_token:
            raise RuntimeError("User access token not found")

        headers = {
            "Authorization": f"Bearer {self._access_token}"
        }

        return self._client.make_request(method, endpoint, headers, data, json)

    def get_access_token_url(self):
        """Returns the endpoint used to Get a new access token from spotify for accessing user data
        """
        scopes = "playlist-modify-private playlist-modify-public user-library-modify"

        auth_endpoint = "https://accounts.spotify.com/authorize"
        query = f"client_id={self._client.client_id}&response_type=code&redirect_uri={self._flask_server}/on_auth&scope={scopes}"

        return f"{auth_endpoint}?{query}"


    def on_auth_request_return(self, code=None, error=None):
        """Handles response from spotify authorization request
        :return: Bool, True if the user was comepletely authenicated
        """
        if not code:
            self._logger.error(f"User authorization request failed: {error}")
            return False

        self._auth_code = code
        success = self._get_access_token_from_auth_code()

        return success


    def _get_access_token_from_auth_code(self):
        """Gets access token for the authorized user
        :return: Bool, True if successful
        """
        spotify_access_token_endpoint = "https://accounts.spotify.com/api/token"

        data = {
            "grant_type": "authorization_code",
            "code": self._auth_code,
            "redirect_uri": f"{self._flask_server}/on_auth"
        }

        resp = self._client.make_request(
                "POST",
                spotify_access_token_endpoint,
                self._client.authorization_header(),
                data
            )

        if not resp:
            self._logger.error("Failed to retrive access token for the user")
            return False

        self._access_token = resp["access_token"]
        return True

class SpotifApplication:
    def __init__(self, spotify_client):
        self._client = spotify_client
        self._logger = logging.getLogger("gpm2spotify")


    def make_request(self, method, endpoint, data=None, json=None):
        """Makes a request to unscoped data
        :param method: String, "GET" or "PUT" or "POST" or "PATCH"
        :param endpoint: String, endpoint to make the request
        :param data: Dictionary, data to me appeneded to the request
        """
        if not self._access_token:
            raise RuntimeError("User access token not found")

        headers = {
            "Authorization": f"Bearer {self._access_token}"
        }

        return self._client.make_request(method, endpoint, headers, data, json)

    def get_access_token(self):
        """Gets a new access token from spotify for the unscoped data
        :returns: Bool, True if the access token is successfully retrieved
        """

        spotify_access_token_endpoint = "https://accounts.spotify.com/api/token"
        data = {
            "grant_type": "client_credentials",
        }

        resp = self._client.make_request("POST", spotify_access_token_endpoint, self._client.authorization_header(), data)

        if not resp:
            self._logger.error("Failed to get app access token")
            return False

        self._access_token = resp["access_token"]

        return True
