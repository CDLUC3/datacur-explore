import os

# Get the absolute path of the app directory
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_app_path(*subpaths):
    """Constructs a path relative to the app directory."""
    return os.path.join(APP_DIR, *subpaths)