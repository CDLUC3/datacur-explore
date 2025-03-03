import pdb

import repo_factory
import pandas as pd
import codecs
from striprtf.striprtf import rtf_to_text
import mimetypes
import tempfile
import requests
import os
import threading
import time


# yield to this to give updates progress while downloading
def download_files(file_chooser, input_method, doi_input):
    if input_method == 'Upload file':
        # get the file paths
        file_paths = [file.name for file in file_chooser]
        for path in file_paths:
            yield '', '', os.path.basename(path)
            time.sleep(1)
    else:
        file_list = load_file_list(doi_input)
        if isinstance(file_list, str):  # error message rather than a list
            yield '', '', file_list
        else:  # download the files
            fns = []
            for file_info in file_list:
                fn = next(iter(file_info))
                the_url = file_info[fn]
                yield '', '', f"Downloading {fn}"
                file_path = download_file(the_url, fn)
                fns.append(file_path)
    return fns


# get the list of files for a Dryad or Zenodo DOI, they are formatted as a list of dicts
# with the filename as the key and the download URL as the value
def load_file_list(doi):
    if doi:
        doi = doi.strip()
    try:
        repo = repo_factory.repo_factory(doi)
    except ValueError as e:
        err = f"Error loading DOI: {e}"
        return err

    if not repo.id_exists():
        err = f"DOI {doi} not found."
        return err

    file_list = repo.get_filenames_and_links()
    return file_list


# preliminaries for working with file input
def file_setup(input_method, file, choices):
    if input_method == 'Upload file' and file is None:
        return [], "No file was uploaded."

    if input_method == 'Dryad or Zenodo DOI':
        # make dict of just the selected files and their urls as values
        file_urls = {file: choices.get(file) for file in select_file}

        # get paths of downloaded files
        file_paths = [ download_file(value, filename=key) for key, value in file_urls.items() ]
    else:
        file_paths = [ file.name ]
    return file_paths, 'Got files'

def convert_rtf_to_text(rtf_file_path):
    with open(rtf_file_path, 'r') as file:
        rtf_content = file.read()
    text = rtf_to_text(rtf_content)
    return text


def read_first_of_file(file_path):
    try:
        with open(file_path, 'rb') as file:
            content = file.read(50000)
            content = content.decode('utf-8')
        return content
    except FileNotFoundError:
        print("The file was not found.")
        return None
    except UnicodeDecodeError:
        # could raise an error if the file is not a text file here
        return content.decode('iso-8859-1')


def get_texty_content(from_file):
    if from_file.endswith('.xlsx') or from_file.endswith('.xls'):
        df = pd.read_excel(from_file)
        texty_content = df.to_string()[0:10000]
    elif from_file.endswith('.tsv'):
        df = pd.read_csv(from_file, sep='\t')
        texty_content = df.to_string()[0:10000]
    elif from_file.endswith('.rtf'):
        texty_content = convert_rtf_to_text(from_file)[0:5000]
    else:
        texty_content = read_first_of_file(from_file)[0:5000]

    return texty_content


def download_file(url, filename=None):
    max_size = 300 * 1024 * 1024  # 300MB in bytes
    chunk_size = 1024  # 1KB

    directory = 'dl_files'

    # Create a temporary file or use the specified filename
    if filename:
        temp_file_path = os.path.join(directory, filename)
    else:
        temp_file = tempfile.NamedTemporaryFile(delete=False, dir=directory)
        temp_file_path = temp_file.name

    # Download the file from the internet in chunks
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Check if the request was successful

    total_size = 0
    with open(temp_file_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:  # filter out keep-alive new chunks
                total_size += len(chunk)
                if total_size > max_size:
                    file.write(chunk[:max_size - total_size + len(chunk)])
                    break
                file.write(chunk)

    print(f"File downloaded and saved to: {temp_file_path}")

    # Schedule the file to be removed after 10 minutes
    # threading.Timer(600, os.remove, [temp_file_path]).start()

    return temp_file_path

def readme_and_data(file_paths):
    readme_file = None
    data_file = None

    for file_path in file_paths:
        temp_fp = file_path.lower()
        if 'readme' in temp_fp or file_path.endswith('.txt') or file_path.endswith('.md'):
            readme_file = file_path
        else:
            data_file = file_path

    return readme_file, data_file

def find_file_with_tabular(file_list):
    for file_path in file_list:
        if file_path.endswith(('.csv', '.xls', '.xlsx')):
            return file_path
    return None
