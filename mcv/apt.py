import subprocess
import sys
import re
import os

apt_cmd = "/usr/bin/apt-get"

def _status(pkg):
    cmd = ["/usr/bin/dpkg-query", "-W", "-f", "${Status}", pkg]
    try:
        with open(os.devnull, 'w') as devnull:
            output = subprocess.check_output(cmd, stderr=devnull)
        fields = output.split(' ')
        status = fields[2]
        return status
    except subprocess.CalledProcessError, e:
        return None

def status(pkgs):
    return { p:_status(p) for p in pkgs }

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
