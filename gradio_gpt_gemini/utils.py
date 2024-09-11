# app.py
import gradio as gr
import pandas as pd
import markdown
import pdb
import argparse
import os
import utils  # Import the methods from utils.py

# Read the local CSS file
with open("styles.css", "r") as css_file:
    css_content = css_file.read()

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
    profiles = utils.list_profiles()

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

        input_method.change(fn=lambda x: utils.update_inputs(gr, x), inputs=input_method, outputs=[file_input, doi_group])

        # PROFILE ACTIONS
        profile_input.change(fn=utils.update_textareas, inputs=profile_input, outputs=[system_info_input, user_prompt_input])
        reload_button.click(fn=lambda: utils.reload_profiles(gr), inputs=None, outputs=profile_input)
        save_button.click(fn=utils.save_profile_action,
                          inputs=[save_profile_name_input, system_info_input, user_prompt_input],
                          outputs=[output, profile_input])
        save_button.click(fn=lambda: utils.reload_profiles(gr), inputs=None, outputs=profile_input)
        save_button.click(fn=utils.update_textareas, inputs=save_profile_name_input,
                          outputs=[system_info_input, user_prompt_input])
        del_button.click(fn=utils.delete_profile, inputs=profile_input, outputs=[output, profile_input])
        del_button.click(fn=lambda: utils.reload_profiles(gr), inputs=None, outputs=profile_input)

        # DOI ACTIONS
        choices_state = gr.State()
        load_doi_button.click(fn=lambda x: utils.load_file_list(gr, x), inputs=doi_input, outputs=[select_file, choices_state])

        # SUBMIT ACTIONS
        submit_button.click(fn=lambda *args: utils.process_file_and_return_markdown(gr, *args),
                            inputs=[file_input, system_info_input, user_prompt_input, option_input, input_method, select_file, choices_state],
                            outputs=output)

    auth = None
    if args.user and args.password:
        auth = (args.user, args.password)
    iface.launch(debug=args.debug, share=args.share, auth=auth, server_name=args.listen, server_port=args.port)

if __name__ == "__main__":
    main()