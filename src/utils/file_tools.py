from pathlib import Path

def get_current_dir(file_path: str) -> Path:
    """Returns the absolute parent directory of the provided file path."""
    return Path(file_path).parent.resolve()
