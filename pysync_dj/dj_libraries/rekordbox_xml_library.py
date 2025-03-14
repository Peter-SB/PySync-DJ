import os
import urllib
import xml.etree.ElementTree as ET
from typing import Optional, Dict, Union, Any
from xml.dom import minidom

from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

from settings import SettingsSingleton


class RekordboxXMLLibrary:
    """
    This class will build a iTune Music Library.xml to be used by RekordBox. The xml file mimics an iTunes library
    so that users can import there whole PySync DJ library using the import iTunes library feature in RekordBox.
    """

    def __init__(self, event_logger: 'EventQueueLogger') -> None:
        """
        Initialize the ItunesLibrary class.
        """
        self.unique_track_id_counter = -1
        self.unique_playlist_id_counter = 1

        self.playlists_array: Optional[ET.SubElement] = None
        self.all_tracks_dict: Optional[ET.SubElement] = None
        self.plist: Optional[ET.SubElement] = None

        self.event_logger = event_logger
        self.settings = SettingsSingleton()
        self.create_empty_library_xml()

    def gen_track_id(self) -> int:
        """ Generate a unique track id"""
        self.unique_track_id_counter += 1
        return self.unique_track_id_counter

    def gen_playlist_id(self) -> int:
        """ Generate a unique playlist id"""
        self.unique_playlist_id_counter += 1
        return self.unique_playlist_id_counter

    def create_empty_library_xml(self) -> None:
        # XML declaration and root element setup
        self.plist = ET.Element("plist", version="1.0")

        # Main dictionary element
        main_dict = ET.SubElement(self.plist, "dict")

        # Adding "Library Persistent ID" key with an empty string value
        ET.SubElement(main_dict, "key").text = "Library Persistent ID"
        ET.SubElement(main_dict, "string").text = " "  # Needed or Rekordbox won't read the xml library

        # All tracks in library dictionary
        ET.SubElement(main_dict, "key").text = "Tracks"
        self.all_tracks_dict = ET.SubElement(main_dict, "dict")

        # Playlists array for adding playlist (or folder) dicts
        ET.SubElement(main_dict, "key").text = "Playlists"
        self.playlists_array = ET.SubElement(main_dict, "array")

        self.add_root_playlist()

    def save_xml(self, file_name: str = "PySyncLibrary.xml") -> None:
        # Convert to a pretty XML string
        rough_string = ET.tostring(self.plist, "utf-8")
        reparsed = minidom.parseString(rough_string)
        pretty_xml_str = reparsed.toprettyxml(indent="  ", encoding="UTF-8")

        # Writing the doctype manually since ElementTree won"t do it for us and its needed by RekordBox
        doctype = '<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">'
        final_xml_content = doctype + '\n' + pretty_xml_str.decode('utf-8')

        # Save to file
        file_location = os.path.join(self.settings.dj_library_drive,
                                     self.settings.rekordbox_playlist_folder,
                                     file_name)
        os.makedirs(os.path.dirname(file_location), exist_ok=True)
        with open(file_location, "w", encoding="UTF-8") as f:
            f.write(final_xml_content)

    def add_playlist(self, playlist_name: str, file_locations: list[str]) -> None:
        """
        Adds playlist information to the playlists Element.

        :param playlist_name: name of the playlist being saved.
        :param file_locations: list of locations

        """
        track_dict = [(self.gen_track_id(), file_location) for file_location in file_locations]

        self.add_to_all_track(track_dict)

        playlist_id = self.gen_playlist_id()

        playlist_info = {
            "Name": playlist_name,
            "Description": " ",
            "Playlist ID": playlist_id,
            "Playlist Persistent ID": f"{playlist_id}",
            "Parent Persistent ID": "PySyncDJ",
            "All Items": True,
            "Playlist Items": [{"Track ID": track_id} for track_id, file_location in track_dict]
        }

        self.add_playlist_from_elements(playlist_info)

    def add_playlist_from_elements(self, playlist_info: dict) -> None:
        playlist_dict = ET.SubElement(self.playlists_array, 'dict')
        for key, value in playlist_info.items():
            ET.SubElement(playlist_dict, 'key').text = key
            if key == "Playlist Items":
                array_element = ET.SubElement(playlist_dict, 'array')
                for item in value:
                    dict_element = ET.SubElement(array_element, 'dict')
                    ET.SubElement(dict_element, 'key').text = 'Track ID'
                    ET.SubElement(dict_element, 'integer').text = str(item['Track ID'])
            elif isinstance(value, bool):
                ET.SubElement(playlist_dict, 'true' if value else 'false')
            else:
                child_type = 'string' if isinstance(value, str) else 'integer'
                ET.SubElement(playlist_dict, child_type).text = str(value)

    def add_to_all_track(self, tracks_dict: list[tuple[int, str]]) -> None:
        """
        Adds track information to the tracks Element.

        :param tracks_dict: [(track_id, track_location)]
        """

        tracks_dict = self.format_tracks_dic(tracks_dict)

        for track_id, details in tracks_dict.items():
            track_key = ET.SubElement(self.all_tracks_dict, 'key')
            track_key.text = str(track_id)

            track_dict = ET.SubElement(self.all_tracks_dict, 'dict')
            for key, value in details.items():
                ET.SubElement(track_dict, 'key').text = key
                child = ET.SubElement(track_dict, 'string' if key != 'Track ID' else 'integer')
                child.text = str(value)

    def format_tracks_dic(self, downloaded_tracks_dict: list[tuple[int, str]]) -> Optional[
        dict[int, dict[str, Union[Union[str, int], Any]]]]:
        """
        Formats the track dictionary ready to be saved in the xml tree
        """
        formatted_track_dict = {}

        for track_id, file_location in downloaded_tracks_dict:
            file_location = os.path.join(self.settings.dj_library_drive, file_location)
            try:
                audio = MP3(file_location, ID3=EasyID3)
                name = audio['title'][0] if 'title' in audio else 'Unknown'
                artist = audio['artist'][0] if 'artist' in audio else 'Unknown'
                album = audio['album'][0] if 'album' in audio else 'Unknown'
                total_time = int(audio.info.length * 100)  # todo: add track length to xml library data

                location = f"file://localhost/{urllib.parse.quote(file_location)}"

                formatted_track_dict[track_id] = {
                    "Track ID": track_id,
                    "Name": name,
                    "Artist": artist,
                    "Album": album,
                    "Kind": "MPEG audio file",
                    "Persistent ID": track_id,
                    "Track Type": "File",
                    "Location": location
                }

            except Exception as e:
                print(f"Error reading file {file_location}: {e}")
                return None

        return formatted_track_dict

    def add_root_playlist(self) -> None:
        """
        Add the root "PySync DJ" Folder.
        """

        root_folder_elements = [
            ("Name", "string", "PySync DJ"),
            ("Description", "string", " "),
            ("Playlist ID", "integer", "1"),
            ("Playlist Persistent ID", "string", "PySyncDJ"),
            ("All Items", "true", None),
            ("Folder", "true", None)
        ]

        root_playlist = ET.SubElement(self.playlists_array, "dict")
        for key, tag, text in root_folder_elements:
            ET.SubElement(root_playlist, "key").text = key
            child = ET.SubElement(root_playlist, tag)
            if text is not None:
                child.text = text

