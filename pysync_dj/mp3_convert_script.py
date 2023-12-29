from moviepy.audio.io.AudioFileClip import AudioFileClip
import os
import sys


def convert_to_mp3(mp4_file: str) -> str:
    """
    Convert an MP4 file to MP3 format, delete the original MP4 file, and return the name of the MP3 file.

    :param mp4_file: The path to the MP4 file.
    :return: The path of the created MP3 file.
    """
    mp3_file = os.path.splitext(mp4_file)[0] + '.mp3'

    video_clip = AudioFileClip(mp4_file)
    video_clip.write_audiofile(mp3_file)
    video_clip.close()

    # Delete the original MP4 file
    os.remove(mp4_file)

    return mp3_file


if __name__ == "__main__":
    # Takes the MP4 file path from command line argument
    mp4_file_path = sys.argv[1]
    convert_to_mp3(mp4_file_path)
