import os
import cProfile
import pstats
from io import StringIO

import app.llms.open_api_code as open_api_code
import app.llms.google_api_code as google_api_code
import app.common.file_reading_util as file_reading_util
import app.common.frictionless_util as frictionless_util  # Corrected import for frictionless_util
import app.llms.bedrock_llama as bedrock_llama  # Corrected import for bedrock_llama
import gradio as gr


# this is a bit confusing since we are yielding to outputs that update the gradio interface and there
# are three outputs because of quirks in how Gradio handles updates. I couldn't get it to update correctly unless
# I included both a markdown and a textbox representation of the same data.

# I was originally going to just have it update the markdown, but it doesn't update if only updated by itself.
# The docs state that only textboxes are guaranteed to update, so I was going to update the textbox and switch it for
# markdown on completion. However, I found that if I included both outputs, it would update the markdown as well.
# I hope this behavior continues to work as expected since it doesn't seem to be explicitly intended.

# The four outputs it has to yield and update are textbox, markdown, status_output and file_output (in that order)
def process_file_and_return_markdown(file, system_info, prompt, llm_option, input_method, select_file, choices,
                                     doi_input, include_frictionless):
    accum = ''

    file_paths, message = file_reading_util.file_setup(input_method, file, select_file, choices)
    yield '', '', message, None
    if len(file_paths) == 0:
        return

    frict_info = None
    if include_frictionless:
        frict_path = file_reading_util.find_file_with_tabular(file_paths)
        yield '', '', "Running Frictionless examination...", None
        frict_info = frictionless_util.get_output(frict_path)  # Corrected namespacing for frictionless_util


    # File processing of input files moved out of LLM client functions
    readme_file, data_file = file_reading_util.readme_and_data(file_paths)
    data_content = file_reading_util.get_texty_content(data_file)
    readme_content = ''


    data_content = f'DATA FILE\n---\n{data_content}\n---\n'

    if readme_file is not None:
        readme_content = file_reading_util.get_texty_content(readme_file)
        data_content += f'README FILE\n---\n{readme_content}\n---\n'
    if frict_info:
        data_content += f'Report from Frictionless data validation\n---\n{frict_info}\n---\n'

    if doi_input and input_method == 'Dryad or Zenodo DOI':
        accum += f"# DOI: {doi_input}\n\n"

    accum += f"- Processing file: {os.path.basename(data_file)}\n\n"

    yield accum, accum, "Starting LLM processing...", None

    llm_generators = {
        "GPT-4o": open_api_code.generate,
        "gemini-2.0-flash": google_api_code.generate,
        "llama3.1-70b": bedrock_llama.generate,
    }

    # Select the correct function based on llm_option
    generator_fn = llm_generators.get(llm_option)

    if generator_fn:
        # this extra wrapping around the generator is to allow us to yield from it for 4 items
        # instead of 3 which is what the generator yields from previously, the StopIteration exception is used to
        # get the final return value from the generator

        gen = generator_fn(data_content, system_info, prompt, accum)
        try:
            while True:
                item = next(gen)
                yield (*item, None)  # Add a 4th item to match expected output
        except StopIteration as e:
            response, accum = e.value

        # accum += f"\n\n---\n\n"

        yield accum, accum, f"Done with {llm_option} processing", None

    # Set the downloadable output at the end
    dl_path = "output.md"
    with open("output.md", "w") as f:
        f.write(accum)
    yield accum, accum, f"Done with {llm_option} processing", dl_path

    # remove the uploaded files
    for file_path in file_paths:
        os.remove(file_path)


# a standalone function to run Frictionless data validation without other processing
def submit_for_frictionless(file, option, input_method, select_file, choices, doi_input):
    file_paths, message = file_reading_util.file_setup(input_method, file, select_file, choices)
    yield '', '', message, None
    if len(file_paths) == 0:
        yield '', '', 'Some files must be chosen', None
        return

    file_path = file_reading_util.find_file_with_tabular(file_paths)

    if file_path is None:
        yield '', '', "Only CSV and Excel files are supported.", None
        return

    accum = ''
    if doi_input and input_method == 'Dryad or Zenodo DOI':
        accum += f"# DOI: {doi_input}\n\n"

    accum += f"- Processing file: {os.path.basename(file_path)}\n\n"

    yield '', '', "Running Frictionless examination...", None
    frict_info = frictionless_util.get_output(file_path)  # Corrected namespacing for frictionless_util

    if frict_info == "":
        frict_info = "No issues reported using the default Frictionless consistency checks."

    accum += f'## Report from frictionless data validation\n\n{frict_info}\n\n'

    # Set the downloadable output at the end
    dl_path = "output.md"
    with open("output.md", "w") as f:
        f.write(accum)

    yield accum, accum, "Done", dl_path

    # remove the uploaded files
    for file_path in file_paths:
        os.remove(file_path)
