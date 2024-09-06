# Transcriber: Video/Audio to Text Transcription and Refinement Tool

Transcriber is a powerful CLI tool that converts video and audio files to text transcriptions using FFmpeg and OpenAI's Whisper API. It can process single video/audio files or entire directories, and optionally refine the transcriptions using AI models like Claude or OpenRouter.

## Features

- Convert video/audio to text transcriptions using OpenAI's Whisper API
- Process single video/audio files or entire directories
- Refine transcriptions using AI models (Claude or OpenRouter) with custom instructions
- Handle large files by splitting them into chunks
- Respect API rate limits and token limits
- Configurable settings via YAML file
- Progress tracking for long-running operations
- Detailed logging and error handling
- Support for processing existing markdown files through refinement

## Prerequisites

- Python 3.11+
- FFmpeg installed and accessible in your system PATH
- OpenAI API key
- Anthropic API key (for Claude refinement)
- OpenRouter API key (optional, for OpenRouter refinement)
- Poetry (for package management)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/transcriber.git
   cd transcriber
   ```

2. Install dependencies using Poetry:
   ```
   poetry install
   ```

3. Set up your API keys:
   - Create a `.env` file in the project root
   - Add your API keys:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     ANTHROPIC_API_KEY=your_anthropic_api_key_here
     OPENROUTER_API_KEY=your_openrouter_api_key_here
     ```

4. Configure the `config.yaml` file with your desired settings.

## Usage

Basic usage:
