import os
import app.config as config

# Get the absolute path of the app directory
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_app_path(*subpaths):
    """Constructs a path relative to the app directory."""
    return os.path.join(APP_DIR, *subpaths)

def get_profile_path(profile_name):
    """Constructs a path for a profile file, handling Colab vs Local."""
    if config.IN_COLAB:
        # Use Google Drive in Colab
        drive_path = '/content/drive/MyDrive/datacur-explore/prompt_profiles'
        if not os.path.exists(drive_path):
             # Attempt to create the directory if it doesn't exist, though mounting usually handles this
             # This assumes the user has mounted drive at /content/drive
             try:
                 os.makedirs(drive_path, exist_ok=True)
             except OSError:
                 # Fallback or error handling if drive isn't mounted/writable
                 pass
        return os.path.join(drive_path, f'{profile_name}.json')
    else:
        # Use local file system
        return get_app_path('prompt_profiles', f'{profile_name}.json')

def list_profile_files():
    """Lists profile files from the appropriate location."""
    if config.IN_COLAB:
        drive_path = '/content/drive/MyDrive/datacur-explore/prompt_profiles'
        if os.path.exists(drive_path):
             return [f for f in os.listdir(drive_path) if f.endswith('.json')]
        else:
             return []
    else:
        profile_dir = get_app_path('prompt_profiles')
        if os.path.exists(profile_dir):
            return [f for f in os.listdir(profile_dir) if f.endswith('.json')]
        else:
            return []
