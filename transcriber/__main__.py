import argparse
import sys
import os
import traceback
from .video_processing import process_file
from .claude_processing import process_with_claude
from .file_utils import print_stage, print_progress

def main():
    parser = argparse.ArgumentParser(
        description="Convert video to text using FFmpeg and OpenAI Whisper, then optionally process with Claude API",
        epilog="Example usage:\n"
               "  Video to text: transcriber input_video.mp4\n"
               "  Refine existing file: transcriber input_transcript.md --instructions custom_prompt.md",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("input", help="Path to the input video file or existing transcript")
    parser.add_argument("--output", help="Path to save the output markdown file (optional)")
    parser.add_argument("--instructions", help="Name of the instructions file in the 'instructions' folder, or full path to a custom instructions file")
    parser.add_argument("--verbose", action="store_true", help="Print detailed error messages")
    
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input path '{args.input}' does not exist.")
        sys.exit(1)

    # Handle instructions file path
    if args.instructions:
        if not os.path.isabs(args.instructions):
            instructions_path = os.path.join('instructions', args.instructions)
            if not os.path.exists(instructions_path):
                print(f"Error: Instructions file '{instructions_path}' does not exist.")
                sys.exit(1)
        else:
            instructions_path = args.instructions
            if not os.path.exists(instructions_path):
                print(f"Error: Instructions file '{instructions_path}' does not exist.")
                sys.exit(1)
    else:
        instructions_path = None

    # Handle output file path
    if args.output:
        output_path = args.output
    else:
        input_basename = os.path.splitext(os.path.basename(args.input))[0]
        if instructions_path:
            output_path = os.path.join('processed', f"{input_basename}_processed.md")
        else:
            output_path = os.path.join('finished', f"{input_basename}.md")

    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        if args.input.lower().endswith('.md'):
            # Refining an existing transcript
            if instructions_path:
                process_with_claude(args.input, output_path, instructions_path)
            else:
                print("Error: Instructions are required to process an existing transcript.")
                sys.exit(1)
        else:
            # Processing a video file
            transcript_path = process_file(args.input, 'finished')
            if transcript_path and instructions_path:
                process_with_claude(transcript_path, output_path, instructions_path)

        print_stage("Processing completed")
        print_progress(f"Output saved to: {output_path}")
    except Exception as e:
        if args.verbose:
            print("An error occurred:")
            print(traceback.format_exc())
        else:
            print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()