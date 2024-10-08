# utils.py
import os
import json
import repo_factory
import file_reading_util
import open_api_code
import google_api_code
import time
import gradio as gr
import pdb

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
    choices['[Select file after looking up DOI]'] = '[Select file after looking up DOI]'
    return gr.update(choices=list(choices.keys()), value='[Select file after looking up DOI]', visible=True), choices

def process_file_and_return_markdown(file, system_info, prompt, option, input_method, select_file, choices, completed_state):
    if input_method == 'Upload file' and file is None:
        yield '', '', "No file was uploaded."
        return
    elif input_method == 'Dryad or Zenodo DOI' and select_file == '[Select file after looking up DOI]':
        yield '', '', "The doi needs to be looked up and a file selected."
        return

    if input_method == 'Dryad or Zenodo DOI':
        file_url = choices.get(select_file)
        file_path = file_reading_util.download_file(file_url, select_file)
    else:
        file_path = file.name

    f_name = os.path.basename(file_path)
    if option == "GPT-4o":
        yield from open_api_code.generate_stream(file_path, system_info, prompt)

        # note that return doesn't work right for final value. you need to yield it instead
        yield (gr.update(visible=False),
               gr.update(visible=True),
               'Done')
    elif option == "Gemini-1.5-flash-001":
        yield from google_api_code.generate(file_path, system_info, prompt)

        print('GETTING TO RETURN VALUE')

        # note that return doesn't work right for final value. you need to yield it instead
        yield (gr.update(visible=False),
                gr.update(visible=True),
                'Done')

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


