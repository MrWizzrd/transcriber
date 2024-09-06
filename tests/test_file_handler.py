import pytest
from pathlib import Path
from transcriber.file_handler import FileHandler

def test_safe_filename():
    unsafe_name = "File with spaces and !@#$%^&*().mp4"
    safe_name = FileHandler.safe_filename(unsafe_name)
    assert " " not in safe_name
    assert all(c.isalnum() or c in "-_." for c in safe_name)

def test_ensure_dir(tmp_path):
    test_dir = tmp_path / "test_dir"
    FileHandler.ensure_dir(test_dir)
    assert test_dir.exists()
    assert test_dir.is_dir()

def test_write_and_read_file(tmp_path):
    test_file = tmp_path / "test_file.txt"
    content = "This is a test content."
    FileHandler.write_file(test_file, content)
    assert test_file.exists()
    read_content = FileHandler.read_file(test_file)
    assert read_content == content