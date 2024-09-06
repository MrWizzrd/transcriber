import tiktoken

def count_tokens(text: str) -> int:
    """
    Count the number of tokens in a given text using the GPT-3 tokenizer.

    Args:
        text (str): The input text to tokenize.

    Returns:
        int: The number of tokens in the text.
    """
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    return len(encoding.encode(text))

def split_into_chunks(text: str, max_tokens: int) -> list[str]:
    """
    Split a text into chunks, each containing at most max_tokens.

    Args:
        text (str): The input text to split.
        max_tokens (int): The maximum number of tokens per chunk.

    Returns:
        list[str]: A list of text chunks.
    """
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    tokens = encoding.encode(text)
    chunks = []
    current_chunk = []

    for token in tokens:
        current_chunk.append(token)
        if len(current_chunk) >= max_tokens:
            chunks.append(encoding.decode(current_chunk))
            current_chunk = []

    if current_chunk:
        chunks.append(encoding.decode(current_chunk))

    return chunks