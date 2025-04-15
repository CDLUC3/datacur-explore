import gradio as gr
import os
import json
from app.interface.page_handlers.common import (
    list_profiles,
    update_inputs,
    update_textareas,
    reload_profiles,
    save_profile_action,
    delete_profile,
    load_file_list,
    process_file_and_return_markdown
)

from app.interface.page_handlers.data_quality import (
    process_file_and_return_markdown,
    submit_for_frictionless
)

from app.common.path_utils import get_app_path

def data_quality_page():
    with open(get_app_path("interface", "pages", "styles.css"), "r") as css_file:
        css_content = css_file.read()

    default_system_info = \
        ("You are a system helping a researcher analyze a file containing research data in tabular format. "
         "The objective is to give advice to improve the data quality for reuse and reproducibility by other researchers "
         "in the same field. Besides general practices, specific advice for improving the given file is most useful. "
         "Notify the user if the file does not appear to be tabular data.")

    default_user_prompt = (
        'The file contains research data in tabular format. Analyze it for data '
        'quality metrics and to help visualize the data for other researchers in the same field. How can it be '
        'improved for reuse and reproducibility?')

    # Check if the JSON file exists and load values
    json_file_path = get_app_path('prompt_profiles', '_default_data_quality.json')
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)
            default_system_info = data.get('system_info', default_system_info)
            default_user_prompt = data.get('user_prompt', default_user_prompt)

    options = ["GPT-4o", "gemini-2.0-flash", "llama3.1-70b"]
    profiles = list_profiles()

    # Create the Gradio interface with additional text inputs
    with gr.Blocks(css=css_content) as iface:
        with gr.Row():
            gr.Markdown("# Basic data quality analysis with LLMs")
        with gr.Row():
            with gr.Column():
                input_method = gr.Radio(label="Choose an input method", choices=["Upload file", "Dryad or Zenodo DOI"],
                                        value="Dryad or Zenodo DOI")
                file_input = gr.File(label="Upload file", visible=False)
                with gr.Group(visible=True, elem_classes='grp-style') as doi_group:
                    with gr.Row(elem_classes="bottom-align grp-style"):
                        doi_input = gr.Textbox(label="Dryad or Zenodo DOI", placeholder="e.g. 10.5061/dryad.8515j",
                                               value="10.5281/zenodo.13616727", scale=3)
                        load_doi_button = gr.Button("Lookup DOI", elem_classes="small-button margin-bottom", scale=1)
                    with gr.Row():
                        select_files = gr.CheckboxGroup(label="Choose readme and a data file to analyze", choices=[],
                                                        interactive=True)
                with gr.Accordion("Prompting", open=True):
                    system_info_input = gr.TextArea(label="System conditioning", value=default_system_info)
                    user_prompt_input = gr.TextArea(label="User prompt", value=default_user_prompt)
                with gr.Accordion("Profile management", open=False):
                    with gr.Row(elem_classes="bottom-align"):
                        profile_input = gr.Dropdown(label="Load profile name", choices=profiles,
                                                    value="[Select profile]",
                                                    interactive=True, scale=4)
                        reload_button = gr.Button("🔄 refresh", elem_classes="small-button", scale=1)
                        del_button = gr.Button("delete profile", elem_classes="small-button", scale=1)
                    with gr.Row(elem_classes="bottom-align"):
                        save_profile_name_input = gr.Textbox(label="Profile name to save")
                        save_button = gr.Button("Save Profile", elem_classes="small-button")
                include_frictionless = gr.Checkbox(label="Validate w/ Frictionless and send to LLM", value=False)
                option_input = gr.Radio(label="Choose an option", choices=options, value="GPT-4o")
                frictionless_submit = gr.Button("Submit for Frictionless validation")
                submit_button = gr.Button("Submit to LLM")
            with gr.Column(elem_id="right-column", elem_classes="column"):
                status_output = gr.Textbox(visible=True, label="Status", placeholder="Status messages will appear here")
                textbox_output = gr.Textbox(visible=False, show_label=False, placeholder="Output will appear here")
                markdown_output = gr.Markdown(visible=True)
                frict_md_output = gr.Markdown(visible=True)

        input_method.change(fn=update_inputs, inputs=input_method, outputs=[file_input, doi_group])

        # PROFILE ACTIONS
        profile_input.change(fn=update_textareas, inputs=profile_input,
                             outputs=[system_info_input, user_prompt_input])
        reload_button.click(fn=reload_profiles, inputs=None, outputs=profile_input)
        save_button.click(fn=save_profile_action,
                          inputs=[save_profile_name_input, system_info_input, user_prompt_input],
                          outputs=[status_output, profile_input])

        del_button.click(fn=delete_profile, inputs=profile_input, outputs=[status_output, profile_input])

        # DOI ACTIONS
        choices_state = gr.State()
        load_doi_button.click(fn=load_file_list, inputs=doi_input, outputs=[select_files, choices_state])

        # SUBMIT ACTIONS
        submit_button.click(
            fn=process_file_and_return_markdown,
            inputs=[file_input, system_info_input, user_prompt_input, option_input, input_method, select_files,
                    choices_state, doi_input, include_frictionless],
            outputs=[textbox_output, markdown_output, status_output]
        )
        frictionless_submit.click(
            fn=submit_for_frictionless,
            inputs=[file_input, option_input, input_method, select_files, choices_state, doi_input],
            outputs=[frict_md_output, status_output]
        )
