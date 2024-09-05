import os
from .file_utils import print_stage, print_progress, safe_filename
from .audio_processing import convert_video_to_audio
from .transcription import transcribe_audio
from .claude_processing import process_with_claude

def process_file(video_path, output_dir):
    print_stage(f"Processing file: {os.path.basename(video_path)}")
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    safe_base_name = safe_filename(base_name)
    audio_path = os.path.join(output_dir, f"{safe_base_name}_audio.wav")
    transcript_path = os.path.join(output_dir, f"{safe_base_name}.md")

    try:
        convert_video_to_audio(video_path, audio_path)
        transcript = transcribe_audio(audio_path)
        
        print_progress(f"Saving transcription to: {transcript_path}")
        with open(transcript_path, "w") as f:
            f.write(f"# Transcription: {base_name}\n\n")
            f.write(transcript)
        
        print_progress("Transcription saved successfully")
        return transcript_path
    except Exception as e:
        print(f"Error processing {video_path}: {str(e)}")
        return None
    finally:
        if os.path.exists(audio_path):
            print_progress(f"Removing temporary audio file: {audio_path}")
            os.remove(audio_path)

def process_directory(input_dir, output_dir, refine, instructions):
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']
    video_files = [f for f in os.listdir(input_dir) if any(f.lower().endswith(ext) for ext in video_extensions)]
    total_files = len(video_files)
    
    print_stage(f"Processing directory: {input_dir}")
    print_progress(f"Found {total_files} video files")

    for index, filename in enumerate(video_files, start=1):
        print_stage(f"Processing file {index} of {total_files}")
        video_path = os.path.join(input_dir, filename)
        transcript_path = process_file(video_path, output_dir)
        
        if refine and transcript_path:
            refined_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}_refined.md")
            print_stage(f"Refining transcript with Claude API")
            process_with_claude(transcript_path, refined_path, instructions)