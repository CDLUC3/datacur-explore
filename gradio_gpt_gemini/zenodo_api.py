from repo_interface import RepoInterface
import requests
import urllib.parse
import json
import pdb

BASE_URL = 'https://zenodo.org/api/'

# import zenodo_api
# za = zenodo_api.ZenodoApi('10.5281/zenodo.13713417')
# za.get_metadata()
# za.get_filenames_and_links()
# za.id_exists()


class ZenodoApi(RepoInterface):
    def __init__(self, doi):
        self.doi = doi

    def id_exists(self):
        return not (self.get_metadata() is None)

    # maybe these work?
    # https://zenodo.org/api/records/10.5281/zenodo.12817126
    # https://zenodo.org/api/records/10.5281/zenodo.13713417

    def get_metadata(self):
        params = {
            'q': f'doi:{self.doi}'
        }
        response = requests.get(f'{BASE_URL}records', params=params)
        if response.status_code != 200:
            return None
        info = response.json()
        return info['hits']['hits'][0]

    def get_filenames_and_links(self):
        meta = self.get_metadata()
        files = meta['files']
        file_pairs = [{item['key']: item['links']['self']} for item in files]
        return file_pairs
