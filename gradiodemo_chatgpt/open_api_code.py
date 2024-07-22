import base64
import openai
import pdb
import pandas as pd
import codecs
from striprtf.striprtf import rtf_to_text

# Check https://github.com/openai/openai-python for the latest version of the OpenAI Python library.
# TODO: update to use better interface since this began based on information from ChatGPT that was all out of date
# for an old version of the API that is now invalid and there are probably better ways to do this.


def convert_rtf_to_text(rtf_file_path):
    with open(rtf_file_path, 'r') as file:
        rtf_content = file.read()
    text = rtf_to_text(rtf_content)
    return text


def read_first_of_file(file_path):
    try:
        with open(file_path, 'rb') as file:
            content = file.read(50000)
            # If you need the content as a string, uncomment the next line
            content = content.decode('utf-8')
        return content
    except FileNotFoundError:
        print("The file was not found.")
        return None
    except UnicodeDecodeError:
        # could raise an error if the file is not a text file here
        return content.decode('iso-8859-1')


def generate(from_file, system_info, prompt, api_key):
    if from_file.endswith('.xlsx') or from_file.endswith('.xls'):
        df = pd.read_excel(from_file)
        csv_content = df.to_string()[0:10000]
    elif from_file.endswith('.tsv'):
        df = pd.read_csv(from_file, sep='\t')
        csv_content = df.to_string()[0:10000]
    elif from_file.endswith('.rtf'):
        csv_content = convert_rtf_to_text(from_file)[0:10000]
    else:
        csv_content = read_first_of_file(from_file)[0:10000]

    client = openai.OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_info},
            {"role": "user", "content": prompt + '\n\n' + csv_content}
        ],
        # prompt=textsi_1,
        max_tokens=2048  # Adjust the max tokens based on your needs
    )

    return response.choices[0].message.content
