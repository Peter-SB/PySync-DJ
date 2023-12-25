from pathlib import Path

spotify_client_id = "87a07cc2f67449dea1033ac2edef323f"
spotify_client_secret = "ea63089c4a8c4e38862eacdaf2aefdfb"
spotify_redirect_uri = 'http://localhost:8888/callback'

dj_library_directory = Path("E:\\")
tracks_folder = "pysync_dj_tracks"

download_liked_songs = True  # Not working, keep False
liked_songs_limit = 100  # How many of your liked songs to download
playlists_to_download = {
    "Nfdnbs24": "2rBDG7m5QcjM3OjHyorkMZ",
    "Jazz n Bass": "6Ch7BrfAM6cTiiBtzONxZR",
    "Chill DnB": "1sbpRux2JYEvosuikC01AY",
    "Dnb24.1" : "7suQlwliFponAvWaKjyBxC"
}
