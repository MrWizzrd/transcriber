import logging
import sys
import os  # Add this import
from pathlib import Path
import click
from tqdm import tqdm
from colorama import init, Fore, Style
import asyncio
from dotenv import load_dotenv
from .refinement_processing import process_with_refinement, process_multiple_files
from .audio_processing import process_audio_file

from .config import Config
from .file_handler import FileHandler
from .video_processing import process_file
from .exceptions import TranscriberError, APIKeyError
from .api_utils import test_openai_api_key, test_anthropic_api_key, test_openrouter_api_key, test_api_keys

init(autoreset=True)  # Initialize colorama

# Load environment variables from .env file
load_dotenv()

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': Fore.BLUE,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        log_message = super().format(record)
        return f"{self.COLORS.get(record.levelname, '')}{log_message}{Style.RESET_ALL}"

def setup_logging(verbose):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if verbose else logging.WARNING)
    
    handler = logging.StreamHandler()
    handler.setFormatter(ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

async def async_main(input_path: Path, output_path: Path, output_dir: Path, instructions_path: Path, config: Config, verbose: bool):
    """
    Main asynchronous function to process input files or directories.

    Args:
        input_path (Path): Path to the input file or directory.
        output_path (Path): Path to save the output file.
        output_dir (Path): Directory to save all output files.
        instructions_path (Path): Path to the instructions file for refinement.
        config (Config): Configuration object.
        verbose (bool): Whether to print verbose output.

    This function handles different types of inputs (directory, audio file, video file, or markdown file)
    and processes them accordingly, including transcription and optional refinement.
    """
    if input_path.is_dir():
        input_files = FileHandler.list_media_files(input_path) + list(input_path.glob('*.md'))  # Include .md files
        total_files = len(input_files)
        if not verbose:
            print(f"Processing {total_files} files...")
        with tqdm(total=total_files, disable=verbose) as pbar:
            await process_multiple_files(input_files, output_dir, instructions_path, config, pbar)
    elif input_path.suffix.lower() in ['.mp3', '.wav']:
        if not verbose:
            print(f"Processing audio file: {input_path.name}")
        transcript_path = process_audio_file(input_path, output_dir)
        if instructions_path:
            if not verbose:
                print("Refining transcript with AI...")
            await process_with_refinement(transcript_path, output_path, instructions_path, config)
    else:
        if input_path.suffix.lower() == '.md':
            if not verbose:
                print(f"Refining transcript: {input_path.name}")
            await process_with_refinement(input_path, output_path, instructions_path, config)
        else:
            if not verbose:
                print(f"Processing video file: {input_path.name}")
            transcript_path = process_file(input_path, output_dir)
            if instructions_path:
                if not verbose:
                    print("Refining transcript with AI...")
                await process_with_refinement(transcript_path, output_path, instructions_path, config)

@click.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.option('--output', help="Path to save the output markdown file (optional)")
@click.option('--output-dir', help="Directory to save all output files (optional)")
@click.option('--instructions', help="Name of the instructions file in the 'instructions' folder, or full path to a custom instructions file")
@click.option('--verbose', is_flag=True, help="Print detailed log messages")
def main(input_path: str, output: str, output_dir: str, instructions: str, verbose: bool):
    """
    CLI entry point for the transcriber tool.

    This function sets up the environment, loads configuration, and initiates the processing
    of input files or directories. It handles command-line arguments and options, sets up logging,
    and manages error handling and reporting.

    Args:
        input_path (str): Path to the input file or directory.
        output (str): Path to save the output markdown file (optional).
        output_dir (str): Directory to save all output files (optional).
        instructions (str): Name of the instructions file or path to a custom instructions file.
        verbose (bool): Whether to print verbose output.
    """
    setup_logging(verbose)
    
    try:
        config = Config.from_file(Path('config.yaml'))
        
        # Set the API keys
        os.environ['OPENAI_API_KEY'] = config.openai_api_key
        os.environ['ANTHROPIC_API_KEY'] = config.anthropic_api_key
        os.environ['OPENROUTER_API_KEY'] = config.openrouter_api_key
        
        # Test API keys
        test_api_keys(config)
        
        input_path = Path(input_path)
        
        if instructions:
            instructions_path = Path(instructions) if Path(instructions).is_absolute() else config.instructions_dir / instructions
            if not instructions_path.exists():
                raise TranscriberError(f"Instructions file '{instructions_path}' does not exist.")
        else:
            instructions_path = None

        if output_dir:
            output_dir = Path(output_dir)
        else:
            output_dir = config.output_dir

        if output:
            output_path = Path(output)
        else:
            output_path = output_dir / f"{input_path.stem}_processed.md" if instructions_path else output_dir / f"{input_path.stem}.md"

        FileHandler.ensure_dir(output_dir)

        asyncio.run(async_main(input_path, output_path, output_dir, instructions_path, config, verbose))

        print(f"{Fore.GREEN}Processing completed. Output saved to: {output_path}{Style.RESET_ALL}")

    except APIKeyError as e:
        print(f"{Fore.RED}API Key Error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)
    except TranscriberError as e:
        print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        if verbose:
            logging.exception("An unexpected error occurred:")
        else:
            print(f"{Fore.RED}An error occurred: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    main()