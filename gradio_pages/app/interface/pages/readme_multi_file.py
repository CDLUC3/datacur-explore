import gradio as gr
import os
import json
import app.interface.page_handlers.common as utils
import app.interface.page_handlers.readme_multi_file as readme_multi_file
from app.common.path_utils import get_app_path
import pdb

def create_readme_page(js_inject_content=None):
    default_system_info =\
        ("You are a system helping a researcher create a draft of a README.md file to include with their research data "
         "deposit.  You'll be supplied with some files from which to infer as much relevant information as possible.")

    default_user_prompt = (
        'Use the files below to get an idea of the research outputs for this dataset.  Please create readme '
        'output that speculatively describes what the dataset is about, the files and how to use it. Create the readme '
        'in a markdown format.   Use good academic practices for informing a new user of the data and the '
        'essentials of the dataset.')

    # Check if the JSON file exists and load values
    json_file_path = get_app_path('prompt_profiles', '_default_multi_file.json')
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)
            default_system_info = data.get('system_info', default_system_info)
            default_user_prompt = data.get('user_prompt', default_user_prompt)
            default_user_prompt2 = data.get('user_prompt2', '')

    user_prompt_input2 = gr.State(default_user_prompt2)

    options = ["GPT-4o", "gemini-2.0-flash", "llama3.1-70b"]
    profiles = utils.list_profiles()

    # Create the Gradio interface with additional text inputs
    with gr.Blocks():
        with gr.Row():
            gr.Markdown("# Generate readme with LLMs from files")
        with gr.Row():
            with gr.Column():
                input_method = gr.Radio(label="Choose an input method", choices=["Upload file", "Dryad or Zenodo DOI"],
                                        value="Dryad or Zenodo DOI")
                file_input = gr.File(label="Upload file(s)", file_count="multiple", visible=False)
                with gr.Group(visible=True, elem_classes='grp-style') as doi_group:
                    with gr.Row(elem_classes="bottom-align grp-style"):
                        doi_input = gr.Textbox(label="Dryad or Zenodo DOI", placeholder="e.g. 10.5061/dryad.8515j",
                                               value="10.5281/zenodo.13948032")
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
                status_output = gr.Textbox(visible=True, label="Status", placeholder="Status messages will appear here")
                textbox_output = gr.Textbox(visible=False, show_label=False, placeholder="Output will appear here")
                markdown_output = gr.Markdown(visible=True, elem_classes="readme-markdown")
                download_control = gr.File(label="Download output")

                # frict_md_output = gr.Markdown(visible=True)

        input_method.change(fn=utils.update_inputs, inputs=input_method, outputs=[file_input, doi_group])

        # PROFILE ACTIONS
        profile_input.change(fn=utils.update_textareas, inputs=profile_input, outputs=[system_info_input, user_prompt_input, user_prompt_input2])
        reload_button.click(fn=utils.reload_profiles, inputs=None, outputs=profile_input)
        save_button.click(fn=utils.save_profile_action,
                          inputs=[save_profile_name_input, system_info_input, user_prompt_input, user_prompt_input2],
                          outputs=[status_output, profile_input])

        del_button.click(fn=utils.delete_profile, inputs=profile_input, outputs=[status_output, profile_input])

        # SUBMIT ACTIONS
        submit_button.click(
            fn=readme_multi_file.process_file_and_return_markdown,
            inputs=[file_input, system_info_input, user_prompt_input, option_input, input_method, doi_input],
            outputs=[textbox_output, markdown_output, status_output, download_control]
        )
