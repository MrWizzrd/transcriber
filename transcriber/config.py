import os
import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class Config:
    openai_api_key: str
    anthropic_api_key: str
    openrouter_api_key: str
    use_openrouter: bool
    output_dir: Path
    instructions_dir: Path
    claude_model: str
    openrouter_claude_model: str
    max_tokens: int
    temperature: float

    @classmethod
    def from_file(cls, path: Path) -> 'Config':
        with path.open('r') as f:
            data = yaml.safe_load(f)
        # Convert string paths to Path objects
        data['output_dir'] = Path(data['output_dir'])
        data['instructions_dir'] = Path(data['instructions_dir'])
        
        # Load API keys from environment variables
        data['openai_api_key'] = os.getenv('OPENAI_API_KEY', data.get('openai_api_key', ''))
        data['anthropic_api_key'] = os.getenv('ANTHROPIC_API_KEY', data.get('anthropic_api_key', ''))
        data['openrouter_api_key'] = os.getenv('OPENROUTER_API_KEY', data.get('openrouter_api_key', ''))
        
        return cls(**data)