import subprocess
import sys
import re
import os
import distutils.spawn


def _pip_cmd():
    return distutils.spawn.find_executable('pip')


def _status(pip_output):
    return dict([l.split('==')
                 for l
                 in pip_output.split('\n')
                 if l and not l.startswith('#')])


def status(pkgs):
    cmd = [_pip_cmd(), 'freeze']
    out = subprocess.Popen(
            cmd, stdout=subprocess.PIPE).communicate()[0].strip()
    installed = _status(out)
    return dict((p, installed.get(p)) for p in pkgs)


def _install_cmd(pkgs, upgrade=False):
    if not pkgs:
        return None

    opt_upgrade = ['--upgrade'] if upgrade else []

    return [_pip_cmd(), 'install'] + opt_upgrade + pkgs


def install(pkgs, upgrade=False):
    installed_packages = status(pkgs)
    pkgs_to_install = [p for p in pkgs if not installed_packages[p]]

    cmd = _install_cmd(pkgs_to_install, upgrade=upgrade)

    if cmd:
        return subprocess.call(cmd, stdout=sys.stdout, stderr=sys.stderr)
    else:
        return None
