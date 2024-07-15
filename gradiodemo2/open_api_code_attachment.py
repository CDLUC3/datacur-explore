import base64
import openai
import pdb
import local_secrets
import pandas as pd

# Check https://github.com/openai/openai-python for the latest version of the OpenAI Python library.
# TODO: update to use better interface since this began based on information from ChatGPT that was all out of date
# for an old version of the API that is now invalid and there are probably better ways to do this.

CLIENT = openai.OpenAI(api_key=local_secrets.OPENAI_API_KEY)


def create_openai_file(from_file):
    # Read the file content
    with open(from_file, 'rb') as f:
        file_data = f.read()

    # Create a file in the OpenAI API
    response = CLIENT.files.create(file=file_data, purpose='assistants')

    return response.id  # Returns the ID of the created file


def generate(from_file):
    pdb.set_trace()
    file_id = create_openai_file(from_file)
    # df = pd.read_csv(from_file)
    # csv_content = df.to_string()[0:5000]

    sys_role = """You are a system helping a researcher analyze a file containing research data in tabular format.
         The objective is to give advice to improve the data quality for reuse and reproducibility by other researchers
         in the same field. Besides general practices, specific advice for improving the given file is most useful."""

    query = (
        'The file contains research data in tabular format. Analyze it for data '
        'quality metrics and to help visualize the data for other researchers in the same field. How can it be '
        'improved for reuse and reproducibility?')

    response = CLIENT.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": sys_role},
            {"role": "user", "content": query}
        ],
        file=file_id,
        # prompt=textsi_1,
        max_tokens=1000  # Adjust the max tokens based on your needs
    )

    pdb.set_trace()

    del_response = CLIENT.files.delete(file_id)

    pdb.set_trace()

    return response.choices[0].message.content
