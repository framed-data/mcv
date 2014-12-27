"""CircleCI"""

import mcv.http
import requests


def artifacts(token, username, project, build_num):
    """Retrieve a list of build artifacts"""

    url = "/".join([
        "https://circleci.com/api/v1/project",
        username,
        project,
        str(build_num),
        "artifacts"])

    r = requests.get(
        url,
        params={'circle-token': token},
        headers={'accept': 'application/json'})
    return r.json()


def get_file(token, url):
    return mcv.http.get_file(url, params={'circle-token': token})
