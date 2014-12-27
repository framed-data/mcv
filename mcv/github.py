"""GitHub utility functions"""

from __future__ import absolute_import

import mcv.pip
import mcv.file
import mcv.http
import subprocess
import tarfile


def keys_uri(username):
    template = 'https://github.com/{username}.keys'
    return template.format(username=username)


def _archive_url(owner, repo, rev, auth=None):
    auth_str = ":".join(auth) + "@" if auth else ""
    fmt = "https://{}github.com/{}/{}/archive/{}.tar.gz"

    return fmt.format(auth_str, owner, repo, rev)


def get_archive_tarball(owner, repo, rev, **get_kwargs):
    """**get_kwargs: same keyword args used by mcv.http.get_file,
    which are the same as requests.get"""

    archive_url = _archive_url(owner, repo, rev)
    response, f = mcv.http.get_file(archive_url, **get_kwargs)
    return tarfile.open(fileobj=f, mode='r:gz') if f else None


def extract_tarball(tarfile, path):
    """Specialized tarball extractor that strips the first
    directory component from the tarball that GitHub puts in."""
    return subprocess.call(
        ['tar', 'zxvf',
         tarfile.name,
         '--strip-components', '1',
         '-C', path])


def pip_install(user, repo, rev, oauth):
    url = _archive_url(user, repo, rev, auth=(oauth, 'x-oauth-basic'))
    mcv.pip.install([url])


def deploy_repo(user, repo, rev, path, oauth):
    auth = (oauth, 'x-oauth-basic')
    tarball = get_archive_tarball(user, repo, rev, auth=auth)
    mcv.file.mkdir(path)
    extract_tarball(tarball, path)
