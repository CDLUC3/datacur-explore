import base64
import openai
import pdb
import pandas as pd
import codecs
import config
from striprtf.striprtf import rtf_to_text
import file_reading_util
import logging
import gradio as gr

# logging.basicConfig(level=logging.DEBUG)

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
        max_tokens=4096  # Adjust the max tokens based on your needs
    )

    return response.choices[0].message.content


def generate_stream(from_file, system_info, prompt):
    csv_content = file_reading_util.get_csv_content(from_file)

    client = openai.OpenAI(api_key=config.get('openai_api_key'))

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_info},
            {"role": "user", "content": prompt + '\n\n' + csv_content}
        ],
        max_tokens=4096,
        stream=True
    )

    temp_chunk = ''
    accum = ''

    for chunk in response:
        # print(f"Chunk received: {chunk}")

        if len(chunk.choices) > 0:
            # save up chunks so it doesn't update like every 3 letters in an overly small and insane way
            real_chunk = chunk.choices[0].delta.content
            if real_chunk:
                temp_chunk += real_chunk

                if len(temp_chunk) > 30:
                    accum += temp_chunk
                    temp_chunk = ''
                    yield accum, accum, 'Running'

    if temp_chunk:
        accum += temp_chunk
    yield accum, accum, 'Running'
