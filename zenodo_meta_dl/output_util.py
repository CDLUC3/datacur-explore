import json
import re
import os
import requests
import pdb
import time
import secrets

# BASE_URL = 'https://datadryad.org'
DATACITE_URL = 'https://data.datacite.org/application/vnd.datacite.datacite+json/'
HEADERS = {"accept": "application/json"}
SUFFIXES = ('.csv', '.xlsx', '.xls', '.tsv', '.txt', '.md', '.rtf')

def sanitize_filename(filename):
    # Define allowed characters, remove unsafe characters
    sanitized = re.sub(r'[^a-zA-Z0-9\-_. ]', '_', filename)

    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')

    # Truncate to 255 characters to avoid filesystem limits
    sanitized = sanitized[:255]

    # Handle special case where filename could become empty
    if not sanitized:
        sanitized = "default_filename"

    # Handle potential reserved filenames for Windows
    reserved_names = {"CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8",
                      "COM9", "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"}
    if sanitized.upper() in reserved_names:
        sanitized = "_" + sanitized

    return sanitized


def download_file(url, filename):
    # Send a GET request to the URL
    response = requests.get(url, stream=True)

    # Check if the request was successful
    if response.status_code == 200:
        # Open a local file with the same name as in the URL in binary write mode
        with open(filename, 'wb') as file:
            # Write the content of the response to the file
            for chunk in response.iter_content(chunk_size=128):
                file.write(chunk)
    else:
        print(f"Failed to download the file. Status code: {response.status_code}")


def output_zenodo_to_files(hit):
    fn_doi = sanitize_filename(hit['doi'])

    directory_path = f"output/{fn_doi}"
    os.makedirs(directory_path, exist_ok=True)  # Ensure the directory exists

    with open(f"output/{fn_doi}/zenodo_hit.json", 'w') as f:
        json.dump(hit, f, indent=2)

    with open(f"output/{fn_doi}/zenodo_bare_meta.json", 'w') as f:
        json.dump(hit['metadata'] , f, indent=2)

    # get the files for this dataset that are of the correct type and size
    for file_info in hit['files']:
        if file_info['key'].endswith(SUFFIXES) and 0 < file_info['size'] < 5.0e+8:  # 500 MB
            download_url = f"{file_info['links']['self']}?access_token={secrets.TOKEN}"
            print(f"  Downloading {file_info['key']}, {file_info['size']} bytes")
            download_file(download_url, f"output/{fn_doi}/{file_info['key']}")
            time.sleep(5)  # To prevent hitting the API limits by too many requests



    # get specific version info for this version
    # response = requests.get(f"{BASE_URL}{dataset['_links']['stash:version']['href']}",
    #                         headers=HEADERS)
    #
    # version_info = response.json()
    #
    # time.sleep(5)
    #
    # page = f"{BASE_URL}{version_info['_links']['stash:files']['href']}"
    #
    # counter = 1
    # while True:
    #     # Get the files info for the current page
    #     response = requests.get(page, headers=HEADERS)
    #     json_response = response.json()
    #
    #     # save the files info to a json file
    #     with open(f"output/{fn_doi}/dryad_file_info-page{counter}.json", 'w') as f:
    #         json.dump(json_response, f, indent=2)
    #
    #     # go through every file in response
    #     for file_info in json_response['_embedded']['stash:files']:
    #         if file_info['status'] != 'deleted' and file_info['path'].endswith(SUFFIXES) and \
    #                 file_info['_links'].get('stash:download') is not None and \
    #                 0 < file_info['size'] < 5.0e+8:  # 500 MB
    #             download_url = f"{BASE_URL}{file_info['_links']['stash:download']['href']}"
    #             print(f"  Downloading {file_info['path']}, {file_info['size']} bytes")
    #             download_file(download_url, f"output/{fn_doi}/{file_info['path']}")
    #             time.sleep(5)  # To prevent hitting the API limits by too many requests
    #
    #     if '_links' in json_response and 'next' in json_response['_links']:
    #         page = f"{BASE_URL}{json_response['_links']['next']['href']}"
    #         counter += 1
    #     else:
    #         break

    dc_json = datacite_json_metadata(hit['doi'])
    if dc_json:
        with open(f"output/{fn_doi}/datacite_meta.json", 'w') as f:
            json.dump(dc_json, f, indent=2)


def datacite_json_metadata(doi):
    base_url = "https://data.datacite.org/application/vnd.datacite.datacite+json/"
    url = f"{base_url}{doi}"
    headers = {"Accept": "application/vnd.datacite.datacite+json"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        metadata = response.json()
        return metadata
    else:
        print(f"Failed to download json metadata for {doi} Status code: {response.status_code}")
        return None

