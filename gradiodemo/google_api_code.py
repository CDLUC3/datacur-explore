import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason
import vertexai.preview.generative_models as generative_models
import pdb
import local_secrets


def generate(from_file):
    with open(from_file, 'rb') as file:
        file_content = file.read()

    document1 = Part.from_data(mime_type="text/csv", data=file_content)

    vertexai.init(project=local_secrets.PROJECT, location=local_secrets.LOCATION)

    generation_config = {"max_output_tokens": 8192, "temperature": 0.5, "top_p": 0.95}

    safety_settings = {
        generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    }

    text1 = """What suggestions can you make to improve data quality for the data in the file? Please be specific about
    things you recommend changing and format the action items as a bulleted list."""

    textsi_1 = 'The file contains research data in tabular format. Analyze it for data ' \
               'quality metrics and to help visualize the data for other researchers in the same field.'

    model = GenerativeModel(
        "gemini-1.5-flash-001",
        system_instruction=[textsi_1]
    )
    responses = model.generate_content(
        [document1, text1],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True,
    )

    out_text = ""

    for response in responses:
        out_text += response.text
        print(response.text, end="")

    return out_text

