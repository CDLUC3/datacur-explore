import yaml
import os
if os.getenv('COLAB_RELEASE_TAG'):
    IN_COLAB = True
else:
    IN_COLAB = False

KEYS = ['openai_api_key', 'google_project', 'google_location', 'google_api_key', 'dryad_api_key', 'dryad_secret']

if not IN_COLAB:
    # Get the directory of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to config.yaml
    config_path = os.path.join(current_dir, 'config.yaml')

    with open(config_path, 'r') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
else:
    config = {}
    import google.colab.userdata as userdata
    for item in KEYS:
        config[item] = userdata.get(item)


def get(key):
    try:
        return config[key]
    except Exception as e:
        print(f"Error getting {key}: {e}")
        return None


# this is mostly just for setting and short-term peristing the dryad api token
def set(key, value):
    config[key] = value
