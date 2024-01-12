# Release Notes

---

## Release 1.1 - Save As MP3 

This update introduces MP4 to MP3 conversion after the audio files are downloaded. This is because CDJs can read MP4 files. The files are converted with python library moviepy. 
The settings file was also updated (and the spotify client secret refreshed) for security and readability. 

### Features

 - Files are now converted to MP3 (from MP4) after downloading.
 - Settings file update for GitHub.

### Breaking Changes

 - Track comments with song popularity (metadata from spotify) now not saving.
