import os

import app.llms.open_api_code as open_api_code
import app.llms.google_api_code as google_api_code
import gradio as gr
import cProfile
import pstats
import app.common.file_reading_util as file_reading_util
import app.common.frictionless_util as frictionless_util

# this is a bit confusing since we are yielding to outputs that update the gradio interface and there
# are three outputs because of quirks in how Gradio handles updates. I couldn't get it to update correctly unless
# I included both a markdown and a textbox representation of the same data.

# Inputs: file_chooser,
#   system_info -- the system conditioning text
#   user_prompt -- the text input by the user
#   llm_option -- "GPT-4o", "Gemini-1.5-flash-001", "llama3.1-70b"
#   input_method -- "Upload file" or "Dryad or Zenodo DOI"
#   doi_input -- the DOI textbox input for DOI
#   'choices' used to exist here and it was a dict of file names and URLs obtained from the Dryad or Zenodo DOI lookup
#       from checkboxes of files to process.  Instead, we now can just use all or a bunch of files that we can find as
#       inside of this function rather than being processed and chosen ahead of time.
# The three outputs it has to yield and update are textbox, markdown and status_output (in that order)
def process_file_and_return_markdown(file_chooser, system_info, user_prompt, llm_option,
                                     input_method, doi_input):

    file_paths = yield from file_reading_util.download_files(file_chooser, input_method, doi_input)

    if isinstance(file_paths, str):  # if it returns a string, it's an error message
        yield '', '', file_paths
        return

    accum = ''
    if doi_input and input_method == 'Dryad or Zenodo DOI':
        accum += f"# DOI: {doi_input}\n\n"

    file_context = ''
    for file_path in file_paths:
        file_content = file_reading_util.get_texty_content(file_path)
        file_context += f"## Filename: {os.path.basename(file_path)}\n\n{file_content}\n\n"

    yield accum, accum, "Starting LLM processing..."

    if llm_option == "GPT-4o":
        cgpt_response, accum = yield from open_api_code.generate(file_context, system_info, user_prompt, accum)
        accum += f"\n\n---\n\n"
        yield accum, accum, "Done with ChatGPT processing"

    elif llm_option == "gemini-2.0-flash":
        google_response, accum = yield from google_api_code.generate(file_context, system_info, user_prompt, accum)
        accum += f"\n\n---\n\n"
        yield accum, accum, "Done with gemini processing"

    elif llm_option == "llama3.1-70b":
        llama_response, accum = yield from bedrock_llama.generate(file_content, system_info, user_prompt, accum)
        accum += f"\n\n---\n\n"
        yield accum, accum, "Done with Llama processing"

    # remove the uploaded files
    for file_path in file_paths:
        os.remove(file_path)
