import pytest
from unittest.mock import patch, MagicMock
from transcriber.transcription import transcribe_audio_chunk, transcribe_audio

@pytest.fixture
def mock_openai_client():
    with patch('transcriber.transcription.OpenAI') as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        yield mock_client

def test_transcribe_audio_chunk(mock_openai_client, tmp_path):
    mock_response = MagicMock()
    mock_response.text = "This is a test transcription."
    mock_openai_client.audio.transcriptions.create.return_value = mock_response

    test_audio = tmp_path / "test_audio.wav"
    test_audio.write_text("dummy audio content")

    result = transcribe_audio_chunk(mock_openai_client, test_audio)
    assert result == "This is a test transcription."

@patch('transcriber.transcription.os.environ.get')
@patch('transcriber.transcription.count_tokens')
def test_transcribe_audio(mock_count_tokens, mock_env_get, mock_openai_client, tmp_path):
    mock_env_get.return_value = "fake_api_key"
    mock_count_tokens.return_value = 10  # Mocking token count

    # Create dummy chunk files
    chunk_files = [tmp_path / f"chunk_{i}.wav" for i in range(3)]
    for chunk_file in chunk_files:
        chunk_file.write_text("dummy chunk content")

    # Mock the split_audio function
    mock_split_audio = MagicMock()
    mock_split_audio.return_value = [str(file) for file in chunk_files]
    
    # Patch the audio_processing module
    with patch('transcriber.audio_processing.split_audio', mock_split_audio):
        mock_response = MagicMock()
        mock_response.text = "Chunk transcription."
        mock_openai_client.audio.transcriptions.create.return_value = mock_response

        test_audio = tmp_path / "test_audio.wav"
        test_audio.write_text("dummy audio content")

        result = transcribe_audio(str(test_audio))
        expected_result = "Chunk transcription. " * 3
        expected_result = expected_result.strip()  # Remove trailing space
        assert result == expected_result

        # Verify that split_audio was called
        mock_split_audio.assert_called_once_with(str(test_audio))

        # Verify that count_tokens was called for each chunk
        assert mock_count_tokens.call_count == 3

    # Verify that chunk files have been deleted
    for chunk_file in chunk_files:
        assert not chunk_file.exists(), f"Chunk file {chunk_file} was not deleted"