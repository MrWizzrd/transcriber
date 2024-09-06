import pytest
from pathlib import Path
from transcriber.config import Config

def test_config_from_file(tmp_path):
    config_content = """
    api_key: test_api_key
    output_dir: ./output
    instructions_dir: ./instructions
    default_model: claude-2.1
    max_tokens: 100000
    temperature: 0.5
    """
    config_file = tmp_path / "test_config.yaml"
    config_file.write_text(config_content)

    config = Config.from_file(config_file)
    assert config.api_key == "test_api_key"
    assert isinstance(config.output_dir, Path)
    assert isinstance(config.instructions_dir, Path)
    assert config.default_model == "claude-2.1"
    assert config.max_tokens == 100000
    assert config.temperature == 0.5