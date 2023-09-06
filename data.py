import sys
import requests
import json
import html

DUMMY = True
URL = 'https://api.spot-hinta.fi/TodayAndDayForward'
PLACEHOLDER = "__DATA_PLACEHOLDER__"


def fetch_data():
    print("fetching from " + URL)
    res = requests.get(URL)
    response = json.loads(res.text)
    return response


def fetch_data_dummy():
    print("using dummy fetch")
    with open('dummy.json', 'r', encoding='utf-8') as f:
        response = f.read()
    return json.loads(response)


def get_data():
    return fetch_data_dummy() if DUMMY else fetch_data()


def replace(inputFilename):
    data = get_data()
    with open(inputFilename, 'r+', encoding='utf-8') as f:
        existing = f.read()
        replaced = existing.replace(
            PLACEHOLDER, html.escape(json.dumps(data), quote=True))
        f.seek(0)
        f.write(replaced)
        f.truncate()
        print("Wrote " + inputFilename)


if __name__ == "__main__":
    replace(sys.argv[1])
