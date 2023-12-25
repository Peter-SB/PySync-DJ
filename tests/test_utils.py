import unittest

from pysync_dj.utils import extract_spotify_playlist_id


class TestExtractSpotifyPlaylistID(unittest.TestCase):

    def test_valid_url(self):
        url = "https://open.spotify.com/playlist/7suQlwliFponAvWaKjyBxC"
        self.assertEqual("7suQlwliFponAvWaKjyBxC", extract_spotify_playlist_id(url))

    def test_valid_url_example2(self):
        url = "https://open.spotify.com/playlist/1mjGp0ddtuC5DDx0lWtCNQ"
        self.assertEqual("1mjGp0ddtuC5DDx0lWtCNQ", extract_spotify_playlist_id(url))

    def test_valid_id(self):
        url = "7suQlwliFponAvWaKjyBxC"
        self.assertEqual("7suQlwliFponAvWaKjyBxC", extract_spotify_playlist_id(url))

    def test_invalid_url(self):
        """Will still pass because function should work on partial url"""
        url = "https://notspotifyurl.com/playlist/7suQlwliFponAvWaKjyBxC"
        self.assertEqual("7suQlwliFponAvWaKjyBxC", extract_spotify_playlist_id(url))

    def test_invalid_url2(self):
        url = "https://notspotifyurl.com/playlist2/7suQlwliFponAvWaKjyBxC"
        self.assertEqual("7suQlwliFponAvWaKjyBxC", extract_spotify_playlist_id(url))

    def test_url_without_playlist_id(self):
        url = "https://open.spotify.com/playlist/"
        self.assertIsNone(extract_spotify_playlist_id(url))

    def test_non_url_string(self):
        url = "random string"
        self.assertIsNone(extract_spotify_playlist_id(url))

    def test_empty_string(self):
        url = ""
        self.assertIsNone(extract_spotify_playlist_id(url))

    def test_url_with_additional_path(self):
        url = "https://open.spotify.com/playlist/7suQlwliFponAvWaKjyBxC/otherpath"
        self.assertEqual("7suQlwliFponAvWaKjyBxC", extract_spotify_playlist_id(url))

