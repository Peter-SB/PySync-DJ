import logging
import os
import re
from typing import Optional

import pytube.helpers
import unicodedata
from pytube import Search, YouTube
from pytube.exceptions import VideoUnavailable

from utils import LOGGER_NAME


class YouTubeDownloadHelper:
    """
    Helper class for searching and downloading audio from YouTube videos.

    Provides functionality to search for a YouTube video based on a given search string,
    and download the highest quality audio stream available for that video.
    """

    def __init__(self, root_dir: str, tracks_folder: str) -> None:
        """
        Initialize the YouTubeDownloadHelper.

        :param root_dir: The root directory where tracks will be stored.
        :param tracks_folder: The specific folder within root_dir for storing tracks.
        """
        self.logger = logging.getLogger(LOGGER_NAME)
        self.track_dir = os.path.join(root_dir, tracks_folder)

    @staticmethod
    def _safe_filename(s: str, max_length: int = 255) -> str:
        """Sanitize a string making it safe to use as a filename.

        This function keeps ASCII and non-ASCII alphanumeric characters,
        and removes characters that are not allowed in filenames according
        to NTFS and general filesystem conventions.

        :param s:A string to make safe for use as a file name.
        :param max_length: The maximum filename character length.
        :returns: A sanitized string.
        """
        # Characters in range 0-31 (0x00-0x1F) are not allowed in ntfs filenames.
        # Additionally, certain symbols are not allowed in filenames.
        # We use a regex pattern that keeps ASCII and non-ASCII alphanumeric characters,
        # and replaces other characters.

        pattern = r'[^\w\-_\. ]'  # This keeps letters, digits, underscore, hyphen, dot, and space.
        regex = re.compile(pattern, re.UNICODE)
        filename = regex.sub("", s)

        # Truncate to max_length and remove trailing spaces
        return filename[:max_length].rstrip()

    @staticmethod
    def _remove_diacritics(s: str) -> str:
        """
        Remove diacritics from a string and replace them with their ASCII equivalents.

        :param s: The input string with diacritics.
        :return: A string with diacritics replaced by ASCII characters.
        """
        # Normalize the string to decompose the diacritic characters
        normalized = unicodedata.normalize('NFKD', s)

        # Filter out non-ASCII characters
        return ''.join(c for c in normalized if unicodedata.category(c) != 'Mn' and ord(c) < 128)


    def search_video(self, search_query: str) -> Optional[YouTube]:
        """
        Search YouTube with the given query and return the first video result.

        :param search_query: The query string to search on YouTube.
        :return: The first YouTube video object found or None if no results.
        """
        search = Search(search_query)
        if search_results := search.results:
            self.logger.debug(f"Search results for {search_query}: {search_results[0]}")
            return search_results[0]
        else:
            self.logger.warning(f"No search results for {search_query}")
            return None

    def search_video_url(self, search_url: str) -> Optional[YouTube]:
        """
        Search YouTube for the video corresponding to the given URL.

        :param search_url: The URL string of the YouTube video.
        :return: The YouTube video object if found, otherwise None.
        """
        try:
            video = YouTube(search_url)
            self.logger.debug(f"Found video from URL: {video.title}")
            return video
        except VideoUnavailable:
            self.logger.warning(f"Video unavailable for URL: {search_url}")
            return None

    def download_audio(self, video: YouTube) -> str:
        """
        Download the highest quality audio stream of the given YouTube video.

        :param video: The YouTube video object from which to download audio.
        :return: The file path of the downloaded audio, if available.
        """
        # Override this function to avoid Streams doing a file size check which will here always be different from raw
        # file, I assume due to metadata (image including) on audio files.
        def override_exists_at_path(file_path: str) -> bool:
            return os.path.isfile(file_path)

        audio_stream = video.streams.get_audio_only()
        if audio_stream:
            audio_stream.exists_at_path = override_exists_at_path
            file_name = self._remove_diacritics(audio_stream.default_filename)
            file_name = self._safe_filename(file_name)
            return audio_stream.download(filename=file_name, output_path=self.track_dir)
        else:
            self.logger.warning(f"No audio stream available for this video {video}")


