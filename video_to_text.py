import argparse
import subprocess
import os
import sys
from openai import OpenAI
import shlex
import re
from pydub import AudioSegment
from whisper.transcribe import Transcriber

def print_stage(message):
    print(f"\n=== {message} ===")

def print_progress(message):
    print(f"  > {message}")

def convert_video_to_audio(video_path, audio_path):
    try:
        print_progress(f"Converting video to audio: {os.path.basename(video_path)}")
        command = f"ffmpeg -i {shlex.quote(video_path)} -vn -acodec pcm_s16le -ar 44100 -ac 2 {shlex.quote(audio_path)}"
        subprocess.run(command, shell=True, check=True, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL)
        print_progress("Conversion completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error converting video to audio: {e.stderr.decode()}")
        raise

def split_audio(audio_path, chunk_length_ms=60000):
    print_progress("Splitting audio into chunks")
    audio = AudioSegment.from_wav(audio_path)
    chunks = []
    for i, chunk in enumerate(audio[::chunk_length_ms]):
        chunk_name = f"{audio_path}_chunk_{i}.wav"
        chunk.export(chunk_name, format="wav")
        chunks.append(chunk_name)
    return chunks

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

def process_file(video_path, output_dir):
    print_stage(f"Processing file: {os.path.basename(video_path)}")
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    safe_base_name = re.sub(r'[^\w\-_\. ]', '_', base_name)
    audio_path = os.path.join(output_dir, f"{safe_base_name}_audio.wav")
    markdown_path = os.path.join(output_dir, f"{safe_base_name}.md")

    try:
        convert_video_to_audio(video_path, audio_path)
        transcript = transcribe_audio(audio_path)
        
        print_progress(f"Saving transcription to: {markdown_path}")
        with open(markdown_path, "w") as f:
            f.write(f"# Transcription: {base_name}\n\n")
            f.write(transcript)
        
        print_progress("Transcription saved successfully")
    except Exception as e:
        print(f"Error processing {video_path}: {str(e)}")
    finally:
        if os.path.exists(audio_path):
            print_progress(f"Removing temporary audio file: {audio_path}")
            os.remove(audio_path)

def process_directory(input_dir, output_dir):
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']
    video_files = [f for f in os.listdir(input_dir) if any(f.lower().endswith(ext) for ext in video_extensions)]
    total_files = len(video_files)
    
    print_stage(f"Processing directory: {input_dir}")
    print_progress(f"Found {total_files} video files")

    for index, filename in enumerate(video_files, start=1):
        print_stage(f"Processing file {index} of {total_files}")
        video_path = os.path.join(input_dir, filename)
        process_file(video_path, output_dir)

def main():
    parser = argparse.ArgumentParser(
        description="Convert video to text using FFmpeg and OpenAI Whisper",
        epilog="Example usage:\n"
               "  Single file: %(prog)s input_video.mp4 output_transcript.md\n"
               "  Directory:   %(prog)s /path/to/video/directory /path/to/output/directory",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("input", help="Path to the input video file or directory")
    parser.add_argument("output", help="Path to save the output markdown file or directory")
    
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input path '{args.input}' does not exist.")
        sys.exit(1)

    if os.path.isdir(args.input):
        if not os.path.exists(args.output):
            os.makedirs(args.output)
        process_directory(args.input, args.output)
    else:
        output_dir = os.path.dirname(args.output) if os.path.dirname(args.output) else '.'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        if not args.output.lower().endswith('.md'):
            args.output += '.md'
        process_file(args.input, output_dir)

    print_stage("Processing completed")

if __name__ == "__main__":
    transcriber = Transcriber()
    transcriber.transcribe()