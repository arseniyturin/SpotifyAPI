try:
    import requests
except ImportError:
    print('> use pip install requests')

import base64
from time import time

try:
    import pandas as pd
except ImportError:
    print('> use pip install pandas')

class SpotifyAPI:

    """
        SpotifyAPI - simple class for working with Spotify API functions.

        Requires having 'client_id' and 'client_secret' for authorization.
        You can obtain both when you register your app here:
        https://developer.spotify.com/dashboard/applications

        If authorization went successful, client receives an 'access_token'.
        The token is used in each API call. Expires in 1 hour.
        No need to manually renew the token, class takes care of it.

        Supports following API calls:
            .genres() - obtain all genres in Spotify
            .search() - search for artist / song / album ... etc

        """

    def __init__(self, client_id: str = None, client_secret: str = None) -> str:
        """Authentification"""

        if type(client_id) != str and type(client_secret) != str:
            raise TypeError('Both client_id and client_secret must be strings')

        self.urls = {
            "api": "https://api.spotify.com/v1/",
            "auth": "https://accounts.spotify.com/api/token",
        }


        # client id and client secret are given by Spotify when App is registered
        self.client_id  = client_id
        self.client_secret = client_secret
        credentials = f"{self.client_id}:{self.client_secret}"
        # credentials must be encoded to base64 and included to the request header
        credentials_b64 = base64.b64encode(credentials.encode()).decode()


        # attempt to get token
        response = requests.post(
            url = self.urls['auth'],
            data = {"grant_type": "client_credentials"},
            headers = {"Authorization": f"Basic {credentials_b64}"}
        )
        # response comes in json format
        response = response.json()
        # if authorization is success we get access token
        if 'access_token' in response:
            self.start = time()
            access_token = response['access_token']
            self.api_headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": "Bearer " + access_token
            }
            print('ACCESS GRANTED.\nToken expires in 1 hour')
        # otherwise we throw an error
        else:
            print(f'ERROR: {response["error"]}')
            self.access_token = 0

    def __repr__(self) -> str:

        return ''

    def __str__(self) -> str:
        """Shows brief information about class"""
        elapsed = round(time()-self.start)
        if elapsed > 60:
            seconds = elapsed % 60
            minutes = elapsed // 60
            elapsed = f"{minutes} minutes {seconds} seconds"
        else:
            elapsed = f"{elapsed} seconds"

        print(f"""
            Class: {self.__class__.__name__}\n
            Time Elapsed: {elapsed}
            Available methods:
                .genres() -  method obtain all genres in Spotify
                .search() - search for artist
        """)
        return ''

    # Access Token is given for 1 hour. We can get new one the same way we received first one
    def update_token(self) -> None:
        """If token expired -> renew"""
        elapsed = (time() - self.start) / 3600
        if elapsed > 1:
            self.__init__(self.client_id, self.client_secret)

    # get genres
    @property
    def genres(self) -> dict:
        """
        Genres method
        -------------
        .genres() - takes no parameters, return all Spotify genres
        """
        self.update_token()

        url = self.urls['api'] + 'recommendations/available-genre-seeds'
        r = requests.get(url=url, headers=self.api_headers)
        return r.json()

    # search
    def search(self, q: str = 'post malone', t: str = 'artist') -> dict:
        """
        Search method\n
        Parameters:
            - q (query): ex. Post Malone
            - t (type): ex. album, artist, playlist, track, show and episode
                could be combined like: artist, track
        """
        params = {'q': q, 'type': t}
        url = self.urls['api'] + 'search'
        r = requests.get(url, params=params, headers=self.api_headers)
        return r.json()
