from repo_interface import RepoInterface
import requests
import urllib.parse
import json
import pdb

BASE_URL = 'https://datadryad.org'

HEADERS = {"accept": "application/json"}

# import dryad_api
# da = dryad_api.DryadApi('10.5061/dryad.8pk0p2nn9')
# da.get_metadata()
# da.get_filenames_and_links()
# da.id_exists()

class DryadApi(RepoInterface):
    def __init__(self, doi):
        self.doi = doi

    def id_exists(self):
        return not (self.get_metadata() is None)

    def get_metadata(self):
        response = requests.get(f'{BASE_URL}/api/v2/datasets/doi:{urllib.parse.quote(self.doi, safe="")}')
        if response.status_code != 200:
            return None
        info = response.json()
        return info

    def get_filenames_and_links(self):
        meta = self.get_metadata()
        response = requests.get(f"{BASE_URL}{meta['_links']['stash:version']['href']}",
                                headers=HEADERS)
        version_info = response.json()

        page = f"{BASE_URL}{version_info['_links']['stash:files']['href']}"

        file_list = []

        # go through all the pages of files for this version
        while True:
            # Get the files info for the current page
            response = requests.get(page, headers=HEADERS)
            json_response = response.json()

            # go through every file in response
            for file_info in json_response['_embedded']['stash:files']:
                if file_info['status'] != 'deleted' and file_info['_links'].get('stash:download') is not None:
                    download_url = f"{BASE_URL}{file_info['_links']['stash:download']['href']}"
                    file_list.append({file_info['path']: download_url})

            if '_links' in json_response and 'next' in json_response['_links']:
                page = f"{BASE_URL}{json_response['_links']['next']['href']}"
            else:
                break

        return file_list
