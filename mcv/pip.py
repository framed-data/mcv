import subprocess
import sys
import re
import os

pip_cmd = "/usr/bin/pip"
pip_list_cmd = [pip_cmd, 'freeze']

def _status(pip_output):
    return dict([l.split('==')
                 for l
                 in pip_output.split('\n')
                 if l and not l.startswith('#')])

def status(pkgs):
    out = subprocess.check_output(pip_list_cmd).strip()
    installed = _status(out)
    return { p:installed.get(p) for p in pkgs }

def _install_cmd(pkgs, upgrade=False):
    if not pkgs:
        return None

    opt_upgrade = ['--upgrade'] if upgrade else []

    return [pip_cmd, 'install'] + opt_upgrade + pkgs

def install(pkgs, upgrade=False):
    installed_packages = status(pkgs)
    pkgs_to_install = [p for p in pkgs if not installed_packages[p]]

    cmd = _install_cmd(pkgs_to_install, upgrade=upgrade)

    if cmd:
        return subprocess.call(cmd, stdout=sys.stdout, stderr=sys.stderr)
    else:
        return None
