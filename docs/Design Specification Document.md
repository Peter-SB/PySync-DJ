# PySync DJ: 1.0 Design Specification Document



## Introduction

Keeping music libraries organised across platforms and softwares is effort and hinders users ability to get started on mixing. PySync DJ is a Python-based program designed to stream line this process by synchronize Spotify playlists with DJ libraries, specifically Serato and Rekordbox. This document outlines the planning, design features, implementation phases, and the resolution of challenges encountered during the development of PySync DJ. It serves as a comprehensive guide demonstrating the project's lifecycle from conception to the final 1.0 product.


## Project Overview

- **Goal**: To create a Python program capable of syncing a Spotify library with a DJ library.
- **Functionality**: Users can select Spotify playlists to download as MP3 files, sourced from YouTube. Metadata from Spotify is added to the file info.
- **Storage Strategy**: Audio files are stored locally and a hashmap maps Spotify songs to YouTube videos for efficient file management to stop file duplication and increase runtimes.
- **Compatibility**: Ensures saved local playlists are compatible with both Serato and Rekordbox DJ software.



## Key Features and Specifications

- **Initial Command Line Interface**: The first version is command-line based, with plans for a UI upgrade.
- **Spotify API Integration**: Uses Spotipy to query Spotify for playlist information.
- **YouTube Downloading**: Uses Pytube to download audio files from YouTube. 
- **Data Management**: Manages data conversion to ensure compatibility with DJ software. Uses Pyrekordbox for Rekordbox and investigates other tools for Serato integration.
- **Video Selection** Users can select specific video URLs for any song 



## Planned Development Phases

1. Spotify playlist querying and playlist data storage.
2. Downloading YouTube videos for tracks. Store in the appropriate folder system.
3. Create appropriate key value paring system for relating serato tracks to youtube videos and mp3 files.
4. Conversioning downloaded YouTube content to MP3 format.
5. Develop a reading of these playlists with rekordbox and serato.
6. Clean up and additional features.

### Future Plans

 - Ui and bundled executable
 - Server Setup: Establish a server for managing libraries continuously.
 - Song Selection and Display: Create an algorithm for song selection from youtube and implement a user-friendly display.



## TDD, Iterative Development, and Software Practices 

- Utilised Test-Driven Development (TDD) to refine functions, such as extracting Spotify playlists from URLs.
- Iteratively improved the project, addressing edge cases and optimising performance.
- Adhere to SOLID principles where practical. 
- Multiprocessing tracks in a fan-out producer/consumer-like model. [Read more here](Relase%20Notes.md).



## GPT Assisted Workflow

GPT-4 was used as a tool for some of this to improve workflows. Speeding up planning, research, and development. While the idea for this has been brewing for a while I finally started by sitting down planning out the project, design phases, what libraries to use, what challenges I might face and how this would work in a notes app. Then GPT-4 took those notes and rewrote them in a more structured and refined way. 

GPT-4 Would also be used for code development to speed up tedious simple class and function writing. Just one less step than, for example, going to google and googling how to open a yaml file only to instantly forget after finding the answer on stack overflow.

I experimented with GPT TDD where I would tell it to create my function and unit tests associated with it. I would then edit the unit tests to include overlooked edge cases (the code was good but still simple so needed a lot of help). I would then feed the new test cases back to GPT and tell it to rewrite the function. This was only minorly experimented with though, more investigation needed. I do worry about overfitting. You'd need to be careful and have an understanding of edge cases or GPT could hypothetically just force the function to work for your unit tests instead of providing a clean solution. 

At no time did I feel that ChatGPT was giving me answers I couldn't have come up with myself, and without an understanding of the answers it gave I would have not been able to correct coding mistakes, fix bugs, and design overarching structures. GPT did however save me time and energy to be better spent elsewhere. Like auto complete or a calculator it is a tool to save you time on the less important parts and save you to think about the bigger picture.



## **1.0 Release Features**:

### Core Functionalities
- **Spotify Playlist Query**: Ability to query Spotify playlists and liked songs.
- **Direct Sync**: Playlists and liked songs are synced directly from the Spotify playlist. 
- **Limit on Liked Songs**: Liked songs feature a time and/or track limit. 

### YouTube Downloading
- **Audio File Download**: Audio files are downloaded from YouTube.
- **Search Criteria**: Artist and song name are used for searching.
- **Selection of Videos**: The first search result is downloaded as an MP4. 

### Data Management
- **File Storage**: Songs are saved in a collective audio files folder.
- **Metadata Addition**: Song data such as Name, Artist, and cover art are added to the audio file. 
- **Database Management**: Downloaded songs are kept in a database, allowing only one audio file per song, even when songs appear on multiple playlists. 
  - **Database Editability**: The database can be edited to change the YouTube source video. 

### DJ Software Integration
- **Serato Integration**: Serato crates are saved directly to your Serato file and will be available when Serato is loaded. 
- **Rekordbox Integration**: Rekordbox playlists are exported as a iTunes Library.xml and alternatively saved as `.m3u` files and are imported. 

### Configuration
- **Settings Management**: A `settings.yaml` file holds configuration settings. 

**Deadline**: 1.0 release 01/2024.



*End of Design Specification Document for PySync DJ*
