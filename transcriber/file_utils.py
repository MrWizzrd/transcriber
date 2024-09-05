import re

def print_stage(message):
    print(f"\n=== {message} ===")

def print_progress(message):
    print(f"  > {message}")

def safe_filename(filename):
    return re.sub(r'[^\w\-_\. ]', '_', filename)