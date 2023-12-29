import os.path
from typing import Optional
import logging

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

        serato_crate = SeratoCrate("Liked Songs")
        rekordbox_playlist = RekordboxLibrary()

        liked_songs_data = self.spotify_helper.get_liked_tracks()
        self.download_playlist(liked_songs_data, serato_crate, rekordbox_playlist)

        self.logger.info("Saving crate data...")
        serato_crate.save_crate()
        rekordbox_playlist.create_m3u_file("Liked Songs.m3u")

    def download_all_playlists(self) -> None:
        """
        Get and download all playlists specified in settings, creating corresponding Serato crates and Rekordbox
        playlists.
        """
        for playlist_name, playlist_url in self.settings.playlists_to_download.items():
            playlist_id = extract_spotify_playlist_id(playlist_url)
            self.logger.info(f"Getting playlist information for playlist {playlist_name=}, {playlist_url=}, {playlist_id=}")

            serato_crate = SeratoCrate(playlist_name)
            rekordbox_playlist = RekordboxLibrary()

            playlist_data = self.spotify_helper.get_playlist_tracks(playlist_id)
            self.download_playlist(playlist_data, serato_crate, rekordbox_playlist)

            self.logger.info("Saving crate data...")
            serato_crate.save_crate()
            rekordbox_playlist.create_m3u_file(f"{playlist_name}.m3u")

    def download_playlist(self,
                          playlist_data: list[dict],
                          serato_crate: SeratoCrate,
                          rekordbox_playlist: RekordboxLibrary) -> None:
        """
        Downloads tracks from a given playlist and updates the Serato crate and Rekordbox playlist objects.

        :param playlist_data: List of dictionaries containing playlist track data.
        :param serato_crate: The Serato crate to update with downloaded tracks.
        :param rekordbox_playlist: The Rekordbox playlist to update with downloaded tracks.
        """

        for track in playlist_data:
            try:
                track_file_path = self.process_spotify_track(track)

                rekordbox_playlist.tracks.append(track_file_path)
                serato_crate.add_track(track_file_path)

            except Exception as e:
                self.logger.warning(f"Error, {e}")

    def process_spotify_track(self, track: dir) -> str:
        """
        Checks if a spotify track has already been downloaded, if it has a custom URL, or if it needs to be downloaded.

        :param track: A dictionary representing the Spotify track.
        :return: The file path of the downloaded track, or the existing file path if already downloaded.
        """
        track_id = track["track"]["id"]
        track_file_path = self.id_to_video_map.get(track_id)

        if track_file_path:
            # If the file paths is not a custom url and the file is downloaded, skip
            track_file_path_is_url = "youtube.com/" in track_file_path
            if not track_file_path_is_url and os.path.exists(track_file_path):
                self.logger.info(f"Skipping track\"{track['track']['name']}\" as it is already downloaded")
                return track_file_path

            # If the file path is a custom url, download the track from the given url
            if track_file_path_is_url:
                self.logger.info(f"Downloading track: \"{track['track']['name']}\" from custom url {track_file_path}")
                return self.download_track(track, track_file_path)

        # If there is no file path in the database, or fails other checks, download the track
        self.logger.info(f"Downloading track: \"{track['track']['name']}\"")
        return self.download_track(track)

    def download_track(self, track: dir, custom_yt_url: str = None) -> str:
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

        self.id_to_video_map[track_id] = track_file_path
        save_hashmap_to_json(self.id_to_video_map)

        return track_file_path


# Default usage
if __name__ == "__main__":
    pysync_dj = PySyncDJ()
    pysync_dj.run()
