# How to Use Transcriber

Transcriber is a versatile CLI tool for converting video and audio files to text, transcribing audio, and refining transcriptions. This guide will walk you through the installation process and demonstrate various use cases.

## Installation

1. Ensure you have Python 3.11+ and FFmpeg installed on your system.

2. Clone the Transcriber repository:
   ```
   git clone https://github.com/yourusername/transcriber.git
   cd transcriber
   ```

3. Install dependencies using Poetry:
   ```
   poetry install
   ```

4. Set up your API keys:
   - Create a `.env` file in the project root
   - Add your API keys:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     ANTHROPIC_API_KEY=your_anthropic_api_key_here
     ```

5. Configure the `config.yaml` file with your desired settings.

## Basic Usage

### Transcribing a Video or Audio File

To transcribe a single video or audio file:
