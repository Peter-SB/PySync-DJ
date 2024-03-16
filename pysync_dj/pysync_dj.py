import concurrent.futures
import traceback
import multiprocessing

from ui_elements.progress_bar import ProgressBar
from ui_elements.ui_output_log import UIOutputLog
from track_processor import process_track
from serato_crate import SeratoCrate
from settings import SettingsSingleton
from rekordbox_library import RekordboxLibrary
from utils import load_hashmap_from_json, \
    extract_spotify_playlist_id
from spotify_helper import SpotifyHelper
from yt_download_helper import YouTubeDownloadHelper


class PySyncDJ:
    """
    Main class for the PySync DJ application.

    This class integrates different components of the application
    such as Spotify playlist querying, YouTube video downloading,
    and other functionalities to sync a Spotify library with a DJ library.
    """

    def __init__(self, selected_drive):
        """
        Initializes the PySyncDJ application.
        """
        self.progress_bar = ProgressBar()
        self.logger = UIOutputLog()

        self.settings = SettingsSingleton()
        self.settings.update_setting("dj_library_drive", selected_drive)

        self.spotify_helper = SpotifyHelper()
        self.ytd_helper = YouTubeDownloadHelper(self.settings.dj_library_drive, self.settings.tracks_folder)

    def run(self):
        """
        Main method to run the application.

        This method orchestrates the overall process of syncing the Spotify library
        with the DJ library.
        """
        #self.ui_output_log.log("Starting PySync DJ application.")
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
        RekordboxLibrary(playlist_name, downloaded_track_list, self.settings.dj_library_drive)

    def download_all_playlists(self) -> None:
        """
        Get and download all playlists specified in settings, creating corresponding Serato crates and Rekordbox
        playlists.
        """
        playlist_index = 0
        for playlist_name, playlist_url in self.settings.playlists_to_download.items():
            playlist_id = extract_spotify_playlist_id(playlist_url)

            self.logger.info(f"Getting playlist information for playlist {playlist_name=}, {playlist_url=}, {playlist_id=}")

            playlist_data = self.spotify_helper.get_playlist_tracks(playlist_id)
            downloaded_track_list = self.download_playlist(playlist_data, playlist_index)

            self.logger.info("Saving DJ library data...")
            SeratoCrate(playlist_name, downloaded_track_list)
            RekordboxLibrary(playlist_name, downloaded_track_list, self.settings.dj_library_drive)

            playlist_index += 1


    def download_playlist(self, playlist_data: list[dict], playlist_index: int) -> list[str]:
        """
        Downloads tracks from a given playlist and updates the Serato crate and Rekordbox playlist objects.

        :param playlist_data: List of dictionaries containing playlist track data.
        :return: List of downloaded tack's file paths.
        """

        manager = multiprocessing.Manager()
        id_to_video_map = manager.dict(load_hashmap_from_json(self.settings.dj_library_drive))
        lock = manager.Lock()

        downloaded_tracks = []

        with concurrent.futures.ProcessPoolExecutor() as executor:
            track_processors = [executor.submit(
                process_track,
                track_data,
                lock,
                self.settings,
                id_to_video_map,
                self.logger) for track_data in playlist_data]

            for index, track_processor in enumerate(concurrent.futures.as_completed(track_processors)):

                number_of_playlists = len(self.settings.playlists_to_download)
                self.progress_bar.set_progress(((index+1)/ len(playlist_data) + playlist_index) / number_of_playlists)

                try:
                    track_file_path = track_processor.result()
                    downloaded_tracks.insert(index, track_file_path)

                except Exception as e:
                    print(f"E {e}")
                    print(traceback.format_exc())

        return downloaded_tracks


# Default usage
if __name__ == "__main__":
    pysync_dj = PySyncDJ()
    pysync_dj.run()
