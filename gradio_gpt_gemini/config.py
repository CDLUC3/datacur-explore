import yaml
import os
if os.getenv('COLAB_RELEASE_TAG'):
    IN_COLAB = True
else:
    IN_COLAB = False

if not IN_COLAB:
    with open("config.yaml", 'r') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
else:
    config = {}
    import google.colab.userdata as userdata
    attributes = dir(userdata)
    for item in userdata:
        config[item] = userdata.get(item)


def get(key):
    try:
        return config[key]
    except Exception as e:
        print(f"Error getting {key}: {e}")
        return None
