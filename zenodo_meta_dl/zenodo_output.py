import requests
import json
import time
import secrets

all_records = []

ranges = [['2024-12-01', '2024-12-31'], ['2024-11-01', '2024-11-30']]

for r in ranges:
    the_start = r[0]
    the_end = r[1]

    zenodo_range = f'[{the_start} TO {the_end}]'

    page = 0

    # see https://help.zenodo.org/guides/search/

    response = requests.get('https://zenodo.org/api/records',
                            params={'sort': 'newest', 'q': f'created:{zenodo_range}', 'resource_type': 'dataset',
                                    'size': 100, 'access_token': secrets.TOKEN})
    info = response.json()

    print('getting page 1 of range:', zenodo_range)

    while True:
        # ['hits']['hits'] is a list of datasets
        # ['hits']['hits'][0]['metadata'] is the metadata for the first dataset
        # ['links']['next'] is the next page (if it exists)
        hits = info.get("hits", {}).get("hits", [])

        print('results page:', info['links']['self'])

        all_records.extend(hits)

        time.sleep(2)  # To prevent hitting the API limits by too many requests

        if info['links'].get('next') is None:
            break

        # munge the access token as last param since the next page link doesn't include it
        response = requests.get(f"{info['links']['next']}&access_token={secrets.TOKEN}",
                                headers={"accept": "application/json"})

        info = response.json()

# Write to a JSON file
output_file = "zenodo_records.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(all_records, f, indent=2)  # Pretty-print with indentation

print(f"Total records collected: {len(all_records)}")
print(f"Data saved to {output_file}")

print('done')
