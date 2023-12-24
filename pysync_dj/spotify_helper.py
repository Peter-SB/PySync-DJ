import json
import logging

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from typing import List, Dict

import config
from utils import LOGGER_NAME


class SpotifyHelper:
    """
    A helper class for interacting with the Spotify API.
    """

    def __init__(self, client_id: str, client_secret: str) -> None:
        """
        Initializes the SpotifyHelper with Spotify API credentials.

        :param client_id: Spotify Client ID
        :param client_secret: Spotify Client Secret
        """
        self.logger = logging.getLogger(LOGGER_NAME)

        self.client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)

        self.sp = spotipy.Spotify(client_credentials_manager=self.client_credentials_manager)

    def get_playlist_tracks(self, playlist_id: str) -> List[Dict]:
        """
        Retrieves tracks from a given Spotify playlist.

        :param playlist_id: Spotify playlist ID
        :return: List of tracks in the playlist
        """
        results = self.sp.playlist_items(playlist_id)
        tracks = results['items']
        while results['next']:
            results = self.sp.next(results)
            tracks.extend(results['items'])
        return tracks

    def get_liked_tracks(self, limit: int) -> List[Dict]:
        """
        Retrieves tracks from the users liked list.

        :param limit: the number of tracks to return
        :return: List of tracks in the playlist
        """

        auth_manager = SpotifyOAuth(
            client_id=config.spotify_client_id,
            client_secret=config.spotify_client_secret,
            redirect_uri=config.spotify_redirect_uri,
            scope="user-library-read"
        )

        # Create a Spotipy client with the auth manager
        sp = spotipy.Spotify(auth_manager=auth_manager)

        # Fetch liked songs
        results = sp.current_user_saved_tracks()
        liked_songs = []

        while results:
            if len(liked_songs) >= limit:
                break
            liked_songs.extend(results['items'])
            if results['next']:
                results = sp.next(results)
            else:
                break

        return liked_songs[:limit]

