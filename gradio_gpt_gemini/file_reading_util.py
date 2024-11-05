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

    # Schedule the file to be removed after 3 minutes
    threading.Timer(180, os.remove, [temp_file_path]).start()

    return temp_file_path
