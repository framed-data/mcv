"""HTTP"""

import requests
import tempfile


def get_file(url, **kwargs):
    local = tempfile.NamedTemporaryFile()
    kwargs['stream'] = True
    r = requests.get(url, **kwargs)

    if r.status_code == 200:
        with open(local.name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=256 * 1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
    else:
        local = None

    return [r, local]
