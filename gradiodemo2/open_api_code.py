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

    text1 = """What suggestions can you make to improve data quality for the data in the file? Please be specific about
    things you recommend changing and format the action items as a bulleted list in markdown."""

    textsi_1 = 'The file contains research data in tabular format. Analyze it for data ' \
               'quality metrics and to help visualize the data for other researchers in the same field.  Here is the ' \
               f'csv content:\n\n{csv_content}\n\n'

    client = openai.OpenAI(api_key=local_secrets.OPENAI_API_KEY)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": text1},
            {"role": "user", "content": textsi_1}
        ],
        # prompt=textsi_1,
        max_tokens=1000  # Adjust the max tokens based on your needs
    )

    return response.choices[0].message.content
