"""GitHub utility functions"""

from __future__ import absolute_import

import mcv.http
import tarfile


def keys_uri(username):
    template = 'https://github.com/{username}.keys'
    return template.format(username=username)


def get_archive_tarball(owner, repo, rev, **get_kwargs):
    """**get_kwargs: same keyword args used by mcv.http.get_file,
    which are the same as requests.get"""

    archive_url = "/".join([
        "https://github.com",
        owner,
        repo,
        "archive",
        rev + ".tar.gz"])

    response, f = mcv.http.get_file(archive_url, **get_kwargs)
    return tarfile.open(fileobj=f, mode='r:gz') if f else None


def extract_tarball(tarfile, path):
    """Specialized tarball extractor that strips the first
    directory component from the tarball that GitHub puts in."""
    for tarinfo in tarfile.getmembers():
        subpath_ix = tarinfo.name.find("/")
        tarinfo.name = tarinfo.name[subpath_ix + 1:]
        tarfile.extract(tarinfo, path)
