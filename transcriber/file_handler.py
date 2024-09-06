from pathlib import Path
import logging
from typing import List
import re

class FileHandler:
    """A utility class for handling file operations in the Transcriber project."""

    @staticmethod
    def ensure_dir(path: Path) -> None:
        """
        Ensure that a directory exists, creating it if necessary.

        Args:
            path (Path): The directory path to ensure.
        """
        path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def read_file(path: Path) -> str:
        """
        Read the contents of a file.

        Args:
            path (Path): The path to the file to read.

        Returns:
            str: The contents of the file.

        Raises:
            IOError: If there's an error reading the file.
        """
        try:
            with path.open('r') as f:
                return f.read()
        except IOError as e:
            logging.error(f"Error reading file {path}: {e}")
            raise

    @staticmethod
    def write_file(path: Path, content: str) -> None:
        """
        Write content to a file.

        Args:
            path (Path): The path to the file to write.
            content (str): The content to write to the file.

        Raises:
            IOError: If there's an error writing to the file.
        """
        try:
            with path.open('w') as f:
                f.write(content)
        except IOError as e:
            logging.error(f"Error writing file {path}: {e}")
            raise

    @staticmethod
    def list_video_files(directory: Path) -> List[Path]:
        """
        List all video files in a directory.

        Args:
            directory (Path): The directory to search for video files.

        Returns:
            List[Path]: A list of paths to video files in the directory.
        """
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']
        return [f for f in directory.iterdir() if f.suffix.lower() in video_extensions]

    @staticmethod
    def safe_filename(filename: str) -> str:
        """
        Convert a filename to a safe version by removing invalid characters.

        Args:
            filename (str): The original filename.

        Returns:
            str: A safe version of the filename.
        """
        return re.sub(r'[^\w\-_\. ]', '', filename).replace(' ', '_')

    @staticmethod
    def list_audio_files(directory: Path) -> List[Path]:
        """
        List all audio files in a directory.

        Args:
            directory (Path): The directory to search for audio files.

        Returns:
            List[Path]: A list of paths to audio files in the directory.
        """
        audio_extensions = ['.mp3', '.wav']
        return [f for f in directory.iterdir() if f.suffix.lower() in audio_extensions]

    @staticmethod
    def list_media_files(directory: Path) -> List[Path]:
        """
        List all media files (video, audio, and markdown) in a directory.

        Args:
            directory (Path): The directory to search for media files.

        Returns:
            List[Path]: A list of paths to media files in the directory.
        """
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']
        audio_extensions = ['.mp3', '.wav']
        return [f for f in directory.iterdir() if f.suffix.lower() in video_extensions + audio_extensions or f.suffix.lower() == '.md']