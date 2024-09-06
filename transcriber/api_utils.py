import os
from openai import OpenAI
from anthropic import Anthropic
from .exceptions import APIKeyError

def test_openai_api_key():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise APIKeyError("OpenAI API key is not set in the environment variables.")
    
    client = OpenAI(api_key=api_key)
    try:
        # Make a simple API call to test the key
        client.models.list()
    except Exception as e:
        raise APIKeyError(f"Error testing OpenAI API key: {str(e)}")

def test_anthropic_api_key():
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        raise APIKeyError("Anthropic API key is not set in the environment variables.")
    
    client = Anthropic(api_key=api_key)
    try:
        # Make a simple API call to test the key
        client.completions.create(
            model="claude-2.1",
            max_tokens_to_sample=1,
            prompt="Human: Test\n\nAssistant: This is a test."
        )
    except Exception as e:
        raise APIKeyError(f"Error testing Anthropic API key: {str(e)}")

def test_openrouter_api_key():
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        raise APIKeyError("OpenRouter API key is not set in the environment variables.")
    
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    try:
        # Make a simple API call to test the key
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[{"role": "user", "content": "This is a test."}],
            max_tokens=5,
        )
        # Check if the response is valid
        if not response.choices or not response.choices[0].message.content:
            raise APIKeyError("Invalid response from OpenRouter API")
    except Exception as e:
        raise APIKeyError(f"Error testing OpenRouter API key: {str(e)}")

def test_api_keys(config):
    if config.use_openrouter:
        test_openrouter_api_key()
    else:
        test_openai_api_key()
        test_anthropic_api_key()