from datetime import datetime

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from typing import List, Dict

from event_queue import EventQueueLogger
from settings import SettingsSingleton


class SpotifyHelper:
    """
    A helper class for interacting with the Spotify API.

    This class provides methods to interact with Spotify, such as retrieving playlist tracks
    and liked tracks, using the Spotipy library.
    """

    def __init__(self, event_logger: EventQueueLogger) -> None:
        """
        Initializes the SpotifyHelper with Spotify API credentials.
        """
        self.logger = event_logger
        self.settings = SettingsSingleton()
        self.client_credentials_manager = SpotifyClientCredentials(
            client_id=self.settings.spotify_client_id,
            client_secret=self.settings.spotify_client_secret
        )
        self.sp = spotipy.Spotify(client_credentials_manager=self.client_credentials_manager)

    def get_playlist_tracks(self, playlist_id: str) -> List[Dict]:
        """
        Retrieves tracks from a given Spotify playlist.

        :param playlist_id: Spotify playlist ID
        :return: A list of dictionaries, each representing a track in the playlist.
        """
        try:
            results = self.sp.playlist_items(playlist_id)
            tracks = results['items']
            while results['next']:
                results = self.sp.next(results)
                tracks.extend(results['items'])
            return tracks
        except Exception as e:
            self.logger.error(f"Error retrieving playlist tracks: {e}")
            return []

    def get_liked_tracks(self) -> List[Dict]:
        """
        Retrieves tracks from the users liked list.

        :return: A list of dictionaries, each representing a liked track.
        """
        auth_manager = SpotifyOAuth(
            client_id=self.settings.spotify_client_id,
            client_secret=self.settings.spotify_client_secret,
            redirect_uri=self.settings.spotify_redirect_uri,
            scope="user-library-read"
        )

        # Create a Spotipy client with the auth manager
        sp = spotipy.Spotify(auth_manager=auth_manager)

        # Fetch liked songs
        liked_songs = []
        try:
            results = sp.current_user_saved_tracks()
            while results:
                for track in results["items"]:
                    if self._is_track_within_date_and_track_limit(liked_songs, track):
                        liked_songs.append(track)
                    else:
                        return liked_songs[:self.settings.liked_songs_track_limit]

                results = sp.next(results) if results['next'] else None
            return liked_songs[:self.settings.liked_songs_track_limit]
        except Exception as e:
            self.logger.error(f"Error retrieving liked tracks: {e}")
            return []

    def _is_track_within_date_and_track_limit(self, liked_songs: List[Dict], track: Dict) -> bool:
        """
        Helper method to check if a track is within the user-specified date limit and track limit.

        :param liked_songs: The current list of liked songs.
        :param track: The track object to check.
        :return: True if the song is within the limit, False otherwise.
        """
        if self.settings.liked_songs_date_limit:
            liked_songs_date_limit = datetime.strptime(self.settings.liked_songs_date_limit, '%d-%m-%y').date()
            track_added_date = datetime.fromisoformat(track["added_at"].replace('Z', '+00:00')).date()
            if track_added_date < liked_songs_date_limit:
                return False

        if self.settings.liked_songs_track_limit:
            return len(liked_songs) < self.settings.liked_songs_track_limit

        return True
