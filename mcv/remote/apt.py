import mcv.remote
import mcv.apt

import sys


def _status(ssh, pkg):
    raw_out, err, exit = mcv.remote.execute(ssh, mcv.apt._dpkg_query_cmd(pkg))
    out = raw_out + "\n"  # dpkg output by default has no newline

    return mcv.apt._dpkg_status(out)


def status(ssh, pkgs):
    return dict((p, _status(ssh, p)) for p in pkgs)


def _install(ssh, pkgs):
    if not pkgs:
        return (None, None, None)

    return mcv.remote.execute(
        ssh,
        [mcv.apt.apt_cmd, 'install', '-y'] + pkgs,
        sudo=True)


def install(ssh, pkgs):
    installed_packages = status(ssh, pkgs)
    pkgs_to_install = [p for p in pkgs if not installed_packages[p]]

    return _install(ssh, pkgs_to_install)


def update(ssh):
    return mcv.remote.execute(
        ssh,
        mcv.apt.update_cmd,
        sudo=True)
