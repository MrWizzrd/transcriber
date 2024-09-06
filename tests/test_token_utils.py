import pytest
from transcriber.token_utils import count_tokens, split_into_chunks

def test_count_tokens():
    text = "Hello, world!"
    assert count_tokens(text) > 0

def test_split_into_chunks():
    text = "This is a long text that should be split into multiple chunks. " * 10
    max_tokens = 20
    chunks = split_into_chunks(text, max_tokens)
    assert len(chunks) > 1
    for chunk in chunks:
        assert count_tokens(chunk) <= max_tokens