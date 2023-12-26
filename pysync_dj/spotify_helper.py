import json
import logging
from datetime import date, datetime

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from typing import List, Dict

from settings import SettingsSingleton
from utils import LOGGER_NAME


class SpotifyHelper:
    """
    A helper class for interacting with the Spotify API.
    """

    def __init__(self, client_id: str, client_secret: str) -> None:
        """
        Initializes the SpotifyHelper with Spotify API credentials.

        # todo: clean up this function, take out client_id and client secret

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

    def get_liked_tracks(self, liked_songs_track_limit: int, liked_songs_date_limit: date) -> List[Dict]:
        """
        Retrieves tracks from the users liked list.

        :param liked_songs_track_limit: the number of tracks to return
        :return: List of tracks in the playlist
        """
        settings = SettingsSingleton()

        auth_manager = SpotifyOAuth(
            client_id=settings.spotify_client_id,
            client_secret=settings.spotify_client_secret,
            redirect_uri=settings.spotify_redirect_uri,
            scope="user-library-read"
        )

        # Create a Spotipy client with the auth manager
        sp = spotipy.Spotify(auth_manager=auth_manager)

        # Fetch liked songs
        results = sp.current_user_saved_tracks()
        liked_songs = []

        while results:
            for track in results["items"]:
                if (settings.liked_songs_date_limit
                        and not self.track_added_inside_of_date_limit(track, settings.liked_songs_date_limit)):
                    return liked_songs[:liked_songs_track_limit]

                if liked_songs_track_limit and len(liked_songs) >= liked_songs_track_limit:
                    return liked_songs[:liked_songs_track_limit]

                liked_songs.append(track)

            if results['next']:
                results = sp.next(results)
            else:
                break

        return liked_songs[:liked_songs_track_limit]


    @staticmethod
    def track_added_inside_of_date_limit(track: dict, liked_songs_date_limit: str) -> bool:
        """
        Check if a track was added is within the user specified date limit.

        :param track: The track object to check.
        :param liked_songs_date_limit: The date limit as a string.
        :return: True if the song is within the limit, False otherwise.
        """
        if not liked_songs_date_limit:
            return True

        liked_songs_date_limit = datetime.strptime(liked_songs_date_limit, '%d-%m-%y').date()
        track_added_date = datetime.fromisoformat(track["added_at"].replace('Z', '+00:00')).date()

        if track_added_date >= liked_songs_date_limit:
            return True

        return False
