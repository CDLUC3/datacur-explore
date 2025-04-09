# utils.py
import os
import json
from itertools import accumulate

import repo_factory
import file_reading_util

import time
import gradio as gr
import pdb
import frictionless_util
import cProfile
import pstats
from io import StringIO

import importlib.util
import sys
from pathlib import Path

# from readme_gen.utils import import_module_from_path

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

# temporary imports for refactoring.  Sometime soon these should be all in one application instead of three
google_api_code = import_module_from_path('../many-stage/google_api_code.py')
open_api_code = import_module_from_path('../many-stage/open_api_code.py')
bedrock_llama = import_module_from_path('../many-stage/bedrock_llama.py')

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

def load_file_list(doi):
    if doi:
        doi = doi.strip()
    try:
        repo = repo_factory.repo_factory(doi)
    except ValueError as e:
        err = f"Error loading DOI: {e}"
        return gr.update(choices=[err], value=err, visible=True), [err]

    if not repo.id_exists():
        err = f"DOI {doi} not found."
        return gr.update(choices=[err], value=err, visible=True), [err]

    file_list = repo.get_filenames_and_links()
    choices = {key: value for item in file_list for key, value in item.items()}
    return gr.update(choices=list(choices.keys()), visible=True), choices


# this is a bit confusing since we are yielding to outputs that update the gradio interface and there
# are three outputs because of quirks in how Gradio handles updates. I couldn't get it to update correctly unless
# I included both a markdown and a textbox representation of the same data.

# I was originally going to just have it update the markdown, but it doesn't update if only updated by itself.
# The docs state that only textboxes are guaranteed to update, so I was going to update the textbox and switch it for
# markdown on completion. However, I found that if I included both outputs, it would update the markdown as well.
# I hope this behavior continues to work as expected since it doesn't seem to be explicitly intended.

# The three outputs it has to yield and update are textbox, markdown and status_output (in that order)
def process_file_and_return_markdown(file, system_info, prompt, option, input_method, select_file, choices,
                                     doi_input, include_frictionless):
    file_paths, message = file_reading_util.file_setup(input_method, file, select_file, choices)
    yield '', '', message
    if len(file_paths) == 0:
        return

    frict_info = None
    if include_frictionless:
        frict_path = file_reading_util.find_file_with_tabular(file_paths)
        yield '', '', "Running Frictionless examination..."
        frict_info = frictionless_util.get_output(frict_path)  # this may take a while on large files


    # File processing of input files moved out of LLM client functions
    readme_file, data_file = file_reading_util.readme_and_data(file_paths)
    data_content = file_reading_util.get_csv_content(data_file)
    readme_content = ''

    data_content = f'DATA FILE\n---\n{data_content}\n---\n'

    if readme_file is not None:
        readme_content = file_reading_util.get_csv_content(readme_file)
        data_content += f'README FILE\n---\n{readme_content}\n---\n'
    if frict_info:
        data_content += f'Report from Frictionless data validation\n---\n{frict_info}\n---\n'

    accum = ''
    if doi_input and input_method == 'Dryad or Zenodo DOI':
        accum += f"# DOI: {doi_input}\n\n"

    if option == "GPT-4o":
        cgpt_response, accum = yield from open_api_code.generate(data_content, system_info, prompt, accum)
        accum += f"\n\n---\n\n"
        yield accum, accum, "Done with ChatGPT processing"

    elif option == "gemini-2.0-flash":
        google_response, accum = yield from google_api_code.generate(data_content, system_info, prompt, accum)
        accum += f"\n\n---\n\n"
        yield accum, accum, "Done with gemini processing"

    elif option == "llama3.1-70b":
        llama_response, accum = yield from bedrock_llama.generate(data_content, system_info, prompt, accum)
        accum += f"\n\n---\n\n"
        yield accum, accum, "Done with Llama processing"


# a standalone function to run Frictionless data validation without other processing
def submit_for_frictionless(file, option, input_method, select_file, choices, doi_input):
    file_paths, message = file_reading_util.file_setup(input_method, file, select_file, choices)
    yield '', '', message
    if len(file_paths) == 0:
        yield '', 'Some files must be chosen'
        return

    file_path = file_reading_util.find_file_with_tabular(file_paths)

    if file_path is None:
        yield '', "Only CSV and Excel files are supported."
        return

    accum = ''
    if doi_input and input_method == 'Dryad or Zenodo DOI':
        accum += f"# DOI: {doi_input}\n\n"

    accum += f"- Processing file: {os.path.basename(file_path)}\n\n"

    yield '', "Running Frictionless examination..."
    profiler = cProfile.Profile()
    profiler.enable()
    frict_info = frictionless_util.get_output(file_path)
    profiler.disable()

    # Print the profiling results
    result = StringIO()
    ps = pstats.Stats(profiler, stream=result).sort_stats(pstats.SortKey.CUMULATIVE)
    ps.print_stats()
    print(result.getvalue())

    if frict_info == "":
        frict_info = "No issues reported using the default Frictionless consistency checks."

    accum += f'## Report from frictionless data validation\n\n{frict_info}\n\n'
    yield accum, "Done"

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
