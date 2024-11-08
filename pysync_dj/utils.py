import datetime
import json
import logging
import os
import re
from logging.handlers import RotatingFileHandler
from typing import Optional

import unicodedata
from mutagen.id3 import TIT2, TPE1, TALB, COMM, ID3, APIC
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4, MP4Cover
from mutagen.mp4 import MP4Tags
import requests

LOGGER_NAME = "LOGGER_MAIN"


def setup_file_logging() -> logging.Logger:
    def find_log_files(directory):
        matched_files = []
        for filename in os.listdir(directory):
            if filename.startswith("pysync_dj_log_") and filename.endswith(".log"):
                matched_files.append(os.path.join(directory, filename))
        return matched_files

    log_directory = "../logs"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    # Clean up old log files, ensure only the latest 3 are kept.
    existing_logs = find_log_files(os.path.join(log_directory))
    existing_logs.sort(reverse=True)
    for old_log in existing_logs[2:]:
        os.remove(old_log)

    # Filename with datetime suffix
    datetime_suffix = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = os.path.join(log_directory, f"pysync_dj_log_{datetime_suffix}.log")

    # Set up logging
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)  # Adjust as needed

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)  # Adjust as needed
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler with rotation
    file_handler = RotatingFileHandler(log_filename, maxBytes=5 * 1024 * 1024, backupCount=2)
    file_handler.setLevel(logging.DEBUG)  # Adjust as needed
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger


def set_track_metadata_mp4(track: dir, track_file_path: str) -> None:
    """
    Adds metadata from the spotify track data to the mp4 audio file including cover art if avalible.

    :param track: Track data from spotify
    :param track_file_path: path to the mp4 audio file
    """
    audio = MP4(track_file_path)
    if not audio.tags:
        audio.tags = MP4Tags()

    track_data = track["track"]
    track_name = track_data["name"]
    track_artist = track_data["artists"][0]["name"]
    track_artists = ", ".join([artist["name"] for artist in track_data["artists"]])

    track_popularity = track_data["popularity"]
    track_album = track_data["album"]["name"]
    track_cover_imgs = track_data["album"]["images"]

    # Basic metadata
    audio.tags = MP4Tags()
    audio["\xa9nam"] = track_name
    audio["\xa9ART"] = track_artists
    audio["\xa9alb"] = track_album
    audio["\xa9cmt"] = f"{track_popularity=}"

    # Adding cover art
    if track_cover_imgs:
        response = requests.get(track_cover_imgs[1]["url"])
        if response.status_code == 200:
            audio["covr"] = [MP4Cover(response.content, imageformat=MP4Cover.FORMAT_JPEG)]

    audio.save()


def set_track_metadata(track: dict, track_file_path: str) -> None:
    """
    Adds metadata from the Spotify track data to the MP3 audio file, including cover art if available.

    :param track: Track data from Spotify.
    :param track_file_path: Path to the MP3 audio file.
    """
    audio = MP3(track_file_path, ID3=ID3)

    track_data = track["track"]
    track_name = track_data["name"]
    track_artist = track_data["artists"][0]["name"]
    track_artists = ", ".join([artist["name"] for artist in track_data["artists"]])
    track_popularity = track_data["popularity"]
    track_album = track_data["album"]["name"]
    track_cover_imgs = track_data["album"]["images"]

    # Basic metadata
    audio['TIT2'] = TIT2(encoding=3, text=track_name)
    audio['TPE1'] = TPE1(encoding=3, text=track_artists)
    audio['TALB'] = TALB(encoding=3, text=track_album)
    audio['COMM'] = COMM(encoding=3, lang='eng', desc=f'Popularity = {track_popularity}',
                         text=f"{track_popularity}")  # todo: Needs fixing after mp3 update

    audio.save()

    audio = ID3(track_file_path)

    # Adding cover art
    if track_cover_imgs:
        response = requests.get(track_cover_imgs[0]["url"])
        if response.status_code == 200:
            audio['APIC'] = APIC(
                encoding=3,
                mime='image/jpeg',
                type=3,  # Cover image
                desc=u'Cover',
                data=response.content
            )

    audio.save()


def save_hashmap_to_json(id_to_video_map: dict, file_drive, file_path: str = "id_to_video_map.json") -> None:
    """
    Save a hashmap to a JSON file.

    :param file_drive: The Drive to save the hashmap to.
    :param id_to_video_map: The hashmap to save.
    :param file_path: The path to the JSON file where the hashmap will be saved.
    """
    with open(os.path.join(file_drive, file_path), 'w') as file:
        json.dump(id_to_video_map, file, indent=4)


def load_hashmap_from_json(file_drive, file_path: str = "id_to_video_map.json") -> dict:
    """
    Load a hashmap from a JSON file, creating the file with an empty dictionary if it doesn't exist.

    :param file_drive: The drive to load the hash map from.
    :param file_path: The path to the JSON file from which to load the hashmap.
    :return: The loaded hashmap.
    """
    full_path = os.path.join(file_drive, file_path)
    if not os.path.exists(full_path):
        # Create the file with an empty dictionary if it doesn't exist
        with open(full_path, 'w') as file:
            json.dump({}, file)
        return {}
    else:
        # Load the existing file
        with open(full_path, 'r') as file:
            return json.load(file)


def extract_spotify_playlist_id(url: str) -> Optional[str]:
    """
    Extract the Spotify playlist ID from a given URL.

    :param url: The Spotify playlist URL.
    :return: The extracted playlist ID or None if the URL does not contain a valid ID.
    """
    # Pattern to match a sequence of alphanumeric characters which could be a Spotify playlist ID
    pattern = r'([a-zA-Z0-9]{22})'  # Spotify IDs are 22 characters long
    match = re.search(pattern, url)
    return match.group(1) if match else None


def sanitize_filename(filename: str, max_length: Optional[int] = 255, replace_spaces: bool = False) -> str:
    """
    Sanitize a string to be used as a filename. Removes or replaces characters that are not allowed
    in filenames and limits the length of the filename.

    :param filename: The string to be sanitized for use as a filename.
    :param max_length: The maximum allowed length of the filename (default is 255).
    :param replace_spaces: Should replace spaces with underscores
    :return: The sanitized filename.
    """
    # Normalize Unicode characters to the closest equivalent ASCII character
    normalized = unicodedata.normalize('NFKD', filename).encode('ascii', 'ignore').decode('ascii')

    # Replace spaces with underscores
    if replace_spaces:
        normalized = normalized.replace(" ", "_")

    # Remove or replace characters that are not allowed in filenames
    sanitized = re.sub(r'[\/\\:*?"<>|]', '', normalized)

    # Limit the length of the filename
    return sanitized[:max_length]
