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
    # Colab environment: Load from userdata secrets
    try:
        from google.colab import userdata
        for item in KEYS:
            try:
                config[item] = userdata.get(item)
            except Exception as e:
                # Secret might be missing or not accessible
                print(f"Warning: Failed to retrieve secret '{item}': {e}")
    except ImportError:
        print("Error: google.colab module not found.")


def get(key):
    return config.get(key)


# this is mostly just for setting and short-term peristing the dryad api token
def set(key, value):
    config[key] = value
