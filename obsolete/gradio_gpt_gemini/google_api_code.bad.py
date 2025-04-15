import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason
import vertexai.preview.generative_models as generative_models
import pdb
import config
import mimetypes
import file_reading_util


def generate(file_paths, system_info, prompt, starting_text='', frict_info=''):
    readme_file, data_file = file_reading_util.readme_and_data(file_paths)
    data_content = file_reading_util.get_csv_content(data_file)
    readme_content = None

    # for larger files and using their special storage, this URL seems to document how to do it
    # https://cloud.google.com/vertex-ai/docs/python-sdk/data-classes

    if readme_file is not None:
        readme_content = file_reading_util.get_csv_content(readme_file)
        readme_content = f'README FILE\n---\n{readme_content}\n---\n'
        readme_content = Part.from_data(mime_type="text/plain", data=readme_content.encode('utf-8'))
    if frict_info:
        frict_info = f'Report from Frictionless data validation\n---\n{frict_info}\n---\n'
    data_content = f'DATA FILE\n---\n{data_content}\n---\n'
    data_content = Part.from_data(mime_type="text/csv", data=data_content.encode('utf-8'))

    parts = [item for item in [readme_content, data_content, frict_info, prompt] if item]

    vertexai.init(project=config.get('google_project'), location=config.get('google_location'))

    generation_config = {"max_output_tokens": 8192, "temperature": 0.5, "top_p": 0.95}

    # or may need to use BLOCK_NONE, it was blocking some things about female whale reproduction or something
    safety_settings = {
        generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH:
            generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT:
            generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT:
            generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT:
            generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    }

    model = GenerativeModel(
        "gemini-2.0-flash",
        system_instruction=[system_info]
    )

    responses = model.generate_content(
        parts,
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True,
    )

    out_text = starting_text

    yield out_text, out_text, 'Running'
    for response in responses:
        out_text += response.text
        yield out_text, out_text, 'Running Gemini generation'
        print(response.text, end="")

