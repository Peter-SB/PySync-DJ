# Release Notes


## 2.0 Release - Multiprocessing

### Features:
- Multiprocessing
- Some Reorganisation of the id_to_video_map
- Minor Bug Fixes


### Multiprocessing

I want to implement Multiprocessing to speed up the program allowing for multiple tracks to be downloaded and converted at once.

I started by thinking about a fan out producer consumer model. However because the querying of spotify is so quick I decided to not have this as a separate process.

I further diverted from a producer consumer model but not having a live queue, instead each of the processes are created with a specific track to process and are run and managed by a ProcessPoolExecutor from the concurrent.futures library. 

The results of implementing this were impressive and exciting, reducing the processing time of a playlist by over a half!

Considerations had to be made about asynchronous behaviour using the id_to_video_map in a thread safe way. I decided it would be best to have each of the processes have access to a shared multiprocessing.Manager dictionary to stop duplication of tracks and allow the uptodate id_to_video_map to be saved by the process in case the program was stopped midway. Here a lock was used to write to the saved dictionary file safely.

### Some Reorganisation of the id_to_video_map

There was some reorganisation of the id_to_video_map to firstly save it to the drive, not in the program directory so that if the user changes the drive, there is no confusion. Secondly the drive letter was removed from the id_to_video_map so that the file locations are not drive specific.



## Release 1.1 - Save As MP3 


This update introduces MP4 to MP3 conversion after the audio files are downloaded. This is because CDJs can read MP4 files. The files are converted with python library moviepy. 
The settings file was also updated (and the spotify client secret refreshed) for security and readability. 

### Features

 - Files are now converted to MP3 (from MP4) after downloading.
 - Settings file update for GitHub.

### Breaking Changes

 - Track comments with song popularity (metadata from spotify) now not saving.
