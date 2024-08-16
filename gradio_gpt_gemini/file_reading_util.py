import pandas as pd
import codecs
from striprtf.striprtf import rtf_to_text
import mimetypes


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