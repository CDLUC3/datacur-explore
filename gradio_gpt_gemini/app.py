import gradio as gr
import pandas as pd
import markdown
import pdb
import open_api_code
import google_api_code
import argparse
import os

# looking at https://www.cloudskillsboost.google/course_templates/552?utm_campaign=FY24-Q2-global-website-skillsboost&utm_content=developers&utm_medium=et&utm_source=cgc-site&utm_term=-
# vertex ai studio

# https://medium.com/@nimritakoul01/getting-started-with-gradio-python-library-49e59e363c66 seems a good intro to gradio
# https://gradio.app/docs#quickstart
# https://gradio.app/docs#gr.Interface


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

    # Create the Gradio interface with additional text inputs
    iface = gr.Interface(
        fn=process_file_and_return_markdown,
        inputs=["file",
                gr.TextArea(label="System conditioning", value=default_system_info),
                gr.TextArea(label="User prompt", value=default_user_prompt),
                gr.Radio(label="Choose an option", choices=options, value="GPT-4o")
                ],
        outputs="markdown",
        title="Basic data quality analysis with LLM"
    )

    auth = None
    if args.user and args.password:
        auth = (args.user, args.password)
    iface.launch(debug=args.debug, share=args.share, auth=auth, server_name=args.listen, server_port=args.port)


if __name__ == "__main__":
    main()
