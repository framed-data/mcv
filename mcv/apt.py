import subprocess
import sys
import re
import os

apt_cmd = "/usr/bin/apt-get"
update_cmd = [apt_cmd, 'update']


# Some of the dpkg facilities are factored out so that they're usable
# both locally here and remotely by mcv.remote.apt
def _dpkg_query_cmd(pkg):
    return ["/usr/bin/dpkg-query", "-W", "-f", "'${Status}'", pkg]


def _dpkg_query_local(pkg):
    cmd = _dpkg_query_cmd(pkg)
    try:
        with open(os.devnull, 'w') as devnull:
            output = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=devnull).communicate()[0]
        return output
    except subprocess.CalledProcessError, e:
        if e.returncode == 1:  # package not installed
            return None
        raise  # other errors/exceptions then actually raise


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


def key_exists(key_id, keyring='/etc/apt/trusted.gpg'):
    command = ['gpg', '--list-keys', '--primary-keyring', keyring]
    out = subprocess.Popen(command, stdout=subprocess.PIPE).communicate()[0]
    lines = out.split("\n")
    return any(key_id in l for l in lines)


def import_key(keyserver, key_id):
    if not key_exists(key_id):
        return subprocess.check_call(['apt-key', 'adv', '--keyserver',
                                      keyserver,
                                      '--recv',
                                      key_id])
    return True


def _source_list_path(list_name):
    filename = list_name if list_name.endswith('list') else list_name + ".list"
    return '/etc/apt/sources.list.d/{0}'.format(filename)


def add_source_list(list_name, lines):
    with open(_source_list_path(list_name), 'w') as f:
        if isinstance(lines, basestring):
            content = lines
        else:
            content = "".join([l + "\n" for l in lines])
        f.write(content)


def rm_source_list(list_name):
    os.unlink(_source_list_path(list_name))


def status(pkgs):
    """Return the install status of the given packages."""
    return dict((p, _dpkg_status(_dpkg_query_local(p))) for p in pkgs)


def _install(pkgs):
    if not pkgs:
        return True

    return subprocess.check_call([apt_cmd, "install", "-y"] + pkgs)


def install(pkgs):
    installed_packages = status(pkgs)
    pkgs_to_install = [p for p in pkgs if not installed_packages[p]]
    return _install(pkgs_to_install)


def update():
    retval = subprocess.call(update_cmd, stdout=sys.stdout)
    return retval
