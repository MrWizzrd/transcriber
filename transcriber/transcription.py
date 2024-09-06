import os
from openai import OpenAI
from .token_utils import count_tokens
import logging

MAX_TOKENS_PER_REQUEST = 4096  # Adjust this based on the Whisper model's limit

def transcribe_audio_chunk(client, chunk_path):
    """
    Transcribe a single audio chunk using the OpenAI API.

    Args:
        client: The OpenAI client object.
        chunk_path: Path to the audio chunk file.

    Returns:
        str: The transcribed text for the audio chunk.
    """
    with open(chunk_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
    return transcript.text

def transcribe_audio(audio_path):
    """
    Transcribe an entire audio file by splitting it into chunks and transcribing each chunk.

    Args:
        audio_path: Path to the audio file to transcribe.

    Returns:
        str: The full transcription of the audio file.

    Raises:
        ValueError: If the OpenAI API key is not set.
        Exception: If there's an error during transcription.
    """
    from .audio_processing import split_audio  # Move this import here to avoid circular import

    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    client = OpenAI(api_key=api_key)
    try:
        logging.info(f"Transcribing audio: {os.path.basename(audio_path)}")
        chunks = split_audio(audio_path)
        transcripts = []
        total_tokens = 0
        
        for i, chunk in enumerate(chunks):
            logging.info(f"Transcribing chunk {i+1} of {len(chunks)}")
            transcript = transcribe_audio_chunk(client, chunk)
            
            chunk_tokens = count_tokens(transcript)
            total_tokens += chunk_tokens
            logging.info(f"Chunk {i+1} tokens: {chunk_tokens}")
            
            transcripts.append(transcript)
            os.remove(chunk)  # Remove the chunk after transcription
        
        full_transcript = " ".join(transcripts)
        logging.info(f"Transcription completed successfully. Total tokens: {total_tokens}")
        return full_transcript
    except Exception as e:
        logging.error(f"Error transcribing audio: {str(e)}")
        raise
    finally:
        for chunk in chunks:
            if os.path.exists(chunk):
                os.remove(chunk)