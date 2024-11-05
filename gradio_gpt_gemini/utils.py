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


# this is a bit confusing since we are yielding to outputs that update the gradio interface and there
# are three outputs because of quirks in how Gradio handles updates. I couldn't get it to update correctly unless
# I included both a markdown and a textbox representation of the same data.

# I was originally going to just have it update the markdown, but it doesn't update if only updated by itself.
# The docs state that only textboxes are guaranteed to update, so I was going to update the textbox and switch it for
# markdown on completion. However, I found that if I included both outputs, it would update the markdown as well.
# I hope this behavior continues to work as expected since it doesn't seem to be explicitly intended.

# The three outputs it has to yield and update are textbox, markdown and status_output (in that order)
def process_file_and_return_markdown(file, system_info, prompt, option, input_method, select_file, choices, doi_input):
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

    accum = ''
    if doi_input:
        accum += f"# DOI: {doi_input}\n\n"

    accum += f"- Processing file: {file_path}\n\n"
    # should be able to work with file_path now in Frictionless data
    if file_path.endswith(('.csv', '.xls', '.xlsx')):
        profiler = cProfile.Profile()
        profiler.enable()
        frict_info = frictionless_util.get_output(file_path)
        profiler.disable()

        # Print the profiling results
        result = StringIO()
        ps = pstats.Stats(profiler, stream=result).sort_stats(pstats.SortKey.CUMULATIVE)
        ps.print_stats()
        print(result.getvalue())

        accum += f'## Report from frictionless data validation\n\n{frict_info}\n\n---\n## Report from LLM\n\n'
        yield accum, accum, "Processing file..."
    else:
        yield '', '', "Only CSV and Excel files are supported."


    f_name = os.path.basename(file_path)
    if option == "GPT-4o":
        yield from open_api_code.generate_stream(file_path, system_info, prompt, accum)

        # note that return doesn't work right for final value. you need to yield it instead
        yield (gr.update(visible=False),
               gr.update(visible=True),
               'Done')
    elif option == "Gemini-1.5-flash-001":
        yield from google_api_code.generate(file_path, system_info, prompt, accum)

        # note that return doesn't work right for final value. you need to yield it instead
        yield (gr.update(visible=False),
                gr.update(visible=True),
                'Done')
    elif option == "llama3.1-70b":
        yield from bedrock_llama.generate_stream(file_path, system_info, prompt, accum)

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


