import requests
import json
import pdb
import pandas as pd
import time
import output_util

# Metadata from the API for December 2019
TARGET_YYYY_MM = '2019-12'

# restart at page 302 once I've been unthrottled
# getting metadata from the API for every record to find those from TARGET_YYYY_MM
response = requests.get('https://datadryad.org/api/v2/datasets', params={
    "page": 1, "per_page": 100}, headers={"accept": "application/json"})
info = response.json()

while True:
    print(info['_links']['self']['href'])
    for dataset in info['_embedded']['stash:datasets']:
        # print(dataset['publicationDate'])
        if dataset.get('publicationDate') is None:
            continue
        yyyy_mm = dataset['publicationDate'][:-3]

        if yyyy_mm == TARGET_YYYY_MM:
            print(dataset['publicationDate'], dataset['identifier'], dataset['title'])
            output_util.output_dryad_to_files(dataset)

    time.sleep(3)

    if info['_links'].get('next') is None:
        break

    response = requests.get(f"https://datadryad.org{info['_links']['next']['href']}",
                            headers={"accept": "application/json"})
    info = response.json()
