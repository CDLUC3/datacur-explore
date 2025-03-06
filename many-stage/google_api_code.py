import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason
import vertexai.preview.generative_models as generative_models
import pdb
import config
import mimetypes
import file_reading_util


def generate(file_context, system_info, prompt, starting_text=''):

    # for larger files and using their special storage, this URL seems to document how to do it
    # https://cloud.google.com/vertex-ai/docs/python-sdk/data-classes

    parts = [item for item in [prompt, file_context] if item]

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
        "gemini-1.5-flash-001",
        system_instruction=[system_info]
    )

    responses = model.generate_content(
        parts,
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True,
    )

    out_text = starting_text
    google_only_text = ''

    yield out_text, out_text, 'Running'
    for response in responses:
        out_text += response.text
        google_only_text += response.text
        yield out_text, out_text, 'Running Gemini generation'
        print(response.text, end="")

    return google_only_text, out_text
