import logging
import asyncio
import os
from pathlib import Path
from openai import OpenAI
from anthropic import Anthropic
from .file_handler import FileHandler  # Add this import
from .config import Config
from .exceptions import RefinementProcessingError
from .token_utils import count_tokens, split_into_chunks

MAX_TOKENS_PER_REQUEST = 20000
REQUESTS_PER_MINUTE = 5
TOKENS_PER_DAY = 300000

async def process_with_refinement(input_path: Path, output_path: Path, instructions_path: Path, config: Config):
    """
    Process a single file with the refinement API.

    This function reads the input file, applies refinement instructions, and saves the refined output.

    Args:
        input_path (Path): Path to the input file to be refined.
        output_path (Path): Path to save the refined output.
        instructions_path (Path): Path to the file containing refinement instructions.
        config (Config): Configuration object containing API settings.

    Raises:
        RefinementProcessingError: If there's an error during the refinement process.
    """
    logging.info(f"Processing with Refinement API: {input_path.name}")
    
    if config.use_openrouter:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv('OPENROUTER_API_KEY'),
        )
        model = config.openrouter_claude_model
    else:
        client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        model = config.claude_model
    
    transcript = FileHandler.read_file(input_path)
    instructions = FileHandler.read_file(instructions_path)
    
    chunks = split_into_chunks(transcript, MAX_TOKENS_PER_REQUEST - count_tokens(instructions) - 200)  # 200 tokens buffer for prompts
    
    refined_chunks = []
    for i, chunk in enumerate(chunks):
        logging.info(f"Processing chunk {i+1} of {len(chunks)}")
        try:
            if config.use_openrouter:
                messages = [
                    {"role": "system", "content": instructions},
                    {"role": "user", "content": f"Here's a chunk of the transcript to refine:\n\n{chunk}\n\nPlease refine this chunk according to the instructions provided."}
                ]
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=config.max_tokens,
                    temperature=config.temperature,
                )
                refined_chunks.append(response.choices[0].message.content)
            else:
                response = client.completions.create(
                    model=model,
                    max_tokens_to_sample=config.max_tokens,
                    temperature=config.temperature,
                    prompt=f"{instructions}\n\nHuman: Here's a chunk of the transcript to refine:\n\n{chunk}\n\nPlease refine this chunk according to the instructions provided.\n\nAssistant:"
                )
                refined_chunks.append(response.completion)
            
            # Rate limiting
            if i < len(chunks) - 1:  # Don't wait after the last chunk
                await asyncio.sleep(60 / REQUESTS_PER_MINUTE)
        
        except Exception as e:
            logging.error(f"Error processing chunk {i+1} with Refinement API: {str(e)}")
            refined_chunks.append(chunk)  # Use original chunk if processing fails
    
    refined_transcript = "\n\n".join(refined_chunks)
    FileHandler.write_file(output_path, refined_transcript)
    
    logging.info(f"Refined transcript saved to: {output_path}")

async def process_multiple_files(input_files: list[Path], output_dir: Path, instructions_path: Path, config: Config, pbar=None):
    from .video_processing import process_file
    from .audio_processing import process_audio_file

    total_tokens = 0
    for input_file in input_files:
        output_path = output_dir / f"{input_file.stem}_refined.md"
        
        # Check if the output file already exists
        if output_path.exists():
            logging.info(f"Skipping {input_file.name} as it has already been processed.")
            if pbar:
                pbar.update(1)
            continue

        try:
            if input_file.suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']:
                transcript_path = process_file(input_file, output_dir)
            elif input_file.suffix.lower() in ['.mp3', '.wav']:
                transcript_path = process_audio_file(input_file, output_dir)
            elif input_file.suffix.lower() == '.md':
                transcript_path = input_file
            else:
                logging.warning(f"Unsupported file type: {input_file.name}. Skipping.")
                if pbar:
                    pbar.update(1)
                continue

            try:
                await process_with_refinement(transcript_path, output_path, instructions_path, config)
            except Exception as e:
                logging.error(f"Error processing {input_file.name} with refinement API: {str(e)}")
                # If refinement processing fails, copy the original transcript to the output
                FileHandler.write_file(output_path, FileHandler.read_file(transcript_path))
            
            # Count tokens processed
            file_content = FileHandler.read_file(output_path)
            file_tokens = count_tokens(file_content)
            total_tokens += file_tokens
            
            logging.info(f"Processed {file_tokens} tokens for {input_file.name}")
            
            if pbar:
                pbar.update(1)
            
            if total_tokens >= TOKENS_PER_DAY:
                logging.warning("Daily token limit reached. Stopping processing.")
                break
            
            # Wait to avoid hitting rate limits
            await asyncio.sleep(60 / REQUESTS_PER_MINUTE)
        
        except Exception as e:
            logging.error(f"Error processing file {input_file.name}: {str(e)}")
            # Continue to the next file

    logging.info(f"Processed a total of {total_tokens} tokens")