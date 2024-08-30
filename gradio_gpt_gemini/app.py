import gradio as gr
import pandas as pd
import markdown
import pdb
import open_api_code
import google_api_code
import argparse
import os
import json

# looking at https://www.cloudskillsboost.google/course_templates/552?utm_campaign=FY24-Q2-global-website-skillsboost&utm_content=developers&utm_medium=et&utm_source=cgc-site&utm_term=-
# vertex ai studio

# https://medium.com/@nimritakoul01/getting-started-with-gradio-python-library-49e59e363c66 seems a good intro to gradio
# https://gradio.app/docs#quickstart
# https://gradio.app/docs#gr.Interface

def list_profiles():
    try:
        return [f.split('.')[0] for f in os.listdir('prompt_profiles') if f.endswith('.json')]
    except Exception as e:
        print(f"Error listing profiles: {e}")
        return []

def load_profile(profile_name):
    try:
        with open(f"prompt_profiles/{profile_name}.json", 'r') as f:
            profile = json.load(f)
        return profile['system_info'], profile['user_prompt']
    except Exception as e:
        print(f"Error loading profile {profile_name}: {e}")
        return "", ""

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
        return f"Profile {profile_name} saved."
    except Exception as e:
        print(f"Error saving profile {profile_name}: {e}")


def process_file_and_return_markdown(file, system_info, prompt, option):
    if file is None:
        return "No file was uploaded."

    f_name = os.path.basename(file.name)
    if option == "GPT-4o":
        response = open_api_code.generate(file.name, system_info, prompt)
        response = f"# Analyzed by GPT-4o:\n\nFile name: {f_name}\n\n" + response
    elif option == "Gemini-1.5-flash-001":
        response = google_api_code.generate(file.name, system_info, prompt)
        response = f"# Analyzed by Gemini-1.5-flash-001:\n\nFile name: {f_name}\n\n" + response
    return response

def update_textareas(profile_name):
    system_info, user_prompt = load_profile(profile_name)
    return system_info, user_prompt

def reload_profiles():
    return gr.update(choices=list_profiles())

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
    with gr.Blocks() as iface:
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("# Basic data quality analysis with LLMs")
                file_input = gr.File(label="Upload file")
                system_info_input = gr.TextArea(label="System conditioning", value=default_system_info)
                user_prompt_input = gr.TextArea(label="User prompt", value=default_user_prompt)
                option_input = gr.Radio(label="Choose an option", choices=options, value="GPT-4o")
                with gr.Row():
                    with gr.Column(scale=8):
                        profile_input = gr.Dropdown(label="Profile name", choices=profiles, value=profiles[0] if profiles else None,
                                                interactive=True)
                    with gr.Column(scale=2):
                        reload_button = gr.Button("🔄", elem_classes="small-button")

                with gr.Row():
                    with gr.Column(scale=8):
                        save_profile_name_input = gr.Textbox(label="Profile name to save")
                    with gr.Column(scale=2):
                        save_button = gr.Button("Save Profile")

                submit_button = gr.Button("Submit to LLM")
            with gr.Column(scale=1):
                output = gr.Markdown()

        profile_input.change(fn=update_textareas, inputs=profile_input, outputs=[system_info_input, user_prompt_input])
        reload_button.click(fn=reload_profiles, inputs=None, outputs=profile_input)
        save_button.click(fn=save_profile_action,
                          inputs=[save_profile_name_input, system_info_input, user_prompt_input],
                          outputs=output)
        submit_button.click(fn=process_file_and_return_markdown,
                            inputs=[file_input, system_info_input, user_prompt_input, option_input],
                            outputs=output)

    auth = None
    if args.user and args.password:
        auth = (args.user, args.password)
    iface.launch(debug=args.debug, share=args.share, auth=auth, server_name=args.listen, server_port=args.port)


if __name__ == "__main__":
    main()
