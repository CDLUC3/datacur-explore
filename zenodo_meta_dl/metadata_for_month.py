import requests
# import json
# import pdb
# import pandas as pd
import time
import output_util
import secrets

# Metadata from the API for December 2019
zenodo_range = '[2019-12-01 TO 2019-12-31]'

file_types = ('csv', 'xlsx', 'xls', 'tsv', 'txt', 'md', 'rtf')

page = 0

# created search works for Zenodo created:[2019-12-01 TO 2019-12-31], publication_date also does
# see https://help.zenodo.org/guides/search/

response = requests.get('https://zenodo.org/api/records',
                        params={'sort': 'newest', 'q': f'publication_date:{zenodo_range}', 'file_type': file_types,
                                'size': 100, 'access_token': secrets.TOKEN})
info = response.json()

print('getting page 1')

while True:
    # ['hits']['hits'] is a list of datasets
    # ['hits']['hits'][0]['metadata'] is the metadata for the first dataset
    # ['links']['next'] is the next page (if it exists)

    print('results page:', info['links']['self'])

    for hit in info['hits']['hits']:
        print(hit['metadata']['publication_date'], hit['metadata']['doi'], hit['metadata']['title'])

        # output the metadata and files
        output_util.output_zenodo_to_files(hit)

    time.sleep(5)  # To prevent hitting the API limits by too many requests

    if info['links'].get('next') is None:
        break

    # munge the access token as last param since the next page link doesn't include it
    response = requests.get(f"{info['links']['next']}&access_token={secrets.TOKEN}",
                            headers={"accept": "application/json"})

    info = response.json()

print('done')


