"""Git-related utilities"""

import os
import mcv.file
import sys
import subprocess
import tempfile
from contextlib import contextmanager

@contextmanager
def git_ssh_env(key_path):
    """Return an environment dictionary that has been setup with
    the proper GIT_SSH set to enable git commands with SSH configured
    properly."""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write("#!/bin/sh\nexec /usr/bin/ssh -i {} \"$@\"\n".format(key_path))
    mcv.file.chmod(f.name, 0700)
    env = os.environ.copy()
    env['GIT_SSH'] = f.name
    yield env

def repo_exists(path, verbose='error'):
    if not os.path.exists(path):
        return False

    cmd = ['git', 'rev-parse', '--is-inside-work-tree']
    with open('/dev/null', 'w') as devnull:
        stdout = sys.stdout if verbose is True else devnull
        stderr = sys.stderr if verbose is True else devnull

        retval = subprocess.call(
                cmd,
                cwd=path,
                stdout=stdout,
                stderr=stderr)
    return retval == 0

def clone(repo_url, repo_path, key_path):
    if not repo_exists(repo_path):
        with git_ssh_env(key_path) as env:
            retval = subprocess.call(['git', 'clone', repo_url, repo_path], env=env)

def fetch(repo_path, key_path):
    with git_ssh_env(key_path) as env:
        return subprocess.call(
            ['git', 'fetch'],
            cwd=repo_path,
            stdout=sys.stdout,
            stderr=sys.stderr,
            env=env)

def current_rev(repo_path):
    return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo_path).strip()

def export(repo_path, deploy_path, rev, opts={'mode': 0777}):
    if not os.path.exists(deploy_path):
        mcv.file.mkdir(deploy_path, opts=opts)

        cmd = "git archive {rev} | tar -x -C {dir}".format(rev=rev, dir=deploy_path)
        out = subprocess.check_output(cmd, cwd=repo_path, shell=True)
        mcv.file.ch_ext(deploy_path, opts)
        return out
