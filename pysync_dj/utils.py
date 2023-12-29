import json
import logging
import os
import re
from pathlib import Path
from typing import Optional

import unicodedata
from mutagen.id3 import TIT2, TPE1, TALB, COMM, ID3, APIC
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4, MP4Cover
from mutagen.mp4 import MP4Tags
import requests

LOGGER_NAME = "LOGGER_MAIN"


def init_logging(file_name: str = "logs/pysync_dj.log") -> None:
    """
    Initialize logging for the application. This sets up logging to output to both
    the console and a file.

    :param file_name: file to log to
    """
    # Create a logger
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)  # Set the logging level

    # Create a file handler that logs messages
    fh = logging.FileHandler(os.path.join(Path.cwd().parent, file_name))
    fh.setLevel(logging.DEBUG)  # Set the logging level for the file handler

    # Create a console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)  # Set the logging level for the console handler

    # Create formatter and add it to the handlers
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)


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
    audio['COMM'] = COMM(encoding=3, lang='eng', desc='Popularity', text=str(track_popularity))

    # Adding cover art
    if track_cover_imgs:
        response = requests.get(track_cover_imgs[0]["url"])
        if response.status_code == 200:
            audio.tags.add(
                APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=3,  # Cover image
                    desc=u'Cover',
                    data=response.content
                )
            )

    audio.save()


def save_hashmap_to_json(id_to_video_map: dict, file_path: str = "../id_to_video_map.json") -> None:
    """
    Save a hashmap to a JSON file.

    :param id_to_video_map: The hashmap to save.
    :param file_path: The path to the JSON file where the hashmap will be saved.
    """
    with open(file_path, 'w') as file:
        json.dump(id_to_video_map, file, indent=4)


def load_hashmap_from_json(file_path: str = "../id_to_video_map.json") -> dict:
    """
    Load a hashmap from a JSON file.

    :param file_path: The path to the JSON file from which to load the hashmap.
    :return: The loaded hashmap.
    """
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}  # Return an empty dictionary if the file does not exist


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
