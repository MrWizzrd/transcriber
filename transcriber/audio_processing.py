import logging
import subprocess
import shlex
from pathlib import Path
from pydub import AudioSegment
from .exceptions import VideoProcessingError
from .file_handler import FileHandler

def convert_video_to_audio(video_path: Path, audio_path: Path):
    """
    Convert a video file to an audio file using FFmpeg.

    Args:
        video_path (Path): Path to the input video file.
        audio_path (Path): Path to save the output audio file.

    Raises:
        VideoProcessingError: If there's an error during the conversion process.
    """
    try:
        logging.info(f"Converting video to audio: {video_path.name}")
        command = f"ffmpeg -i {shlex.quote(str(video_path))} -vn -acodec pcm_s16le -ar 44100 -ac 2 {shlex.quote(str(audio_path))}"
        subprocess.run(command, shell=True, check=True, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL)
        logging.info("Conversion completed successfully")
    except subprocess.CalledProcessError as e:
        raise VideoProcessingError(f"Error converting video to audio: {e.stderr.decode()}")

def split_audio(audio_path: Path, chunk_length_ms: int = 60000):
    """
    Split an audio file into chunks of specified length.

    Args:
        audio_path (Path): Path to the input audio file.
        chunk_length_ms (int): Length of each chunk in milliseconds. Default is 60000 (1 minute).

    Returns:
        list: A list of paths to the created audio chunks.
    """
    logging.info("Splitting audio into chunks")
    audio = AudioSegment.from_wav(str(audio_path))
    chunks = []
    for i, chunk in enumerate(audio[::chunk_length_ms]):
        chunk_name = f"{audio_path}_chunk_{i}.wav"
        chunk.export(chunk_name, format="wav")
        chunks.append(chunk_name)
    return chunks

def process_audio_file(audio_path: Path, output_dir: Path) -> Path:
    """
    Process an audio file by transcribing it and saving the transcription.

    Args:
        audio_path (Path): Path to the input audio file.
        output_dir (Path): Directory to save the output transcription.

    Returns:
        Path: Path to the saved transcription file.

    Raises:
        VideoProcessingError: If there's an error during audio processing.
    """
    from .transcription import transcribe_audio  # Move this import here to avoid circular import

    logging.info(f"Processing audio file: {audio_path.name}")
    safe_base_name = FileHandler.safe_filename(audio_path.stem)
    transcript_path = output_dir / f"{safe_base_name}.md"

    try:
        transcript = transcribe_audio(audio_path)
        
        logging.info(f"Saving transcription to: {transcript_path}")
        FileHandler.write_file(transcript_path, f"# Transcription: {audio_path.name}\n\n{transcript}")
        
        logging.info("Transcription saved successfully")
        return transcript_path
    except Exception as e:
        raise VideoProcessingError(f"Error processing {audio_path}: {str(e)}")