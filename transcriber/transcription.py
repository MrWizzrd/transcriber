import os
from openai import OpenAI
from .file_utils import print_progress
from .audio_processing import split_audio

def transcribe_audio_chunk(client, chunk_path):
    with open(chunk_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
    return transcript.text

def transcribe_audio(audio_path):
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    client = OpenAI(api_key=api_key)
    try:
        print_progress(f"Transcribing audio: {os.path.basename(audio_path)}")
        chunks = split_audio(audio_path)
        transcripts = []
        for i, chunk in enumerate(chunks):
            print_progress(f"Transcribing chunk {i+1} of {len(chunks)}")
            transcript = transcribe_audio_chunk(client, chunk)
            transcripts.append(transcript)
            os.remove(chunk)  # Remove the chunk after transcription
        full_transcript = " ".join(transcripts)
        print_progress("Transcription completed successfully")
        return full_transcript
    except Exception as e:
        print(f"Error transcribing audio: {str(e)}")
        raise
    finally:
        for chunk in chunks:
            if os.path.exists(chunk):
                os.remove(chunk)