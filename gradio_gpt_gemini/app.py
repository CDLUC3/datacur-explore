import gradio as gr
import pandas as pd
import markdown
import pdb
import open_api_code
import google_api_code
import argparse
import os
import json
import repo_factory
import file_reading_util

`# Read the local CSS file
with open("styles.css", "r") as css_file:
    css_content = css_file.read()

# looking at https://www.cloudskillsboost.google/course_templates/552?utm_campaign=FY24-Q2-global-website-skillsboost&utm_content=developers&utm_medium=et&utm_source=cgc-site&utm_term=-
# vertex ai studio

# https://medium.com/@nimritakoul01/getting-started-with-gradio-python-library-49e59e363c66 seems a good intro to gradio
# https://gradio.app/docs#quickstart
# https://gradio.app/docs#gr.Interface

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

def save_profile_action(profile_name, system_info, user_prompt):
    if profile_name is None:
        return "Profile name is required"
    if profile_name.endswith('.json'):
        profile_name = profile_name[:-5]
    try:
        profile = {
            "system_info": system_info,
            "user_prompt": user_prompt
        }
        with open(f"prompt_profiles/{profile_name}.json", 'w') as f:
            json.dump(profile, f)
        return f"Profile {profile_name} saved.", list_profiles()
    except Exception as e:
        print(f"Error saving profile {profile_name}: {e}")
        return f"Error saving profile {profile_name}: {e}", list_profiles()

def load_file_list(doi):
    try:
        repo = repo_factory.repo_factory(doi)
    except ValueError as e:
        return f"Error loading DOI: {e}"
    file_list = repo.get_filenames_and_links()
    # file_list = [(key, value) for item in file_list for key, value in item.items()]
    # file_list.insert(0, ('[Select file after looking up DOI]', '[Select file after looking up DOI]'))
    # return gr.update(choices=file_list, value='[Select file after looking up DOI]', visible=True)
    choices = {key: value for item in file_list for key, value in item.items()}
    choices['[Select file after looking up DOI]'] = '[Select file after looking up DOI]'
    return gr.update(choices=list(choices.keys()), value='[Select file after looking up DOI]', visible=True), choices

def process_file_and_return_markdown(file, system_info, prompt, option, input_method, select_file, choices):
    if input_method == 'Upload file' and file is None:
        return "# No file was uploaded."
    elif input_method == 'Dryad or Zenodo DOI' and select_file == '[Select file after looking up DOI]':
        return "# The doi needs to be looked up and a file selected."

    if input_method == 'Dryad or Zenodo DOI':
        file_url = choices.get(select_file)
        # Download the file from the URL and save it to a temporary file
        file_path = file_reading_util.download_file(file_url, select_file)
    else:
        file_path = file.name

    f_name = os.path.basename(file_path)
    if option == "GPT-4o":
        response = open_api_code.generate(file_path, system_info, prompt)
        response = f"# Analyzed by GPT-4o:\n\nFile name: {f_name}\n\n" + response
    elif option == "Gemini-1.5-flash-001":
        response = google_api_code.generate(file_path, system_info, prompt)
        response = f"# Analyzed by Gemini-1.5-flash-001:\n\nFile name: {f_name}\n\n" + response
    return response

def update_textareas(profile_name):
    system_info, user_prompt = load_profile(profile_name)
    return system_info, user_prompt

def reload_profiles():
    return gr.update(choices=list_profiles())

def update_inputs(input_method):
    if input_method == "Upload file":
        return gr.update(visible=True), gr.update(visible=False)
    elif input_method == "Dryad or Zenodo DOI":
        return gr.update(visible=False), gr.update(visible=True)

def main():
    parser = argparse.ArgumentParser(description="Run the Gradio app with specified options.")
    parser.add_argument('--listen', type=str, default="127.0.0.1",
                        help="If set, the app will listen on the the IP address.")
    parser.add_argument('--port', type=int, default=7860, help="The port to run the app on.")
    parser.add_argument('--share', action='store_true', help="If set, the app will create a public link.")
    parser.add_argument('--user', type=str, help="Username for authentication.")
    parser.add_argument('--password', type=str, help="Password for authentication.")
    parser.add_argument('--debug', action='store_true', help="If set, the app will run in debug mode.")

    args = parser.parse_args()

    # Create the Gradio interface
    # iface = gr.Interface(fn=process_file_and_return_markdown, inputs="file", outputs="markdown")

    default_system_info =\
        ("You are a system helping a researcher analyze a file containing research data in tabular format. "
         "The objective is to give advice to improve the data quality for reuse and reproducibility by other researchers "
         "in the same field. Besides general practices, specific advice for improving the given file is most useful. "
         "Notify the user if the file does not appear to be tabular data.")

    default_user_prompt = (
        'The file contains research data in tabular format. Analyze it for data '
        'quality metrics and to help visualize the data for other researchers in the same field. How can it be '
        'improved for reuse and reproducibility?')

    options = ["GPT-4o", "Gemini-1.5-flash-001"]
    profiles = list_profiles()

    # Create the Gradio interface with additional text inputs
    with gr.Blocks(css=css_content) as iface:
        with gr.Row():
            gr.Markdown("# Basic data quality analysis with LLMs")
        with gr.Row():
            with gr.Column():
                input_method = gr.Radio(label="Choose an input method", choices=["Upload file", "Dryad or Zenodo DOI"], value="Upload file")
                file_input = gr.File(label="Upload file", visible=True)
                with gr.Group(visible=False, elem_classes='grp-style') as doi_group:
                    with gr.Row(elem_classes="bottom-align grp-style"):
                        doi_input = gr.Textbox(label="Dryad or Zenodo DOI", placeholder="e.g. 10.5061/dryad.8515j", scale=3)
                        load_doi_button = gr.Button("Lookup DOI", elem_classes="small-button margin-bottom", scale=1)
                    with gr.Row():
                        select_file = gr.Dropdown(label="Choose file to analyze",
                                                  value='[Select file after looking up DOI]',
                                                  choices=[('[Select file after Looking up DOI]', '[Select file after looking up DOI]')],
                                                  interactive=True)
                with gr.Accordion("Prompting", open=True):
                    system_info_input = gr.TextArea(label="System conditioning", value=default_system_info)
                    user_prompt_input = gr.TextArea(label="User prompt", value=default_user_prompt)
                with gr.Accordion("Profile management", open=False):
                    with gr.Row(elem_classes="bottom-align"):
                        profile_input = gr.Dropdown(label="Load profile name", choices=profiles, value="[Select profile]",
                                                    interactive=True, scale=4)
                        reload_button = gr.Button("🔄 refresh", elem_classes="small-button", scale=1)
                        del_button = gr.Button("delete profile", elem_classes="small-button", scale=1)
                    with gr.Row(elem_classes="bottom-align"):
                        save_profile_name_input = gr.Textbox(label="Profile name to save")
                        save_button = gr.Button("Save Profile", elem_classes="small-button")

                option_input = gr.Radio(label="Choose an option", choices=options, value="GPT-4o")
                submit_button = gr.Button("Submit to LLM")
            with gr.Column(elem_id="right-column", elem_classes="column"):
                output = gr.Markdown()

        input_method.change(fn=update_inputs, inputs=input_method, outputs=[file_input, doi_group])

        # PROFILE ACTIONS
        profile_input.change(fn=update_textareas, inputs=profile_input, outputs=[system_info_input, user_prompt_input])
        reload_button.click(fn=reload_profiles, inputs=None, outputs=profile_input)
        save_button.click(fn=save_profile_action,
                          inputs=[save_profile_name_input, system_info_input, user_prompt_input],
                          outputs=[output, profile_input])
        save_button.click(fn=reload_profiles, inputs=None, outputs=profile_input)
        save_button.click(fn=update_textareas, inputs=save_profile_name_input,
                          outputs=[system_info_input, user_prompt_input])
        del_button.click(fn=delete_profile, inputs=profile_input, outputs=[output, profile_input])
        del_button.click(fn=reload_profiles, inputs=None, outputs=profile_input)


        # DOI ACTIONS
        choices_state = gr.State()
        load_doi_button.click(fn=load_file_list, inputs=doi_input, outputs=[select_file, choices_state])

        # SUBMIT ACTIONS
        submit_button.click(fn=process_file_and_return_markdown,
                            inputs=[file_input, system_info_input, user_prompt_input, option_input, input_method, select_file, choices_state],
                            outputs=output)

    auth = None
    if args.user and args.password:
        auth = (args.user, args.password)
    iface.launch(debug=args.debug, share=args.share, auth=auth, server_name=args.listen, server_port=args.port)


if __name__ == "__main__":
    main()
