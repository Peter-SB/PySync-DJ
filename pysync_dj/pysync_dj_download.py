import concurrent.futures
import multiprocessing
import traceback

import pytube.exceptions

from dj_libraries.itunes_library import ItunesLibrary
from event_queue import EventQueueLogger, EventQueueHandler
from track_processor import process_track
from dj_libraries.serato_crate import SeratoCrate
from settings import SettingsSingleton
from dj_libraries.rekordbox_library import RekordboxLibrary
from utils import load_hashmap_from_json, \
    extract_spotify_playlist_id
from spotify_helper import SpotifyHelper
from yt_download_helper import YouTubeDownloadHelper


class PySyncDJDownload:
    """
    This class does the downloading component of the software.
    """

    def __init__(self, selected_drive, event_queue):
        self.event_queue = event_queue
        self.event_logger: EventQueueLogger = EventQueueLogger(self.event_queue)

        self.event_logger.info("=======================================================")
        self.event_logger.info("===============   Starting  Download  ================")
        self.event_logger.info("=======================================================")

        self.settings = SettingsSingleton(self.event_logger)
        if selected_drive:
            self.settings.update_setting("dj_library_drive", selected_drive)
        self.total_playlists = (
                int(self.settings.download_liked_songs) +
                (len(self.settings.playlists_to_download) if self.settings.playlists_to_download else 0)
        )

        self.spotify_helper = SpotifyHelper(self.event_logger)
        self.ytd_helper = YouTubeDownloadHelper(self.settings.dj_library_drive, self.settings.tracks_folder)
        self.itunes_library = ItunesLibrary(self.event_logger)

        self.run()

    def run(self):
        """
        Main method to run the download algorithm.

        This method does the overall process of syncing the Spotify library
        with the DJ library.
        """
        if self.settings.download_liked_songs:
            self.download_liked_songs()
        if self.settings.playlists_to_download:
            self.download_all_playlists()

        self.itunes_library.save_xml()

        self.event_logger.update_progress(1)
        self.event_logger.enable_download_button()
        self.event_logger.info("Download completed!")

    def download_liked_songs(self) -> None:
        """
        Get and download the user's liked songs from Spotify, creating corresponding a Serato crate and Rekordbox
        playlist.
        """
        self.event_logger.info(f"Getting liked songs information")
        playlist_name = "Liked Songs"

        liked_songs_data = self.spotify_helper.get_liked_tracks()
        downloaded_track_list = self.download_playlist(liked_songs_data, 0) or []

        self.save_to_dj_libraries(playlist_name, downloaded_track_list)

    def download_all_playlists(self) -> None:
        """
        Get and download all playlists specified in settings, creating corresponding Serato crates and Rekordbox
        playlists.
        """

        playlist_index = 1 if self.settings.download_liked_songs else 0
        for playlist_name, playlist_url in self.settings.playlists_to_download.items():
            playlist_id = extract_spotify_playlist_id(playlist_url)

            self.event_logger.debug(
                f"Getting playlist information for playlist {playlist_name=}, {playlist_url=}, {playlist_id=}")
            self.event_logger.info(f"Downloading playlist: {playlist_name}")

            playlist_data = self.spotify_helper.get_playlist_tracks(playlist_id)
            downloaded_track_list = self.download_playlist(playlist_data, playlist_index)

            self.save_to_dj_libraries(playlist_name, downloaded_track_list)

            playlist_index += 1

    def save_to_dj_libraries(self, playlist_name, downloaded_track_list):
        self.event_logger.info("Saving DJ library data...")
        SeratoCrate(playlist_name, downloaded_track_list)
        RekordboxLibrary(playlist_name, downloaded_track_list, self.settings.dj_library_drive)
        self.itunes_library.add_playlist(playlist_name, downloaded_track_list)

    def download_playlist(self, playlist_data: list[dict], playlist_index: int) -> list[str]:
        """
        Downloads tracks from a given playlist and updates the Serato crate and Rekordbox playlist objects.

        :param playlist_data: List of dictionaries containing playlist track data.
        :param playlist_index: Index of the playlist out of all the playlist to download.
        :return: List of downloaded tack's file paths.
        """

        manager = multiprocessing.Manager()
        id_to_video_map = manager.dict(load_hashmap_from_json(self.settings.dj_library_drive))
        lock = manager.Lock()

        downloaded_tracks = []

        with concurrent.futures.ProcessPoolExecutor(max_workers=3) as executor:
            # Submit tasks to the executor
            future_to_track_data = {executor.submit(process_track,
                                                    track_data,
                                                    lock,
                                                    self.settings.get_setting_object(),
                                                    id_to_video_map,
                                                    self.event_queue): track_data
                                    for track_data in playlist_data
                                    }

            for index, future in enumerate(concurrent.futures.as_completed(future_to_track_data)):
                track_data = future_to_track_data[future]
                track_artist = track_data.get("track", {}).get("artists", [{}])[0].get("name", "Unknown")
                track_identifier = f"{track_artist} - {track_data.get('track', {}).get('name')}"

                try:
                    track_file_path = future.result()
                    downloaded_tracks.insert(index, track_file_path)

                except pytube.exceptions.AgeRestrictedError as e:
                    self.event_logger.error(f"Age Restricted Video, \"{track_identifier}\" Cant Download.")
                    self.event_logger.debug(f"{track_data=}, error={e}")

                except Exception as e:
                    self.event_logger.error(f"Error downloading track:  \"{track_identifier}\"")
                    self.event_logger.debug(f"{track_data=}, error={e}")
                    self.event_logger.error(traceback.format_exc())
                    print(e)

                self.event_logger.update_progress((index / len(playlist_data) + playlist_index) / self.total_playlists)

        return downloaded_tracks


if __name__ == "__main__":
    PySyncDJDownload(None, EventQueueHandler())
