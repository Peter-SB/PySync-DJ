import os
import urllib
import xml.etree.ElementTree as ET
from typing import Optional
from xml.dom import minidom

from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

from settings import SettingsSingleton


class ItunesLibrary:

    def __init__(self) -> None:
        """
        Initialize the ItunesLibrary class.
        """
        self.unique_track_id_counter = -1
        self.unique_playlist_id_counter = 1

        self.playlists_array: Optional[ET.SubElement] = None
        self.all_tracks_dict: Optional[ET.SubElement] = None
        self.plist: Optional[ET.SubElement] = None

        self.settings = SettingsSingleton()
        self.create_empty_library_xml()

    def gen_track_id(self):
        self.unique_track_id_counter += 1
        return self.unique_track_id_counter

    def gen_playlist_id(self):
        self.unique_playlist_id_counter += 1
        return self.unique_playlist_id_counter

    def create_empty_library_xml(self):
        # XML declaration and root element setup
        self.plist = ET.Element("plist", version="1.0")

        # Main dictionary element
        main_dict = ET.SubElement(self.plist, "dict")

        # Adding "Library Persistent ID" key with an empty string value
        ET.SubElement(main_dict, "key").text = "Library Persistent ID"
        ET.SubElement(main_dict, "string").text = " "

        # Tracks dictionary (empty for now)
        ET.SubElement(main_dict, "key").text = "Tracks"
        self.all_tracks_dict = ET.SubElement(main_dict, "dict")

        # Playlists array with one dict element
        ET.SubElement(main_dict, "key").text = "Playlists"
        self.playlists_array = ET.SubElement(main_dict, "array")

        self.add_root_playlist()

    def save_xml(self, file_name="iTunes Music Library.xml"):
        # Convert to a pretty XML string
        rough_string = ET.tostring(self.plist, "utf-8")
        reparsed = minidom.parseString(rough_string)
        pretty_xml_str = reparsed.toprettyxml(indent="  ", encoding="UTF-8")

        doctype = '<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">'
        final_xml_content = doctype + '\n' + pretty_xml_str.decode('utf-8')

        # Writing the doctype manually since ElementTree won"t do it for us
        file_location = os.path.join(self.settings.dj_library_drive,
                                     self.settings.rekordbox_playlist_folder,
                                     file_name)
        with open(file_location, "w", encoding="UTF-8") as f:
            f.write(final_xml_content)

    def add_playlist(self, playlist_name, file_locations):
        """
        Adds playlist information to the playlists Element.

        :param playlist_name: name of the playlist being saved.
        :param file_locations: list of locations tuples

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

    def add_playlist_from_elements(self, playlist_info):
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

    def add_to_all_track(self, tracks_dict):
        """
        tracks_dict: [(track_id, track_location)]

        Adds track information to the tracks Element.
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

    def format_tracks_dic(self, downloaded_tracks_dict) -> {}:
        """
        return tracks: {
            "472": {
                "Track ID": 472,
                "Name": "Constant Reminder",
                "Artist": "Anile, DRS",
                "Album": "Constant Reminder",
                "Kind": "MPEG audio file",
                "Persistent ID": "Constant%Reminder",
                "Track Type": "File",
                "Location": "file://localhost/D:/PySync%20Dj%20Tracks/Anile%20-%20Constant%20Reminder%20ft%20DRS.mp3"
            }
        }
        """
        formatted_track_dict = {}

        for track_id, file_location in downloaded_tracks_dict:
            file_location = os.path.join(self.settings.dj_library_drive, file_location)
            try:
                audio = MP3(file_location, ID3=EasyID3)
                name = audio['title'][0] if 'title' in audio else 'Unknown'
                artist = audio['artist'][0] if 'artist' in audio else 'Unknown'
                album = audio['album'][0] if 'album' in audio else 'Unknown'
                total_time = int(audio.info.length * 100)

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

    def add_root_playlist(self):
        # Filling in the playlist dict
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

