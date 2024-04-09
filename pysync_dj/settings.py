import yaml
from typing import Any, Optional


class SettingsSingleton:
    """
    A singleton class for loading and accessing user settings from settings.yaml.

    This class uses a singleton design pattern ensures that settings are loaded only once and
    are accessible throughout the application.

    :ivar _instance: Holds the singleton instance.
    :ivar _settings: Stores the loaded settings.
    :ivar _logger: Program logger
    """

    _instance = None
    _settings = None
    _logger: 'EventQueueLogger' = None

    def __new__(cls,
                event_logger: 'EventQueueLogger' = None,
                file_path: Optional[str] = "../settings.yaml") -> 'SettingsSingleton':
        """
        Create a new instance of SettingsSingleton if it doesn't exist, or return the existing instance.

        :param file_path: The path to the settings file. Only used during the first instantiation.
        :return: An instance of SettingsSingleton.
        """
        if cls._instance is None:
            cls._instance = super(SettingsSingleton, cls).__new__(cls)
            cls._instance.load_settings(file_path)
            cls._logger = event_logger

        return cls._instance

    @staticmethod
    def load_settings(file_path: str) -> None:
        """
        Load settings from the specified file.

        :param file_path: The path to the JSON file containing settings.
        """
        if file_path is not None and SettingsSingleton._settings is None:
            with open(file_path, 'r') as file:
                SettingsSingleton._settings = yaml.safe_load(file)

    @staticmethod
    def get_setting(key: str) -> Any:
        """
        Retrieve a specific setting value by key.

        :param key: The key of the setting to retrieve.
        :return: The value of the specified setting.
        """
        return SettingsSingleton._settings.get(key)

    def update_setting(self, key: str, value: Any) -> None:
        """
        Update a specific setting value by key in the current session.

        :param key: The key of the setting to update.
        :param value: The new value for the setting.
        """
        if SettingsSingleton._settings is not None:
            SettingsSingleton._settings[key] = value
            self._logger.debug(f"Updated setting {key} to {value}")
        else:
            self._logger.error("Attempted to update setting on uninitialized settings.")

    def get_setting_object(self):
        return self._settings

    @property
    def spotify_client_id(self) -> str:
        return self.get_setting('spotify_client_id')

    @property
    def spotify_client_secret(self) -> str:
        return self.get_setting('spotify_client_secret')

    @property
    def spotify_redirect_uri(self) -> str:
        return self.get_setting('spotify_redirect_uri')

    @property
    def dj_library_drive(self) -> str:
        return self.get_setting('dj_library_drive')

    @property
    def tracks_folder(self) -> str:
        return self.get_setting('tracks_folder')

    @property
    def serato_subcrate_dir(self) -> str:
        return self.get_setting('serato_subcrate_dir')

    @property
    def rekordbox_playlist_folder(self) -> str:
        return self.get_setting('rekordbox_playlist_folder')

    @property
    def download_liked_songs(self) -> bool:
        return self.get_setting('download_liked_songs')

    @property
    def liked_songs_track_limit(self) -> int:
        return self.get_setting('liked_songs_track_limit')

    @property
    def liked_songs_date_limit(self) -> str:
        return self.get_setting('liked_songs_date_limit')

    @property
    def playlists_to_download(self) -> dict[str, str]:
        return self.get_setting('playlists_to_download')
