import yaml
import os

# Initialize config dictionary
config = {}

KEYS = ['openai_api_key', 'google_project', 'google_location', 'google_api_key', 'dryad_api_key', 'dryad_secret',
        'user_agent']

# Check if running in Colab
if os.getenv('COLAB_RELEASE_TAG'):
    IN_COLAB = True
else:
    IN_COLAB = False

if not IN_COLAB:
    # Local environment: Load from config.yaml
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, 'config.yaml')

    if os.path.exists(config_path):
        with open(config_path, 'r') as stream:
            try:
                loaded_config = yaml.safe_load(stream)
                if loaded_config:
                    config.update(loaded_config)
            except yaml.YAMLError as exc:
                print(f"Error loading YAML config: {exc}")
    else:
        print(f"Warning: {config_path} not found.")
else:
    # Colab environment: Load from userdata secrets or environment variables
    try:
        from google.colab import userdata
    except ImportError:
        userdata = None

    for item in KEYS:
        value = None
        # Try userdata first
        if userdata:
            try:
                value = userdata.get(item)
            except Exception:
                pass

        # If not found, try environment variables
        if value is None:
            value = os.getenv(item.upper())

        if value:
            config[item] = value
        else:
            print(f"Warning: Secret '{item}' not found.")


def get(key):
    return config.get(key)


# this is mostly just for setting and short-term peristing the dryad api token
def set(key, value):
    config[key] = value
