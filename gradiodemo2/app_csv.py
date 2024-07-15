import gradio as gr
import pandas as pd
import markdown
import pdb
import open_api_code

# looking at https://www.cloudskillsboost.google/course_templates/552?utm_campaign=FY24-Q2-global-website-skillsboost&utm_content=developers&utm_medium=et&utm_source=cgc-site&utm_term=-
# vertex ai studio

# vertex ai just has you use the tools in the console to authenticate

# pip install --upgrade google-cloud-aiplatform
# gcloud auth application-default login

def process_file_and_return_markdown(file):
    # Read the file
    # df = pd.read_csv(file.name)
    response = open_api_code.generate(file.name)

    # Process the file (this would depend on your specific cloud service)
    # For the sake of this example, let's just convert the DataFrame to Markdown
    # markdown_output = df.to_markdown()

    return response


# Create the Gradio interface
iface = gr.Interface(fn=process_file_and_return_markdown, inputs="file", outputs="markdown")
iface.launch()