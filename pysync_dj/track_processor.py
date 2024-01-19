import json
import logging
import os
from typing import Tuple, Any, Union

from utils import LOGGER_NAME, sanitize_filename, load_hashmap_from_json, set_track_metadata, save_hashmap_to_json
from yt_download_helper import YouTubeDownloadHelper


def process_track(track_data, lock, settings, id_to_video_map):
    track_consumer = TrackProcessor(track_data, lock, settings, id_to_video_map)
    return track_consumer.process_spotify_track(track_data)


class TrackProcessor:
    def __init__(self, track_data, lock, settings, id_to_video_map):
        self.logger = logging.getLogger(LOGGER_NAME)
        self.ytd_helper = YouTubeDownloadHelper(settings.dj_library_directory, settings.tracks_folder)
        self.track_data = track_data
        self.lock = lock
        self.id_to_video_map = id_to_video_map
        self.settings = settings

    def process_spotify_track(self, track: dir):
        """
        Checks if a spotify track has already been downloaded, if it has a custom URL, or if it needs to be downloaded.

        :param track: A dictionary representing the Spotify track.
        :return: The file path of the downloaded track, or the existing file path if already downloaded.
        """
        track_id = track["track"]["id"]
        track_file_path = self.id_to_video_map.get(track_id)

        if track_file_path:
            track_file_path_is_url = "youtube.com/" in track_file_path
            track_file_path_with_drive = os.path.join(self.settings.dj_library_directory, track_file_path)

            # If the file paths is not a custom url and the file is downloaded, skip
            if not track_file_path_is_url and os.path.exists(track_file_path_with_drive):
                self.logger.info(f"Skipping track\"{track['track']['name']}\" as it is already downloaded")
                return track_file_path

            # If the file path is a custom url, download the track from the given url
            if track_file_path_is_url:
                self.logger.info(f"Downloading track: \"{track['track']['name']}\" from custom url {track_file_path}")
                return self.download_track(track, track_file_path)

        # If there is no file path in the database, or fails other checks, download the track
        self.logger.info(f"Downloading track: \"{track['track']['name']}\"")
        return self.download_track(track)

    def download_track(self, track: dir, custom_yt_url: str = None):
        """
        Takes a spotify track and downloads it from YouTube.

        :param track: Spotify track to download
        :param custom_yt_url: A url for a video to be used instead of a YouTube search if provided
        :return: The file location of the downloaded track
        """
        track_name = track["track"]["name"]
        track_artist = sanitize_filename(track["track"]["artists"][0]["name"])
        track_id = track["track"]["id"]

        if custom_yt_url:
            youtube_video = self.ytd_helper.search_video_url(custom_yt_url)
        else:
            youtube_video = self.ytd_helper.search_video(f"{track_artist} - {track_name}")

        track_file_path = self.ytd_helper.download_audio(youtube_video)
        set_track_metadata(track, track_file_path)

        with self.lock:
            self.id_to_video_map[track_id] = os.path.splitdrive(track_file_path)[1]
            save_hashmap_to_json(dict(self.id_to_video_map))

        return track_file_path
