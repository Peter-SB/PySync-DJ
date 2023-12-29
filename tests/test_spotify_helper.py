import unittest
from unittest.mock import patch
from spotify_helper import SpotifyHelper

class TestSpotifyHelperTrackLimit(unittest.TestCase):

    @patch('spotify_helper.SettingsSingleton')
    def setUp(self, MockSettings):
        # Set up mock settings with test credentials
        self.mock_settings = MockSettings.return_value
        self.mock_settings.spotify_client_id = "test_client_id"
        self.mock_settings.spotify_client_secret = "test_client_secret"

        # Initialize SpotifyHelper with the mocked settings
        self.spotify_helper = SpotifyHelper()


    def test_track_within_no_limits(self):
        self.mock_settings.liked_songs_date_limit = None
        self.mock_settings.liked_songs_track_limit = 10

        liked_songs = []
        track = {"added_at": "2020-01-01T00:00:00Z"}

        self.assertTrue(self.spotify_helper._is_track_within_date_and_track_limit(liked_songs, track))

    def test_track_within_date_limit(self):
        self.mock_settings.liked_songs_date_limit = "01-01-20"  # MM-DD-YY
        self.mock_settings.liked_songs_track_limit = 10

        liked_songs = []
        track_within_limit = {"added_at": "2020-01-02T00:00:00Z"}
        track_outside_limit = {"added_at": "2019-12-31T00:00:00Z"}

        self.assertTrue(self.spotify_helper._is_track_within_date_and_track_limit(liked_songs, track_within_limit))
        self.assertFalse(self.spotify_helper._is_track_within_date_and_track_limit(liked_songs, track_outside_limit))

    def test_track_within_track_limit(self):
        self.mock_settings.liked_songs_date_limit = None
        self.mock_settings.liked_songs_track_limit = 1

        liked_songs = []
        track = {"added_at": "2020-01-01T00:00:00Z"}

        self.assertTrue(self.spotify_helper._is_track_within_date_and_track_limit(liked_songs, track))

        liked_songs = [{"some_track_data": "data"}]  # One track already in the list

        self.assertFalse(self.spotify_helper._is_track_within_date_and_track_limit(liked_songs, track))

    def test_track_within_both_limits(self):
        self.mock_settings.liked_songs_date_limit = "01-01-20"
        self.mock_settings.liked_songs_track_limit = 2

        liked_songs = [{"some_track_data": "data"}]
        track_within_both_limits = {"added_at": "2020-01-02T00:00:00Z"}

        self.assertTrue(self.spotify_helper._is_track_within_date_and_track_limit(liked_songs, track_within_both_limits))

    def test_track_outside_both_limits(self):
        self.mock_settings.liked_songs_date_limit = "01-01-20"
        self.mock_settings.liked_songs_track_limit = 1

        liked_songs = [{"some_track_data": "data"}]
        track_outside_date_limit = {"added_at": "2019-12-31T00:00:00Z"}

        self.assertFalse(self.spotify_helper._is_track_within_date_and_track_limit(liked_songs, track_outside_date_limit))
