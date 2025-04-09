# utils.py
import os
import json
from itertools import accumulate

import repo_factory
import file_reading_util
import open_api_code
import google_api_code
import time
import gradio as gr
import pdb
import bedrock_llama
import frictionless_util
import cProfile
import pstats
from io import StringIO


# the following is to enable refactoring and testing before combining three applications into one and have them
# share the same code base.

# use the following like this:
# Import the module
# mod = import_module_from_path("../other_dir1/other_dir2/library_code.py")

# Use its contents
# mod.my_function()
def import_module_from_path(path_str, module_name=None):
    """
    Import a Python module from a file path.

    Args:
        path_str (str or Path): Path to the .py file
        module_name (str, optional): Name to give the module (defaults to filename)

    Returns:
        module: The imported module object
    """
    path = Path(path_str).resolve()
    if not path.exists():
        raise FileNotFoundError(f"No file found at {path}")
    if not path.suffix == ".py":
        raise ValueError("Path must point to a .py file")

    if module_name is None:
        module_name = path.stem  # fallback to the filename (without .py)

    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec for {module_name} from {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def load_profile(profile_name):
    try:
        with open(f"prompt_profiles/{profile_name}.json", 'r') as f:
            profile = json.load(f)
        return profile['system_info'], profile['user_prompt']
    except Exception as e:
        print(f"Error loading profile {profile_name}: {e}")
        return "", ""


def delete_profile(profile_name):
    try:
        os.remove(f"prompt_profiles/{profile_name}.json")
        return f"Profile {profile_name} deleted.", list_profiles()
    except Exception as e:
        print(f"Error deleting profile {profile_name}: {e}")
        return f"Error deleting profile {profile_name}: {e}", list_profiles()

# status_output, profile_input
def save_profile_action(profile_name, system_info, user_prompt):
    if profile_name is None:
        return "Profile name is required", list_profiles()
    if profile_name.endswith('.json'):
        profile_name = profile_name[:-5]
    try:
        profile = {
            "system_info": system_info,
            "user_prompt": user_prompt
        }
        with open(f"prompt_profiles/{profile_name}.json", 'w') as f:
            json.dump(profile, f)
        return (f"Profile {profile_name} saved.",
                gr.Dropdown(label="Load profile name", choices=list_profiles(), value=profile_name))
    except Exception as e:
        print(f"Error saving profile {profile_name}: {e}")
        return f"Error saving profile {profile_name}: {e}", list_profiles()

# this is a bit confusing since we are yielding to outputs that update the gradio interface and there
# are three outputs because of quirks in how Gradio handles updates. I couldn't get it to update correctly unless
# I included both a markdown and a textbox representation of the same data.

# Inputs: file_chooser,
#   system_info -- the system conditioning text
#   user_prompt -- the text input by the user
#   llm_option -- "GPT-4o", "Gemini-1.5-flash-001", "llama3.1-70b"
#   input_method -- "Upload file" or "Dryad or Zenodo DOI"
#   doi_input -- the DOI textbox input for DOI
#   'choices' used to exist here and it was a dict of file names and URLs obtained from the Dryad or Zenodo DOI lookup
#       from checkboxes of files to process.  Instead, we now can just use all or a bunch of files that we can find as
#       inside of this function rather than being processed and chosen ahead of time.
# The three outputs it has to yield and update are textbox, markdown and status_output (in that order)
def process_file_and_return_markdown(file_chooser, system_info, user_prompt, llm_option,
                                     input_method, doi_input):


    file_paths = yield from file_reading_util.download_files(file_chooser, input_method, doi_input)

    # file_paths = file_reading_util.file_setup(input_method, file_chooser)
    if isinstance(file_paths, str):  # if it returns a string, it's an error message
        yield '', '', file_paths
        return

    accum = ''
    if doi_input and input_method == 'Dryad or Zenodo DOI':
        accum += f"# DOI: {doi_input}\n\n"

    file_context = ''
    for file_path in file_paths:
        file_content = file_reading_util.get_texty_content(file_path)
        file_context += f"## Filename: {os.path.basename(file_path)}\n\n{file_content}\n\n"

    yield accum, accum, "Starting LLM processing..."

    if llm_option == "GPT-4o":
        yield from open_api_code.generate_stream(file_context, system_info, user_prompt, accum)

        # note that return doesn't work right for final value. you need to yield it instead
        yield (gr.update(visible=False),
               gr.update(visible=True),
               'Done')
    elif llm_option == "gemini-2.0-flash":
        yield from google_api_code.generate(file_context, system_info, user_prompt, accum)

        # note that return doesn't work right for final value. you need to yield it instead
        yield (gr.update(visible=False),
                gr.update(visible=True),
                'Done')
    elif llm_option == "llama3.1-70b":
        yield from bedrock_llama.generate_stream(file_context, system_info, user_prompt, accum)

        # note that return doesn't work right for final value. you need to yield it instead
        yield (gr.update(visible=False),
                gr.update(visible=True),
                'Done')

    # remove the uploaded files
    for file_path in file_paths:
        os.remove(file_path)

def update_inputs(input_method):
    if input_method == "Upload file":
        return gr.update(visible=True), gr.update(visible=False)
    elif input_method == "Dryad or Zenodo DOI":
        return gr.update(visible=False), gr.update(visible=True)

# These are utility functions, and not Gradio handlers, I think
def update_textareas(profile_name):
    system_info, user_prompt = load_profile(profile_name)
    return system_info, user_prompt

def reload_profiles():
    return gr.update(choices=list_profiles())

def list_profiles():
    try:
        profiles = [f.split('.')[0] for f in os.listdir('prompt_profiles') if f.endswith('.json')]
        sorted_profiles = sorted(profiles, key=lambda s: s.lower())
        return ["[Select profile]"] + sorted_profiles
    except Exception as e:
        print(f"Error listing profiles: {e}")
        return ["[Select profile]"]


