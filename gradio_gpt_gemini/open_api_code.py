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

def generate_stream(file_paths, system_info, prompt, starting_text='', frict_info='', model='gpt-40'):
    readme_file, data_file = file_reading_util.readme_and_data(file_paths)
    data_content = file_reading_util.get_csv_content(data_file)

    # for larger files and using their special storage, this URL seems to document how to do it
    # https://cloud.google.com/vertex-ai/docs/python-sdk/data-classes

    readme_content = None

    if readme_file is not None:
        readme_content = file_reading_util.get_csv_content(readme_file)
        readme_content = f'README FILE\n---\n{readme_content}\n---\n'
    if frict_info:
        frict_info = f'Report from Frictionless data validation\n---\n{frict_info}\n---\n'
    data_content = f'DATA FILE\n---\n{data_content}\n---\n'

    # just keep and join non-empty or non None items
    parts = ' '.join([item for item in [readme_content, data_content, frict_info] if item])

    client = openai.OpenAI(api_key=config.get('openai_api_key'))

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_info},
            {"role": "user", "content": prompt + '\n\n' + parts}
        ],
        max_tokens=4096,
        stream=True
    )

    # See https://www.kdnuggets.com/openai-api-for-beginners-your-easy-to-follow-starter-guide
    # You may add additional content with the assistant role and content from previous conversation
    # You may add an image with user, content: {"type": "image_url", "url": "https://example.com/image.jpg"}
    # and may also base64 encode without URL.

    temp_chunk = ''
    accum = starting_text

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
                    yield accum, accum, 'Running ChatGPT generation'

    if temp_chunk:
        accum += temp_chunk
    yield accum, accum, 'Finished ChatGPT generation'
