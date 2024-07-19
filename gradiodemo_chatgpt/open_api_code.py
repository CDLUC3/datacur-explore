import base64
import openai
import pdb
import local_secrets
import pandas as pd

# Check https://github.com/openai/openai-python for the latest version of the OpenAI Python library.
# TODO: update to use better interface since this began based on information from ChatGPT that was all out of date
# for an old version of the API that is now invalid and there are probably better ways to do this.

def generate(from_file, system_info, prompt):
    df = pd.read_csv(from_file)

    csv_content = df.to_string()[0:10000]

    client = openai.OpenAI(api_key=local_secrets.OPENAI_API_KEY)

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
