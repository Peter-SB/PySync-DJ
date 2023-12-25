import os.path
from typing import Optional
import logging

import config
from crate import SeratoCrate
from rekordbox_library import RekordboxLibrary
from utils import init_logging, LOGGER_NAME, set_track_metadata, load_hashmap_from_json, save_hashmap_to_json, \
    extract_spotify_playlist_id, sanitize_filename
from spotify_helper import SpotifyHelper
from yt_downloader_helper import YouTubeDownloadHelper


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

        self.spotify_helper = SpotifyHelper(config.spotify_client_id, config.spotify_client_secret)
        self.ytd_helper = YouTubeDownloadHelper(config.dj_library_directory, config.tracks_folder)

        self.id_to_video_map = load_hashmap_from_json()

    def run(self):
        """
        Main method to run the application.

        This method orchestrates the overall process of syncing the Spotify library
        with the DJ library.
        """
        self.logger.info("Starting PySync DJ application.")

        self.download_liked_songs()
        self.download_all_playlists()

        self.logger.info("PySync DJ application run completed.")

    def download_liked_songs(self):
        if config.download_liked_songs:
            self.logger.info(f"Getting liked songs information")

            serato_crate = SeratoCrate("Liked Songs")
            rekordbox_playlist = RekordboxLibrary()

            liked_songs_data = self.spotify_helper.get_liked_tracks(limit=config.liked_songs_limit)
            self.download_playlist(liked_songs_data, serato_crate, rekordbox_playlist)

            self.logger.info("Saving crate data...")
            serato_crate.save_crate()
            rekordbox_playlist.create_m3u_file(f"E:\\rekordbox_playlist_3mus\\Liked Songs.m3u")

    def download_all_playlists(self):
        for playlist_name, playlist_url in config.playlists_to_download.items():
            playlist_id = extract_spotify_playlist_id(playlist_url)
            self.logger.info(f"Getting playlist information for playlist {playlist_name=}, {playlist_url=}, {playlist_id=}")

            serato_crate = SeratoCrate(playlist_name)
            rekordbox_playlist = RekordboxLibrary()

            playlist_data = self.spotify_helper.get_playlist_tracks(playlist_id)
            self.download_playlist(playlist_data, serato_crate, rekordbox_playlist)

            self.logger.info("Saving crate data...")
            serato_crate.save_crate()
            rekordbox_playlist.create_m3u_file(f"E:\\rekordbox_playlist_3mus\\{playlist_name}.m3u")

    def download_playlist(self,
                          playlist_data: list[dict],
                          serato_crate: SeratoCrate,
                          rekordbox_playlist: RekordboxLibrary) -> None:

        for track in playlist_data:
            try:
                if track_file_path := self.track_download_path(track):
                    self.logger.info(f"Skipping track\"{track['track']['name']}\" as it is already downloaded")
                else:
                    self.logger.info(f"Downloading track: \"{track['track']['name']}\"")
                    track_file_path = self.download_track(track)
                    set_track_metadata(track, track_file_path)

                rekordbox_playlist.tracks.append(track_file_path)
                serato_crate.add_track(track_file_path)

            except Exception as e:
                self.logger.warning(f"Error, {e}")

    def download_track(self, track: dir) -> str:
        """
        Takes a spotify track and downloads it from YouTube.

        :param track: Spotify track to download
        :return: The file location of the downloaded track
        """
        track_name = track["track"]["name"]
        track_artist = sanitize_filename(track["track"]["artists"][0]["name"])
        track_id = track["track"]["id"]

        youtube_video = self.ytd_helper.search_video(f"{track_artist} - {track_name}")
        track_file_path = self.ytd_helper.download_audio(youtube_video, output_path=track_artist)
        self.id_to_video_map[track_id] = track_file_path
        save_hashmap_to_json(self.id_to_video_map)

        return track_file_path

    def track_download_path(self, track: dict) -> Optional[str]:
        track_id = track["track"]["id"]
        if track_file_path := self.id_to_video_map.get(track_id):
            if os.path.exists(track_file_path):
                return track_file_path
        return None


# Example usage
if __name__ == "__main__":
    pysync_dj = PySyncDJ()
    pysync_dj.run()
