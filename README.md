# Transcriber: Video to Text Transcription and Refinement Tool

This CLI tool converts video files to text transcriptions using FFmpeg and OpenAI's Whisper API. It can process either a single video file or a directory containing multiple video files. The transcriptions are saved in Markdown format. Additionally, it can refine existing transcriptions using the Claude API.

## Prerequisites

- Python 3.11+
- FFmpeg installed and accessible in your system PATH
- OpenAI API key
- Anthropic API key (for Claude refinement)
- Poetry (for package management)

## Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd transcriber
   ```

2. Install dependencies using Poetry:
   ```
   poetry install
   ```

3. Ensure FFmpeg is installed on your system and accessible via the command line.

## Usage

1. Set your API keys as environment variables:
   ```
   export OPENAI_API_KEY=your_openai_api_key_here
   export ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

2. Run the tool using Poetry:

   ```
   poetry run transcriber [options] <input> <output>
   ```

### Command-line Options

Here's the output of `transcriber --help`:
