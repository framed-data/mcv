import subprocess
import sys
import re
import os

apt_cmd = "/usr/bin/apt-get"

# Some of the dpkg facilities are factored out so that they're usable
# both locally here and remotely by mcv.remote.apt
def _dpkg_query_cmd(pkg):
    return ["/usr/bin/dpkg-query", "-W", "-f", "'${Status}'", pkg]

def _dpkg_query_local(pkg):
    cmd = _dpkg_query_cmd(pkg)
    try:
        with open(os.devnull, 'w') as devnull:
            output = subprocess.check_output(cmd, stderr=devnull)
        return output
    except subprocess.CalledProcessError, e:
        return None

def _dpkg_status(dpkg_query_output):
    """Return the status of a package given its dpkg query output

    This is split out into separate components so that it's
    agnostic as to whether the dpkg output came from a local
    source or a remote one, e.g. see mcv.remote.apt"""
    normalized = dpkg_query_output.strip() if dpkg_query_output else None
    if not normalized:
        return None

    fields = normalized.split(' ')
    status = fields[2]

    if status == 'not-installed':
        return None
    else:
        return status

def status(pkgs):
    """Return the install status of the given packages."""
    return { p:_dpkg_status(_dpkg_query_local(p)) for p in pkgs }

def _install(pkgs):
    if not pkgs:
        return True

    retval = subprocess.call([apt_cmd, "install", "-y"] + pkgs, stdout=sys.stdout)
    return retval

def install(pkgs):
    installed_packages = status(pkgs)
    pkgs_to_install = [p for p in pkgs if not installed_packages[p]]
    return _install(pkgs_to_install)

def update():
    retval = subprocess.call([apt_cmd, "update"], stdout=sys.stdout)
    return retval
