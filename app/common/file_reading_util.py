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
from app.common.path_utils import get_app_path
from app.repositories.repo_factory import repo_factory
import app.config as config


# yield to this to give updates progress while downloading
def download_files(file_chooser, input_method, doi_input):
    if input_method == 'Upload file':
        # get the file paths
        fns = [file.name for file in file_chooser]
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
        repo = repo_factory(doi)
    except ValueError as e:
        err = f"Error loading DOI: {e}"
        return err

    if not repo.id_exists():
        err = f"DOI {doi} not found."
        return err

    file_list = repo.get_filenames_and_links()
    return file_list


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
    
    
def get_texty_content(from_file):
    if from_file.endswith('.xlsx') or from_file.endswith('.xls'):
        df = pd.read_excel(from_file)
        texty_content = df.to_string()[0:5000]
    elif from_file.endswith('.tsv'):
        df = pd.read_csv(from_file, sep='\t')
        texty_content = df.to_string()[0:5000]
    elif from_file.endswith('.rtf'):
        texty_content = convert_rtf_to_text(from_file)[0:5000]
    else:
        texty_content = read_first_of_file(from_file)[0:5000]

    # remove any incomplete lines at the end if it's a tabular file so it doesn't cause data quality issues if examining
    if (from_file.endswith('.xlsx') or from_file.endswith('.xls') or from_file.endswith('.tsv') or \
        from_file.endswith('.csv')) and "\n" in texty_content:
        lines = texty_content.split('\n')
        if len(lines) > 1 and not lines[-1].strip():
            texty_content = '\n'.join(lines[:-1])  # remove the last empty line

    return texty_content


# Helper to obtain and cache a Dryad OAuth token (stored under key 'token' in config)
def _get_dryad_token(force_refresh=False):
    # Use cached token if available and not expired unless force_refresh is True
    if not force_refresh:
        token = config.get('token')
        expires_at = config.get('token_expires_at')
        try:
            if token and expires_at and time.time() < float(expires_at) - 10:
                return token
        except Exception:
            # If any issue reading expiry, fall through to refresh
            pass

    client_id = config.get('dryad_api_key')
    client_secret = config.get('dryad_secret')

    if not client_id or not client_secret:
        raise RuntimeError('Dryad API credentials are not configured (dryad_api_key/dryad_secret)')

    token_url = 'https://datadryad.org/oauth/token'

    # First try client credentials with HTTP Basic auth (common OAuth pattern)
    try:
        resp = requests.post(token_url,
                             data={'grant_type': 'client_credentials'},
                             auth=(client_id, client_secret),
                             timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            token = data.get('access_token') or data.get('token')
            expires_in = data.get('expires_in')
        else:
            # Fallback: send client_id/client_secret in body
            resp = requests.post(token_url,
                                 data={'grant_type': 'client_credentials',
                                       'client_id': client_id,
                                       'client_secret': client_secret},
                                 timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                token = data.get('access_token') or data.get('token')
                expires_in = data.get('expires_in')
            else:
                raise RuntimeError(f'Failed to obtain Dryad token (status {resp.status_code}): {resp.text}')
    except requests.RequestException as e:
        raise RuntimeError(f'Error requesting Dryad token: {e}')

    if not token:
        raise RuntimeError('Dryad token not found in token response')

    # Cache token and expiry (if provided) for future calls
    config.set('token', token)
    try:
        if expires_in:
            expires_at = time.time() + int(expires_in)
            config.set('token_expires_at', expires_at)
    except Exception:
        # ignore expiry caching errors
        pass
    return token


def download_file(url, filename=None):
    max_size = 300 * 1024 * 1024  # 300MB in bytes
    chunk_size = 1024  # 1KB

    directory = get_app_path('dl_files')

    # Create a temporary file or use the specified filename
    if filename:
        temp_file_path = os.path.join(directory, filename)
    else:
        temp_file = tempfile.NamedTemporaryFile(delete=False, dir=directory)
        temp_file_path = temp_file.name

    # Prepare headers; add Authorization header only for datadryad.org downloads
    headers = {}
    is_dryad = url.startswith('https://datadryad.org')
    if is_dryad:
        token = _get_dryad_token()
        headers['Authorization'] = f'Bearer {token}'

    # Attempt the download. If it fails for Dryad due to connection error or 401/403,
    # refresh token once and retry exactly one time before giving up.
    tried_refresh = False
    while True:
        try:
            response = requests.get(url, stream=True, headers=headers)
        except requests.RequestException as e:
            if is_dryad and not tried_refresh:
                # Try refreshing token once and retry
                token = _get_dryad_token(force_refresh=True)
                headers['Authorization'] = f'Bearer {token}'
                tried_refresh = True
                continue
            else:
                # Non-dryad or already retried: propagate
                raise

        # If Dryad responded with unauthorized/forbidden, try refreshing token once then retry
        if is_dryad and response.status_code in (401, 403) and not tried_refresh:
            tried_refresh = True
            try:
                token = _get_dryad_token(force_refresh=True)
                headers['Authorization'] = f'Bearer {token}'
            except Exception:
                # If refresh failed, raise the HTTP error
                response.raise_for_status()
            # Retry the request once with refreshed token
            continue

        # Otherwise we have a usable response (or non-Dryad response)
        break

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
