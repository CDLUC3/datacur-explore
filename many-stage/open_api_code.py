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

def generate(file_context, system_info, prompt, starting_text=''):

    client = openai.OpenAI(api_key=config.get('openai_api_key'))

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_info},
            {"role": "user", "content": prompt + '\n\n' + file_context}
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

    cgpt_only_output = ''

    for chunk in response:
        # print(f"Chunk received: {chunk}")

        if len(chunk.choices) > 0:
            # save up chunks so it doesn't update like every 3 letters in an overly small and insane way
            real_chunk = chunk.choices[0].delta.content
            if real_chunk:
                temp_chunk += real_chunk

                if len(temp_chunk) > 30:
                    accum += temp_chunk
                    cgpt_only_output += temp_chunk
                    temp_chunk = ''
                    yield accum, accum, 'Running ChatGPT generation'

    if temp_chunk:
        accum += temp_chunk 
        cgpt_only_output += temp_chunk

    yield accum, accum, 'Finished ChatGPT generation'

    return cgpt_only_output, accum
