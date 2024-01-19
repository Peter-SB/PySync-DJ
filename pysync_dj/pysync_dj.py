import concurrent.futures
import os.path
from typing import Optional
import logging

import queue
import multiprocessing

from track_processor import process_track
from crate import SeratoCrate
from settings import SettingsSingleton
from rekordbox_library import RekordboxLibrary
from utils import init_logging, LOGGER_NAME, set_track_metadata, load_hashmap_from_json, save_hashmap_to_json, \
    extract_spotify_playlist_id, sanitize_filename
from spotify_helper import SpotifyHelper
from yt_download_helper import YouTubeDownloadHelper


class PySyncDJ:
    """
    Main class for the PySync DJ application.

    This class integrates different components of the application
    such as Spotify playlist querying, YouTube video downloading,
    and other functionalities to sync a Spotify library with a DJ library.
    """

    def __init__(self):
        """
        Initializes the PySyncDJ application.
        """
        init_logging()
        self.logger = logging.getLogger(LOGGER_NAME)
        self.settings = SettingsSingleton()

        self.spotify_helper = SpotifyHelper()
        self.ytd_helper = YouTubeDownloadHelper(self.settings.dj_library_directory, self.settings.tracks_folder)

        self.logger.info(f"Loading local track database")
        self.id_to_video_map = load_hashmap_from_json()

    def run(self):
        """
        Main method to run the application.

        This method orchestrates the overall process of syncing the Spotify library
        with the DJ library.
        """
        self.logger.info("Starting PySync DJ application.")

        if self.settings.download_liked_songs:
            self.download_liked_songs()
        self.download_all_playlists()

        self.logger.info("PySync DJ application run completed.")

    def download_liked_songs(self) -> None:
        """
        Get and download the user's liked songs from Spotify, creating corresponding a Serato crate and Rekordbox
        playlist.
        """
        self.logger.info(f"Getting liked songs information")
        playlist_name = "Liked Songs"

        liked_songs_data = self.spotify_helper.get_liked_tracks()
        downloaded_track_list = self.download_playlist(liked_songs_data)

        self.logger.info("Saving crate data...")

        SeratoCrate(playlist_name, downloaded_track_list)
        RekordboxLibrary(playlist_name, downloaded_track_list)

    def download_all_playlists(self) -> None:
        """
        Get and download all playlists specified in settings, creating corresponding Serato crates and Rekordbox
        playlists.
        """
        for playlist_name, playlist_url in self.settings.playlists_to_download.items():
            playlist_id = extract_spotify_playlist_id(playlist_url)
            self.logger.info(f"Getting playlist information for playlist {playlist_name=}, {playlist_url=}, {playlist_id=}")

            playlist_data = self.spotify_helper.get_playlist_tracks(playlist_id)
            downloaded_track_list = self.download_playlist(playlist_data)

            self.logger.info("Saving crate data...")
            SeratoCrate(playlist_name, downloaded_track_list)
            RekordboxLibrary(playlist_name, downloaded_track_list)

    def download_playlist(self, playlist_data: list[dict]) -> list[str]:
        """
        Downloads tracks from a given playlist and updates the Serato crate and Rekordbox playlist objects.

        :param playlist_data: List of dictionaries containing playlist track data.
        :return:
        """

        manager = multiprocessing.Manager()
        lock = manager.Lock()

        downloaded_tracks = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_track = [executor.submit(process_track, track_data, lock, self.settings) for track_data in playlist_data]
            for future in concurrent.futures.as_completed(future_to_track):
                try:
                    track_file_path, track_id = future.result()
                    downloaded_tracks.append(track_file_path)

                    with lock:
                        self.id_to_video_map[track_id] = track_file_path
                        save_hashmap_to_json(self.id_to_video_map)

                except Exception as e:
                    print(e)

        return downloaded_tracks


# Default usage
if __name__ == "__main__":
    pysync_dj = PySyncDJ()
    pysync_dj.run()
