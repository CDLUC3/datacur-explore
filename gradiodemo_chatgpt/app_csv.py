import gradio as gr
import pandas as pd
import markdown
import pdb
import open_api_code
import local_secrets

# looking at https://www.cloudskillsboost.google/course_templates/552?utm_campaign=FY24-Q2-global-website-skillsboost&utm_content=developers&utm_medium=et&utm_source=cgc-site&utm_term=-
# vertex ai studio

# vertex ai just has you use the tools in the console to authenticate

# pip install --upgrade google-cloud-aiplatform
# gcloud auth application-default login

def process_file_and_return_markdown(file, system_info, prompt):
    # Read the file
    # df = pd.read_csv(file.name)
    response = open_api_code.generate(file.name, system_info, prompt, local_secrets.OPENAI_API_KEY)

    # Process the file (this would depend on your specific cloud service)
    # For the sake of this example, let's just convert the DataFrame to Markdown
    # markdown_output = df.to_markdown()

    return response


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

# Create the Gradio interface with additional text inputs
iface = gr.Interface(
    fn=process_file_and_return_markdown,
    inputs=["file", gr.TextArea(label="System conditioning", value=default_system_info),
            gr.TextArea(label="User prompt", value=default_user_prompt)],
    outputs="markdown",
    title="Basic data quality analysis with ChatGPT"
)

iface.launch(debug=True)
