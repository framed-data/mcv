import mcv.pip
import mcv.remote
import sys
import re
import os

pip_cmd = "/usr/bin/pip"

def status(ssh, pkgs):
    out, err, exit = mcv.remote.execute(ssh, mcv.pip.pip_list_cmd)
    installed = mcv.pip._status(out)
    return { p:installed.get(p) for p in pkgs }

def _install(ssh, pkgs, sudo=False, verbose=False):
    if not pkgs:
        return True

    cmd = [pip_cmd, 'install'] + pkgs

    return mcv.remote.execute(ssh, cmd, sudo=sudo, verbose=verbose)

def install(ssh, pkgs, sudo=False, verbose=False):
    installed_packages = status(ssh, pkgs)
    pkgs_to_install = [p for p in pkgs if not installed_packages[p]]
    return _install(ssh, pkgs_to_install, sudo=sudo, verbose=verbose)
