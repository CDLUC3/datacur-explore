import pdb

import pandas as pd
import codecs
from striprtf.striprtf import rtf_to_text
import mimetypes
import tempfile
import requests
import os
import threading
import time


# preliminaries for working with file input
def file_setup(input_method, file, select_file, choices):
    if input_method == 'Upload file' and file is None:
        return [], "No file was uploaded."
    elif input_method == 'Dryad or Zenodo DOI' and (len(select_file) == 0 or len(select_file) > 2):
        return [], "The doi needs to be looked up and README and data file selected."

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


def get_csv_content(from_file):
    if from_file.endswith('.xlsx') or from_file.endswith('.xls'):
        df = pd.read_excel(from_file)
        csv_content = df.to_string()[0:10000]
    elif from_file.endswith('.tsv'):
        df = pd.read_csv(from_file, sep='\t')
        csv_content = df.to_string()[0:10000]
    elif from_file.endswith('.rtf'):
        csv_content = convert_rtf_to_text(from_file)[0:10000]
    else:
        csv_content = read_first_of_file(from_file)[0:10000]

    return csv_content


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
