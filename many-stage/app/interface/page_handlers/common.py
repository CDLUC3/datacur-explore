# utils.py
import os
import json
from itertools import accumulate


import app.llms.open_api_code as open_api_code
import app.llms.google_api_code as google_api_code
import gradio as gr
from app.common.path_utils import get_app_path
from app.repositories.repo_factory import repo_factory
import app.common.file_reading_util as file_reading_util
import app.common.frictionless_util as frictionless_util


def load_profile(profile_name):
    try:
        with open(get_app_path('prompt_profiles', f'{profile_name}.json'), 'r') as f:
            profile = json.load(f)
        return profile['system_info'], profile['user_prompt']
    except Exception as e:
        print(f"Error loading profile {profile_name}: {e}")
        return "", ""


def delete_profile(profile_name):
    try:
        os.remove(get_app_path('prompt_profiles', f'{profile_name}.json'))
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
        with open(get_app_path('prompt_profiles', f'{profile_name}.json'), 'w') as f:
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
        repo = repo_factory(doi)
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
def process_file_and_return_markdown(file, system_info, user_prompt, input_method, select_file, choices,
                                     doi_input):
    file_paths, message = file_reading_util.file_setup(input_method, file, select_file, choices)
    yield '', '', message
    if len(file_paths) == 0:
        return

    datafile_path = file_reading_util.find_file_with_tabular(file_paths)

    accum = ''

    if doi_input and input_method == 'Dryad or Zenodo DOI':
        accum += f"# DOI: {doi_input}\n\n"

    # ************************************
    # --- Frictionless data validation ---
    # ************************************

    yield accum, accum, "Running Frictionless examination..."
    frict_info = frictionless_util.get_output(datafile_path)  # this may take a while on large files
    if frict_info == "":
        frict_info = "No issues reported using the default Frictionless consistency checks."

    accum += f'---\n\n## Report from frictionless data validation\n\n{frict_info}\n\n---\n\n'

    yield accum, accum, "Ran frictionless data validation..."

    # *************************
    # --- Gemini processing ---
    # *************************

    yield accum, accum, "Starting gemini processing of frictionless and data file..."

    accum += f"## Gemini Output\n\n---\n\n"

    file_context = ""
    file_context += f"## Frictionless validation\n\n{frict_info}\n\n"
    file_text = file_reading_util.get_texty_content(datafile_path)
    file_context += f"## Filename: {os.path.basename(datafile_path)}\n\n{file_text}\n\n"

    google_response, accum = yield from google_api_code.generate(file_context, system_info, user_prompt, accum)

    accum += f"\n\n---\n\n"

    yield accum, accum, "Done with gemini processing"

    # ************************
    # --- GPT-4 processing ---
    # ************************

    yield accum, accum, "Starting GPT-4 processing of Gemini and data file..."

    accum += f"\n\n## GPT-4 Output\n\n---\n\n"

    file_context = ""
    file_context += f"## Gemini output\n\n{google_response}\n\n"
    file_context += f"## Filename: {os.path.basename(datafile_path)}\n\n{file_text}\n\n"

    cgpt_response, accum = yield from open_api_code.generate(file_context, system_info, user_prompt, accum)

    accum += f"\n\n---\n\n"

    yield accum, accum, "Done with GPT-4 processing"

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
        profiles = [f.split('.')[0] for f in os.listdir(get_app_path('prompt_profiles')) if f.endswith('.json')]
        sorted_profiles = sorted(profiles, key=lambda s: s.lower())
        return ["[Select profile]"] + sorted_profiles
    except Exception as e:
        print(f"Error listing profiles: {e}")
        return ["[Select profile]"]
