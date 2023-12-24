import json
import unittest
from unittest.mock import patch, MagicMock
from pysync_dj.spotify_helper import SpotifyHelper


class TestSpotifyHelper(unittest.TestCase):
    """
    Unit tests for the SpotifyHelper class.
    """

    def setUp(self):
        """
        Set up test environment.
        """
        self.client_id = "test_client_id"
        self.client_secret = "test_client_secret"
        self.playlist_id = "test_playlist_id"
        self.spotify_helper = SpotifyHelper(self.client_id, self.client_secret)

