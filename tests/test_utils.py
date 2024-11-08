import json
import unittest
from unittest.mock import patch, mock_open

from utils import extract_spotify_playlist_id, load_hashmap_from_json


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


class TestLoadHashmapFromJson(unittest.TestCase):
    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data='{"key": "value"}')
    def test_load_existing_file(self, mock_file, mock_exists):
        """Test loading an existing JSON file with content."""
        mock_exists.return_value = True  # Simulate the file exists
        result = load_hashmap_from_json("/fake/drive", "test.json")
        self.assertEqual(result, {"key": "value"})  # Verify the dictionary is loaded correctly
        mock_file.assert_called_once_with("/fake/drive\\test.json", 'r')

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_create_missing_file(self, mock_file, mock_exists):
        """Test creating a missing JSON file."""
        mock_exists.return_value = False  # Simulate the file does not exist
        mock_file.return_value = mock_open().return_value

        result = load_hashmap_from_json("/fake/drive", "test.json")
        self.assertEqual(result, {})  # Verify an empty dictionary is returned

        # Check if the file was opened in write mode and written to
        mock_file.assert_called_once_with("/fake/drive\\test.json", 'w')
        mock_file().write.assert_called_once_with(json.dumps({}))

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data="{}")
    def test_load_empty_file(self, mock_file, mock_exists):
        """Test loading an existing file with an empty dictionary."""
        mock_exists.return_value = True  # Simulate the file exists
        result = load_hashmap_from_json("/fake/drive", "test.json")
        self.assertEqual(result, {})  # Verify the empty dictionary is loaded
        mock_file.assert_called_once_with("/fake/drive\\test.json", 'r')