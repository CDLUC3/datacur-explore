# utils.py
import os
import json
import repo_factory
import file_reading_util
import open_api_code
import google_api_code
import time
import gradio as gr

def list_profiles():
    try:
        profiles = [f.split('.')[0] for f in os.listdir('prompt_profiles') if f.endswith('.json')]
        return ["[Select profile]"] + profiles
    except Exception as e:
        print(f"Error listing profiles: {e}")
        return ["[Select profile]"]

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
        return f"Error loading DOI: {e}"
    file_list = repo.get_filenames_and_links()
    choices = {key: value for item in file_list for key, value in item.items()}
    choices['[Select file after looking up DOI]'] = '[Select file after looking up DOI]'
    return gr.update(choices=list(choices.keys()), value='[Select file after looking up DOI]', visible=True), choices

def process_file_and_return_markdown(file, system_info, prompt, option, input_method, select_file, choices, completed_state):
    if input_method == 'Upload file' and file is None:
        yield "# No file was uploaded."
        return
    elif input_method == 'Dryad or Zenodo DOI' and select_file == '[Select file after looking up DOI]':
        yield "# The doi needs to be looked up and a file selected."
        return

    if input_method == 'Dryad or Zenodo DOI':
        file_url = choices.get(select_file)
        file_path = file_reading_util.download_file(file_url, select_file)
    else:
        file_path = file.name

    f_name = os.path.basename(file_path)
    if option == "GPT-4o":
        return open_api_code.generate_stream(file_path, system_info, prompt)
        # for partial_response in open_api_code.generate_stream(file_path, system_info, prompt):
        #     yield f"# Analyzed by GPT-4o:\n\nFile name: {f_name}\n\n" + partial_response
    elif option == "Gemini-1.5-flash-001":
        words = ['# A ', 'cat ', 'is ', 'looking ', 'at ', 'a ', 'dog', '.']
        text_accum = "" # accumulate the text
        counter = 0
        for word in words:
            counter += 1
            text_accum += word
            # yield text_accum, text_accum, False
            yield (gr.update(visible=True, value=text_accum),
                    gr.update(visible=False, value=text_accum),
                    f'running {counter}')
            time.sleep(1)

        print('GETTING TO RETURN VALUE')
        yield (gr.update(visible=False, value=text_accum),
                gr.update(visible=True, value=text_accum),
                'Done')
        # note that return doesn't work right for final value and you need to yield it
        # for partial_response in google_api_code.generate_stream(file_path, system_info, prompt):
        #     yield f"# Analyzed by Gemini-1.5-flash-001:\n\nFile name: {f_name}\n\n" + partial_response

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


