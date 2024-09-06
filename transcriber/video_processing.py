import logging
from pathlib import Path
from .file_handler import FileHandler
from .audio_processing import convert_video_to_audio
from .transcription import transcribe_audio
from .exceptions import VideoProcessingError
from .token_utils import count_tokens
from .refinement_processing import process_with_refinement  # Update this import

def process_file(video_path: Path, output_dir: Path) -> Path:
    """
    Process a single video file: convert to audio, transcribe, and save the transcript.

    Args:
        video_path (Path): Path to the input video file.
        output_dir (Path): Directory to save the output files.

    Returns:
        Path: Path to the saved transcript file.

    Raises:
        VideoProcessingError: If there's an error during video processing.
    """
    logging.info(f"Processing file: {video_path.name}")
    safe_base_name = FileHandler.safe_filename(video_path.stem)
    audio_path = output_dir / f"{safe_base_name}_audio.wav"
    transcript_path = output_dir / f"{safe_base_name}.md"

    try:
        convert_video_to_audio(video_path, audio_path)
        transcript = transcribe_audio(audio_path)
        
        total_tokens = count_tokens(transcript)
        logging.info(f"Saving transcription to: {transcript_path}")
        logging.info(f"Total tokens in transcription: {total_tokens}")
        
        FileHandler.write_file(transcript_path, f"# Transcription: {video_path.name}\n\n{transcript}")
        
        logging.info("Transcription saved successfully")
        return transcript_path
    except Exception as e:
        raise VideoProcessingError(f"Error processing {video_path}: {str(e)}")
    finally:
        if audio_path.exists():
            logging.info(f"Removing temporary audio file: {audio_path}")
            audio_path.unlink()

def process_directory(input_dir: Path, output_dir: Path, config: 'Config'):
    """
    Process all video files in a directory.

    This function finds all video files in the input directory, processes each one,
    and optionally applies refinement if instructions are provided.

    Args:
        input_dir (Path): Path to the input directory containing video files.
        output_dir (Path): Directory to save all output files.
        config (Config): Configuration object containing processing settings.

    Raises:
        VideoProcessingError: If there's an error during video processing.
    """
    from .claude_processing import process_with_claude  # Move this import here

    video_files = FileHandler.list_video_files(input_dir)
    logging.info(f"Found {len(video_files)} video files")

    for video_path in video_files:
        transcript_path = process_file(video_path, output_dir)
        if transcript_path and config.instructions_path:
            refined_path = output_dir / f"{video_path.stem}_refined.md"
            logging.info(f"Refining transcript with AI")
            process_with_refinement(transcript_path, refined_path, config.instructions_path, config)