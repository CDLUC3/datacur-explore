from app.repositories.repo_interface import RepoInterface
import requests
import re
import app.config as config

BASE_URL = 'https://zenodo.org/api/'

# import zenodo_api
# za = zenodo_api.ZenodoApi('10.5281/zenodo.13713417')
# za.get_metadata()
# za.get_filenames_and_links()
# za.id_exists()


class ZenodoApi(RepoInterface):
    def __init__(self, doi):
        self.doi = self._fix_format_of_doi(doi)

    def id_exists(self):
        return not (self.get_metadata() is None)

    # maybe these work?
    # https://zenodo.org/api/records/10.5281/zenodo.12817126
    # https://zenodo.org/api/records/10.5281/zenodo.13713417

    def get_metadata(self):
        params = {
            'q': f'doi:{self.doi}'
        }
        ua = config.get('user_agent') or 'DataCurationExploration/0.1'
        headers = {
            "User-Agent": ua
        }
        response = requests.get(f'{BASE_URL}records', params=params, headers=headers)
        if response.status_code != 200:
            return None
        info = response.json()
        if info['hits']['total'] < 1:
            # try the fallback since the zenodo api is not consistent and doesn't return results
            # for some dois that are in the system

            fb = self._doi_fallback()
            if fb is None:
                return None
            return fb

        return info['hits']['hits'][0]

    def get_filenames_and_links(self):
        meta = self.get_metadata()
        files = meta['files']
        file_pairs = [{item['key']: item['links']['self']} for item in files]
        return file_pairs

    def _extract_zenodo_id(self):
        match = re.search(r'zenodo\.(\d+)$', self.doi)
        if match:
            return match.group(1)
        return None

    def _doi_fallback(self):
        # You can look up deposition ids which are often embedded in a doi in zenodo
        # and look up with URL like https://zenodo.org/api/records//5948843
        # but this is a major hack since why aren't some available to look up be search that
        # should be available?
        deposition_id = self._extract_zenodo_id()

        if deposition_id is None:
            return None

        ua = config.get('user_agent') or 'DataCurationExploration/0.1'
        headers = {"User-Agent": ua}
        response = requests.get(f'{BASE_URL}records/{deposition_id}', headers=headers)
        if response.status_code != 200:
            return None
        info = response.json()
        return info
