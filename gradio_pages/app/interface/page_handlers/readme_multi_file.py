import os

import app.llms.open_api_code as open_api_code
import app.llms.google_api_code as google_api_code
import app.llms.bedrock_llama as bedrock_llama
import gradio as gr
import app.common.file_reading_util as file_reading_util
import pdb

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

    # this extra wrapping around the generator is to allow us to yield from it for 4 items
    # instead of 3 which is what the generator yields, the StopIteration exception is used to
    # get the return value from the generator which is different than the yield value
    gen = file_reading_util.download_files(file_chooser, input_method, doi_input)

    try:
        while True:
            item = next(gen)
            yield (*item, None)  # Add a 4th item to match expected output
    except StopIteration as e:
        file_paths = e.value  # This is the return value from the generator

    if isinstance(file_paths, str):  # if it returns a string, it's an error message
        yield '', '', file_paths, None
        return

    accum = ''
    if doi_input and input_method == 'Dryad or Zenodo DOI':
        accum += f"# DOI: {doi_input}\n\n"

    file_context = ''
    for file_path in file_paths:
        file_content = file_reading_util.get_texty_content(file_path)
        file_context += f"## Filename: {os.path.basename(file_path)}\n\n{file_content}\n\n"

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
        # instead of 3 which is what the generator yields, the StopIteration exception is used to
        # get the return value from the generator

        gen = generator_fn(file_context, system_info, user_prompt, accum)
        try:
            while True:
                item = next(gen)
                yield (*item, None)  # Add a 4th item to match expected output
        except StopIteration as e:
            response, accum = e.value

        accum += f"\n\n---\n\n"

        yield accum, accum, f"Done with {llm_option} processing", None

    # remove the uploaded files
    for file_path in file_paths:
        os.remove(file_path)

    dl_path = "output.md"
    with open("output.md", "w") as f:
        f.write(accum)
    yield accum, accum, f"Done with {llm_option} processing", dl_path
