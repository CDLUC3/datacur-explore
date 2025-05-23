# utils.py
import os
import pdb

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

# I was originally going to just have it update the markdown, but it doesn't update if only updated by itself.
# The docs state that only textboxes are guaranteed to update, so I was going to update the textbox and switch it for
# markdown on completion. However, I found that if I included both outputs, it would update the markdown as well.
# I hope this behavior continues to work as expected since it doesn't seem to be explicitly intended.

# The three outputs it has to yield and update are textbox, markdown and status_output (in that order)
def process_file_and_return_markdown(file, system_info, user_prompt, user_prompt2, input_method, select_file, choices,
                                     doi_input):
    file_paths, message = file_reading_util.file_setup(input_method, file, select_file, choices)
    yield '', '', message, None
    if len(file_paths) == 0:
        return


    datafile_path = file_reading_util.find_file_with_tabular(file_paths)

    accum = ''

    if doi_input and input_method == 'Dryad or Zenodo DOI':
        accum += f"# DOI: {doi_input}\n\n"


    # ************************************
    # --- Frictionless data validation ---
    # ************************************

    # yield accum, accum, "Running Frictionless examination...", None
    # frict_info = frictionless_util.get_output(datafile_path)  # this may take a while on large files
    # if frict_info == "":
    frict_info = "No issues reported using the default Frictionless consistency checks."
    #
    # accum += f'---\n\n## Report from frictionless data validation\n\n{frict_info}\n\n---\n\n'
    #
    # yield accum, accum, "Ran frictionless data validation...", None


    # *************************
    # --- Gemini processing ---
    # *************************

    yield accum, accum, "Starting gemini processing of frictionless and data file...", None
    
    accum += f"## Gemini Output\n\n---\n\n"

    file_context = ""
    file_context += f"## Frictionless validation\n\n{frict_info}\n\n"
    file_text = file_reading_util.get_texty_content(datafile_path)
    file_context += f"## Filename: {os.path.basename(datafile_path)}\n\n{file_text}\n\n"


    gen = google_api_code.generate(file_context, system_info, user_prompt, accum)

    try:
        while True:
            item = next(gen)
            yield (*item, None)  # Add a 4th item to match expected output
    except StopIteration as e:
        google_response, accum = e.value

    accum += f"\n\n---\n\n"

    yield accum, accum, "Done with gemini processing", None

    # ************************
    # --- GPT-4 processing ---
    # ************************

    accum = ''

    yield accum, accum, "Starting GPT-4 processing of Gemini and data file...", None

    # accum += f"\n\n## GPT-4 Output\n\n---\n\n"

    file_context = ""
    file_context += f"## Gemini output\n\n{google_response}\n\n"
    file_context += f"## Filename: {os.path.basename(datafile_path)}\n\n{file_text}\n\n"

    gen = open_api_code.generate(file_context, system_info, user_prompt2, accum)

    try:
        while True:
            item = next(gen)
            yield (*item, None)  # Add a 4th item to match expected output
    except StopIteration as e:
        cgpt_response, accum = e.value

    accum += f"\n\n---\n\n"

    # remove the uploaded files
    for file_path in file_paths:
        os.remove(file_path)

    dl_path = "output.md"
    with open("output.md", "w") as f:
        f.write(accum)

    yield accum, accum, f"Done with GPT-4 processing", dl_path


def submit_for_frictionless(file, option, input_method, select_file, choices, doi_input):
    file_paths, message = file_reading_util.file_setup(input_method, file, select_file, choices)
    yield '', '', message
    if len(file_paths) == 0:
        yield '', 'Some files must be chosen'
        return

    file_path = file_reading_util.find_file_with_tabular(file_paths)

    if file_path is None:
        yield '', "Only CSV and Excel files are supported."
        return

    accum = ''
    if doi_input and input_method == 'Dryad or Zenodo DOI':
        accum += f"# DOI: {doi_input}\n\n"

    accum += f"- Processing file: {os.path.basename(file_path)}\n\n"

    yield '', "Running Frictionless examination..."
    profiler = cProfile.Profile()
    profiler.enable()
    frict_info = frictionless_util.get_output(file_path)
    profiler.disable()

    # Print the profiling results
    result = StringIO()
    ps = pstats.Stats(profiler, stream=result).sort_stats(pstats.SortKey.CUMULATIVE)
    ps.print_stats()
    print(result.getvalue())

    if frict_info == "":
        frict_info = "No issues reported using the default Frictionless consistency checks."

    accum += f'## Report from frictionless data validation\n\n{frict_info}\n\n'
    yield accum, "Done"
