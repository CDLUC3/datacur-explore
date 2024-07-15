import base64
import openai
import pdb
import local_secrets
import pandas as pd

# Check https://github.com/openai/openai-python for the latest version of the OpenAI Python library.
# TODO: update to use better interface since this began based on information from ChatGPT that was all out of date
# for an old version of the API that is now invalid and there are probably better ways to do this.

def generate(from_file):
    df = pd.read_csv(from_file)

    csv_content = df.to_string()[0:5000]

    system_info = """You are a system helping a researcher analyze a file containing research data in tabular format.
         The objective is to give advice to improve the data quality for reuse and reproducibility by other researchers
         in the same field. Besides general practices, specific advice for improving the given file is most useful."""

    prompt = (
        'The file contains research data in tabular format. Analyze it for data '
        'quality metrics and to help visualize the data for other researchers in the same field. How can it be '
        'improved for reuse and reproducibility? \n\n' + csv_content)

    client = openai.OpenAI(api_key=local_secrets.OPENAI_API_KEY)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_info},
            {"role": "user", "content": prompt}
        ],
        # prompt=textsi_1,
        max_tokens=1024  # Adjust the max tokens based on your needs
    )

    return response.choices[0].message.content
