import mcv.pip
import mcv.remote
import sys
import re
import os

pip_cmd = "/usr/bin/pip"


def status(ssh, pkgs):
    out, err, exit = mcv.remote.execute(ssh, mcv.pip.pip_list_cmd)
    installed = mcv.pip._status(out)
    return dict((p, installed.get(p)) for p in pkgs)


def install(ssh, pkgs, sudo=False, upgrade=False):
    installed_packages = status(ssh, pkgs)
    pkgs_to_install = [p for p in pkgs if not installed_packages[p]]

    cmd = mcv.pip._install_cmd(pkgs_to_install, upgrade=upgrade)

    if cmd:
        return mcv.remote.execute(ssh, cmd, sudo=sudo)
    else:
        return None
