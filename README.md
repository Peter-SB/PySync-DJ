
<p align="center">
  <img src='docs/DALLE_logo.png' width='400'>
</p>

# PySync DJ

## Overview
PySync DJ is a Python-based application designed to sync a Spotify library with a DJ library. It allows users to select Spotify playlists, downloads the tracks as MP3 files (sourced from YouTube), and integrates them with both Serato and Rekordbox DJ libraries. The project aims to streamline the often tedious process of syncing and managing music playlists so we can spend more time DJing!.

**Full 1.0 Design Document [Here](docs/Design%20Specification%20Document.md)**  
**Release Notes [Here](docs/Relase%20Notes.md)**

<p align="center">
  <img src='docs/Screenshot UI.png' width='450'>
</p>

## Features
- **Spotify Integration**: Queries Spotify for Liked Songs and playlist information.
- **YouTube Downloading**: Downloads audio tracks from YouTube based on Spotify playlist data. (Saved in 128kbps).
- **User Interface**: Simple UI for quick and easy use.
- **Intelligent File Management**:
  - Avoids duplication of downloaded files, even when on multiple playlists. Reduces need for reanalysing files. 
  - Organizing tracks by Spotify track and artist names. 
  - Stores Spotify track metadata, including album cover.
- **Serato and Rekordbox Compatibility**: Seamlessly sync playlists with Serato and Rekordbox. Always have your Spotify libary ready to DJ.
- **Multi-Track Processing**: Download and process multiple tracks at once for faster run times.
- **Configurable**: Users can manually override YouTube video sources.
- **Additional Platform Support**: *(Planned)* Future integration with SoundCloud and custom playlists.

## Installation

### Windows Mac Usage

1. Download the settings.yaml file [Here](https://github.com/Peter-SB/PySync-DJ/blob/main/settings.yaml).
2. Download the executable for the operating system you need from the [Actions Tab](https://github.com/Peter-SB/PySync-DJ/actions). Select the latest run, scroll down to Artifacts. Then download for your OS. 
3. Put the two downloads (Settings.yaml and the program executable) in the same folder.
4. Run the program.

** **Warning Mac Build Experimental, May Not Work** ** 

### Python Usage
**Download**  
Ensure you have Python 3.12 installed. Clone the repository and install dependencies:
```bash
git clone github.com:Peter-SB/PySync-DJ.git
cd pysync_dj
pip install -r requirements.txt
```
**To Start**  
Run the program from the command line:

```bash
python pysync_dj_main.py
```

If the program pauses without doing anything for more than a few mins, you can always stop it and try again.

**Logs**  
Can be found in the `logs\` directory .


## Has The Wrong Video Been Downloaded? - Specify Custom Video URLs
Find a better video URL on youtube and put the video url inplace of the current file name in `id_to_video_map.json`. E.g:
```
    "5cRDn5aGMLvWsldoRmOOz0": "E:\\pysync_dj_tracks\\Sub Focus - Solar System.mp4",
```

to

```
    "5cRDn5aGMLvWsldoRmOOz0": "https://www.youtube.com/watch?v=TUebWv_QXCM",
```

## Configuration
Edit settings.py to configure Spotify API credentials and other settings.

```
spotify_client_id: "" # Google how to get this value
spotify_client_secret: ""
spotify_redirect_uri: "http://localhost:8888/callback" # leave as is

dj_library_directory: "E:\\" # Directory of your usb and program output
tracks_folder: "Pysync_d DJ Tracks" # Folder name for location of saved audio files
serato_subcrate_dir: "_Serato_\\Subcrates" # Location of your serato subcrates
rekordbox_playlist_folder: "Rekordbox Playlist Import Files" # Folder name for location of saved rekordbox m3u files

download_liked_songs: true # Should download users liked songs? (true/false)
liked_songs_track_limit: null  # How many of your liked songs to download (integer)
liked_songs_date_limit: 27-08-23 # Date to download back to (DD-MM-YYYY)

playlists_to_download:
  PLaylist1: "2rBDG7m5QcjM3OjHyorkMZ" # Can use either just playlist id
  Playlist2: "https://open.spotify.com/playlist/2rBDG7m5QcjM3OjHyorkMZ" # or full url
```
leave `liked_songs_track_limit` and `rekordbox_playlist_folder` as `null` to not use limit.



## Contributing
Contributions to PySync DJ are welcome. 

## Acknowledgements
Special thanks to the developers of the used libraries, especially Pytube but also including Spotipy and others listed in requirements.txt.

Thanks also to kerrickstaley for their parse_serato_crates.py code.

## ** Disclaimer ** 
This software, is developed solely for personal, non-commercial use. It is intended for research and skill development purposes only. Users must adhere to the following:

1. Compliance: Use PySync DJ in accordance with Spotify's and YouTube's Terms of Service. 
2. Non-commercial Use: PySync DJ is strictly for non-commercial, educational purposes.
3. No Liability: The developer is not liable for misuse of PySync DJ or violations of any terms of service.
4. User Responsibility: Users are responsible for their actions and any consequences while using PySync DJ.

This disclaimer is subject to change. Users are responsible for complying with current terms of all involved platforms.


