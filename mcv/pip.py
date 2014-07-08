import subprocess
import sys
import re
import os

pip_cmd = "/usr/bin/pip"

def status(pkgs):
    out = subprocess.check_output(['/usr/bin/pip', 'list']).strip()
    installed = dict([l.split() for l in out.split('\n')])
    return { p:installed.get(p) for p in pkgs }

def _install(pkgs):
    if not pkgs:
        return True

    cmd = [pip_cmd, 'install'] + pkgs
    retval = subprocess.call(cmd, stdout=sys.stdout, stderr=sys.stderr)
    return retval

def install(pkgs):
    installed_packages = status(pkgs)
    pkgs_to_install = [p for p in pkgs if not installed_packages[p]]
    return _install(pkgs_to_install)
