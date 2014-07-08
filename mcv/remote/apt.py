import mcv.remote
import mcv.apt

import sys

def _status(ssh, pkg, verbose=False):
    raw_out, err, exit = mcv.remote.execute(ssh, mcv.apt._dpkg_query_cmd(pkg))
    out = raw_out + "\n" # dpkg output by default has no newline
    if verbose:
        sys.stdout.write(out)
        sys.stderr.write(err)
    return mcv.apt._dpkg_status(out)

def status(ssh, pkgs, verbose=False):
    return { p:_status(ssh, p, verbose=verbose) for p in pkgs }

def _install(ssh, pkgs):
    if not pkgs:
        return (None, None, None)

    return mcv.remote.execute(ssh, [mcv.apt.apt_cmd, 'install', '-y'] + pkgs, sudo=True)

def install(ssh, pkgs, verbose=False):
    installed_packages = status(ssh, pkgs)
    pkgs_to_install = [p for p in pkgs if not installed_packages[p]]

    return _install(ssh, pkgs_to_install)

