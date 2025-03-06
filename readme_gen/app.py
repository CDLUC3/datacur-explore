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
import utils

# Read the local CSS file
with open("styles.css", "r") as css_file:
    css_content = css_file.read()

# looking at https://www.cloudskillsboost.google/course_templates/552?utm_campaign=FY24-Q2-global-website-skillsboost&utm_content=developers&utm_medium=et&utm_source=cgc-site&utm_term=-
# vertex ai studio

# https://medium.com/@nimritakoul01/getting-started-with-gradio-python-library-49e59e363c66 seems a good intro to gradio
# https://gradio.app/docs#quickstart
# https://gradio.app/docs#gr.Interface

def main():
    parser = argparse.ArgumentParser(description="Run the Gradio app with specified options.")
    parser.add_argument('--listen', type=str, default="127.0.0.1",
                        help="If set, the app will listen on the the IP address.")
    parser.add_argument('--port', type=int, default=7860, help="The port to run the app on.")
    parser.add_argument('--share', action='store_true', help="If set, the app will create a public link.")
    parser.add_argument('--user', type=str, help="Username for authentication.")
    parser.add_argument('--password', type=str, help="Password for authentication.")
    parser.add_argument('--debug', action='store_true', help="If set, the app will run in debug mode.")
    parser.add_argument('--ssl_keyfile', type=str, help="Path to the SSL key file.")
    parser.add_argument('--ssl_certfile', type=str, help="Path to the SSL certificate file.")

    args = parser.parse_args()

    # Create the Gradio interface
    # iface = gr.Interface(fn=process_file_and_return_markdown, inputs="file", outputs="markdown")

    default_system_info =\
        ("You are a system helping a researcher create a draft of a README.md file to include with their research data "
         "deposit.  You'll be supplied with some files from which to infer as much relevant information as possible.")

    default_user_prompt = (
        'Use the files below to get an idea of the research outputs for this dataset.  Please create readme '
        'output that speculatively describes what the dataset is about, the files and how to use it. Create the readme '
        'in a markdown format.   Use good academic practices for informing a new user of the data and the '
        'essentials of the dataset.')

    # Check if the JSON file exists and load values
    json_file_path = './prompt_profiles/_default.json'
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)
            default_system_info = data.get('system_info', default_system_info)
            default_user_prompt = data.get('user_prompt', default_user_prompt)

    options = ["GPT-4o", "Gemini-1.5-flash-001", "llama3.1-70b"]
    profiles = utils.list_profiles()

    # Create the Gradio interface with additional text inputs
    with gr.Blocks(css=css_content) as iface:
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
                markdown_output = gr.Markdown(visible=True)
                frict_md_output = gr.Markdown(visible=True)

        input_method.change(fn=utils.update_inputs, inputs=input_method, outputs=[file_input, doi_group])

        # PROFILE ACTIONS
        profile_input.change(fn=utils.update_textareas, inputs=profile_input, outputs=[system_info_input, user_prompt_input])
        reload_button.click(fn=utils.reload_profiles, inputs=None, outputs=profile_input)
        save_button.click(fn=utils.save_profile_action,
                          inputs=[save_profile_name_input, system_info_input, user_prompt_input],
                          outputs=[status_output, profile_input])

        del_button.click(fn=utils.delete_profile,inputs=profile_input,outputs=[status_output, profile_input])

        # SUBMIT ACTIONS
        # app.py
        submit_button.click(
            fn=utils.process_file_and_return_markdown,
            inputs=[file_input, system_info_input, user_prompt_input, option_input, input_method, doi_input],
            outputs=[textbox_output, markdown_output, status_output]
        )

    auth = None
    if args.user and args.password:
        auth = (args.user, args.password)
    iface.launch(debug=args.debug, share=args.share, auth=auth, server_name=args.listen, server_port=args.port,
                 ssl_keyfile=args.ssl_keyfile, ssl_certfile=args.ssl_certfile)


if __name__ == "__main__":
    main()
