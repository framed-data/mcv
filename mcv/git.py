"""Git-related utilities"""

import os
import mcv.file
import sys
import subprocess
import tempfile
from contextlib import contextmanager
import itertools


def lines_to_string(lines):
    return "".join(" ".join(l) + "\n" for l in lines)


@contextmanager
def git_ssh_env(key_path, opts={}):
    """Return an environment dictionary that has been setup with
    the proper GIT_SSH set to enable git commands with SSH configured
    properly.

    Takes a path to an SSH private key,
    and a dictionary opts={} which contains SSH -o options,
    as explained in man pages for ssh_config(5)
    """
    opt_pairs = [['-o', "{0}={1}".format(k, v)] for k, v in opts.iteritems()]
    opts_chained = [o for o in itertools.chain(*opt_pairs)]

    temp_ssh_script = lines_to_string(
        [["#!/bin/sh"],
         ["exec", "/usr/bin/ssh", "-i", key_path] + opts_chained + ["\"$@\""]])
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(temp_ssh_script)
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

        retval = subprocess.call(cmd, cwd=path, stdout=stdout, stderr=stderr)
    return retval == 0


def clone(repo_url, repo_path, key_path=None, ssh_opts={}):
    """Clone git repo from remote `repo_url` to local `repo_path`

    Takes a path to an SSH private key file, and an dictionary
    of ssh -o options, as explained in man for ssh_config(5)"""
    if not repo_exists(repo_path):
        cmd = ['git', 'clone', repo_url, repo_path]
        if key_path:
            with git_ssh_env(key_path, opts=ssh_opts) as env:
                return subprocess.call(cmd, env=env)
        else:
            return subprocess.call(cmd)


def fetch(repo_path, key_path, ssh_opts={}):
    """Fetch a local git repo at path `repo_path`

    Takes a path to an SSH private key file, and an dictionary
    of ssh -o options, as explained in man for ssh_config(5)"""
    with git_ssh_env(key_path, opts=ssh_opts) as env:
        return subprocess.call(
            ['git', 'fetch'],
            cwd=repo_path,
            stdout=sys.stdout,
            stderr=sys.stderr,
            env=env)


def _show_ref(repo_path):
    return subprocess.Popen(
            ['git', 'show-ref'],
            stdout=subprocess.PIPE,
            cwd=repo_path).communicate()[0]


def _refs(show_ref_output):
    lines = map(lambda l: l.split(), show_ref_output.strip().split('\n'))
    return dict([[ref, commit] for commit, ref in lines])


def refs(repo_path):
    return _refs(_show_ref(repo_path))


def current_rev(repo_path, ref='refs/remotes/origin/master'):
    """Return the commit ID of a ref, usually to find the latest commit ID"""
    return refs(repo_path)[ref]


def export(repo_path, deploy_path, rev, opts={}):
    """Export a copy of the contents of the git repo
    from local `repo_path` at revision `rev` to the local
    directory `deploy_path`.  Does not include the git metadata."""
    if not os.path.exists(deploy_path):
        mcv.file.mkdir(
            deploy_path,
            opts=mcv.util.merge_dicts(
                {'parents': True},
                mcv.util.select_keys(opts, ['mode', 'owner', 'group'])))

        cmd_tmpl = "git archive {rev} | tar -x -C {dir}"
        cmd = cmd_tmpl.format(rev=rev, dir=deploy_path)
        out = subprocess.Popen(
                cmd,
                cwd=repo_path,
                shell=True,
                stdout=subprocess.PIPE).communicate()[0]
        mcv.file.ch_ext(
            deploy_path,
            mcv.util.merge_dicts(
                {'recursive': True},
                mcv.util.select_keys(opts, ['owner', 'group'])))
        return out
