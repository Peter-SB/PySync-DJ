import logging
import os
from typing import Optional
from pytube import Search, YouTube
from pytube.exceptions import VideoUnavailable

from utils import LOGGER_NAME


class YouTubeDownloadHelper:
    """
    A helper class to search and download audio from YouTube videos.

    This class provides functionality to search for a YouTube video
    based on a given search string, select the first result from the search,
    and download the highest quality audio stream available for that video.
    """

    def __init__(self, root_dir: str, tracks_folder: str):
        """
        Initializes the YouTubeDownloader class.
        """
        self.logger = logging.getLogger(LOGGER_NAME)
        self.track_dir = os.path.join(root_dir, tracks_folder)

    def search_video(self, search_query: str) -> Optional[YouTube]:
        """
        Searches YouTube for the given query and returns the first search result or None if no results were found.

        :param search_query: The query string to search for on YouTube.
        :return: YouTube video found (or None).
        """
        search = Search(search_query)
        if search_results := search.results:
            self.logger.debug(f"Search results for {search_query}, {search_results[0]}")
            return search_results[0]
        else:
            self.logger.warning(f"No search results for {search_query}")
            return None

    def search_video_url(self, search_url: str) -> Optional[YouTube]:
        """
        Searches YouTube for the given url and returns the first search result or None if no results were found.

        :param search_url: The url string for the YouTube video.
        :return: YouTube video found (or None).
        """
        video = YouTube(search_url)
        try:
            video_title = video.title
            self.logger.debug(f"Found video from url {video_title=}")
            return video
        except:
            self.logger.warning(f"No search results for {search_url}")
            return None

    def download_audio(self, video: YouTube) -> str:
        """
        Downloads the highest quality audio stream of the given YouTube video.

        :param video: The YouTube video object to download the audio from.
        :return: file path
        """

        def override_exists_at_path(file_path: str) -> bool:
            return (
                    os.path.isfile(file_path)
            )

        audio_stream = video.streams.get_audio_only()
        if audio_stream:
            audio_stream.exists_at_path = override_exists_at_path
            return audio_stream.download(output_path=self.track_dir)
        else:
            self.logger.warning(f"No audio stream available for this video {video}")
