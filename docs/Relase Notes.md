# Release Notes

## 3.3 Release - Update PytubeFix and fix ordering error

Updated the Pytubefix version and fix bug where playlists were not in correct order. Playlist were wrong because of async behaviour.

## 3.2 Release - Swap Pytube For PytubeFix

Fixed broken Pytube by replacing with newer forked library PytubeFix. 

Also built a new dist & added code to allow running without guid.

## 3.1 Release - Windows Executable

Bundles a runnable exe for use by Windows users.

Bug Fix: Failing to create Itune Library.xml folder.

## 3.0 Release - UI

This update turns the console application into a guid app complete with download button, download drive selector, progress bar, and ui output log. It also adds Itune Music Library.xml export format for even simpler rekordbox integration. 

Custom TKinter was used to build a simple guid app that spawned a sub process to run the main download script. 

This update required a large refactor and the code base has grown to accommodate new ui classes as well as a class for handling the event queue and a new class for handling the itunes export.

### Event Queue

Because of the multiple subprocesses, a managed queue was the solution to allow logging and passing of ui updates across subprocesse’s memory separate spaces. The ui runs a function to check the queue periodically and read whether to log debug/info/error to the logger and ui log output, or to update the progress bar. 

### Clean Code, Comments, and Typing

As the size of the project grows and code is refactored, I'm focusing more on good code then obvious doc string. Typing also has the added benefit of helping the interpreter's intellisense and well named, single purpose function allow functionality to be implicitly understood. I still believe there is still a time and place for comments and docstrings where greater meaning or higher level concepts need explaining.

### iTunes Music Libary.xml

To better integrate with Rekordbox I reverse engineered the library.xml files that iTunes exports that can be read by rekordbox. This allows for quicker and more organised importing of your PySync DJ library. 

While not simple to reverse engineer, many fields saved in the .xml file by itunes were unnecessary, this change has greatly improved user experience in rekordbox.  



## 2.0 Release - Multiprocessing

### Features:
- Multiprocessing
- Some Reorganisation of the id_to_video_map
- Minor Bug Fixes


### Multiprocessing

I want to implement Multiprocessing to speed up the program allowing for multiple tracks to be downloaded and converted at once.

I started by thinking about a fan out producer consumer model. However because the querying of spotify is so quick I decided to not have this as a separate process.

I further diverted from a producer consumer model but not having a live queue, instead each of the processes are created with a specific track to process and are run and managed by a ProcessPoolExecutor from the concurrent futures library. 

The results of implementing this were impressive and exciting, reducing the processing time of a playlist by **over a half**!

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
