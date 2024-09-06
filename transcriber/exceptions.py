class TranscriberError(Exception):
    """Base exception class for all Transcriber-related errors."""

class VideoProcessingError(TranscriberError):
    """Exception raised when an error occurs during video processing."""

class ClaudeProcessingError(TranscriberError):
    """Exception raised when an error occurs during Claude API processing."""

class APIKeyError(TranscriberError):
    """Exception raised when there's an issue with API keys."""

class RefinementProcessingError(TranscriberError):
    """Exception raised when an error occurs during refinement processing."""