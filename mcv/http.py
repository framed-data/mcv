"""HTTP"""

import requests
import tempfile


def get_file(url, params={}):
    local = tempfile.TemporaryFile()
    r = requests.get(url, stream=True, params=params)
    with open(local.name, 'wb') as f:
        for chunk in r.iter_content(chunk_size=256 * 1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    return local
