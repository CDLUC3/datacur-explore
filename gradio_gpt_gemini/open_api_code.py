import base64
import openai
import pdb
import pandas as pd
import codecs
import config
from striprtf.striprtf import rtf_to_text
import file_reading_util

# Check https://github.com/openai/openai-python for the latest version of the OpenAI Python library.
def generate(from_file, system_info, prompt):
    csv_content = file_reading_util.get_csv_content(from_file)

    client = openai.OpenAI(api_key=config.get('openai_api_key'))

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_info},
            {"role": "user", "content": prompt + '\n\n' + csv_content}
        ],
        max_tokens=2048  # Adjust the max tokens based on your needs
    )

    return response.choices[0].message.content
