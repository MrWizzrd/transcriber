import os
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
from .file_utils import print_stage, print_progress

def process_with_claude(input_path, output_path, instructions_path):
    print_stage(f"Processing with Claude API: {os.path.basename(input_path)}")
    
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    
    client = Anthropic(api_key=api_key)
    
    with open(input_path, 'r') as f:
        transcript = f.read()
    
    with open(instructions_path, 'r') as f:
        instructions = f.read()
    
    print_progress("Sending request to Claude API")
    try:
        prompt = f"{HUMAN_PROMPT} Here are the instructions for refining the transcript:\n\n{instructions}\n\nHere's the transcript to refine:\n\n{transcript}\n\nPlease refine this transcript according to the instructions provided.{AI_PROMPT}"
        
        response = client.completions.create(
            model="claude-2.1",
            prompt=prompt,
            max_tokens_to_sample=100000,
            temperature=0.5,
        )
        
        refined_transcript = response.completion
        
        with open(output_path, 'w') as f:
            f.write(refined_transcript)
        
        print_progress(f"Refined transcript saved to: {output_path}")
    except Exception as e:
        print(f"Error processing with Claude API: {str(e)}")
        raise
