import argparse
import sys
import os
from .video_processing import process_file, process_directory
from .claude_processing import process_with_claude
from .file_utils import print_stage, print_progress

def main():
    parser = argparse.ArgumentParser(
        description="Convert video to text using FFmpeg and OpenAI Whisper, then optionally process with Claude API",
        epilog="Example usage:\n"
               "  Basic: transcriber input_video.mp4 output_transcript.md\n"
               "  With refinement: transcriber input_video.mp4 output_transcript.md --refine\n"
               "  Custom instructions: transcriber input_video.mp4 output_transcript.md --refine --instructions custom_prompt.md\n"
               "  Refine existing file: transcriber --refine existing_transcript.md --instructions custom_prompt.md",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("input", nargs='?', help="Path to the input video file or directory")
    parser.add_argument("output", nargs='?', help="Path to save the output markdown file or directory")
    parser.add_argument("--refine", action="store_true", help="Process the transcription with Claude API")
    parser.add_argument("--instructions", default="default_prompt.md", help="Path to the Claude instructions file")
    
    args = parser.parse_args()

    if args.refine and not args.output:
        # Refining an existing file
        if not args.input:
            print("Error: When refining an existing file, an input file path is required.")
            sys.exit(1)
        refine_existing_file(args.input, args.instructions)
    elif not args.input or not args.output:
        print("Error: Both input and output paths are required for video processing.")
        sys.exit(1)
    elif not os.path.exists(args.input):
        print(f"Error: Input path '{args.input}' does not exist.")
        sys.exit(1)
    elif os.path.isdir(args.input):
        if not os.path.exists(args.output):
            os.makedirs(args.output)
        process_directory(args.input, args.output, args.refine, args.instructions)
    else:
        output_dir = os.path.dirname(args.output) if os.path.dirname(args.output) else '.'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        if not args.output.lower().endswith('.md'):
            args.output += '.md'
        process_single_file(args.input, args.output, args.refine, args.instructions)

    print_stage("Processing completed")

def process_single_file(input_path, output_path, refine, instructions):
    transcript_path = process_file(input_path, os.path.dirname(output_path))
    
    if refine:
        print_stage(f"Refining transcript with Claude API")
        process_with_claude(transcript_path, output_path, instructions)
    else:
        print_progress(f"Transcription saved to: {transcript_path}")

def refine_existing_file(input_path, instructions):
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' does not exist.")
        sys.exit(1)
    
    output_path = os.path.splitext(input_path)[0] + "_refined.md"
    print_stage(f"Refining existing transcript with Claude API")
    process_with_claude(input_path, output_path, instructions)
    print_progress(f"Refined transcript saved to: {output_path}")

if __name__ == "__main__":
    main()