# Video to Text Transcription Tool

This CLI tool converts video files to text transcriptions using FFmpeg and OpenAI's Whisper API. It can process either a single video file or a directory containing multiple video files. The transcriptions are saved in Markdown format.

## Prerequisites

- Python 3.11+
- FFmpeg installed and accessible in your system PATH
- OpenAI API key
- Poetry (for package management)

## Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd video-to-text
   ```

2. Install dependencies using Poetry:
   ```
   poetry install
   ```

3. Ensure FFmpeg is installed on your system and accessible via the command line.

## Usage

1. Set your OpenAI API key as an environment variable:
   ```
   export OPENAI_API_KEY=your_api_key_here
   ```

2. Run the script using Poetry:

   For a single file:
   ```
   poetry run python video_to_text.py <input_video_path> <output_markdown_path>
   ```

   For a directory:
   ```
   poetry run python video_to_text.py <input_directory> <output_directory>
   ```

   Replace `<input_video_path>` with the path to your video file, `<input_directory>` with the path to your directory containing video files, `<output_markdown_path>` with the desired location for the transcription Markdown file, and `<output_directory>` with the desired directory for output files.

Examples:
