"""Utilities for using Vagrant as a remote"""

import subprocess
import mcv.util
import mcv.remote
import paramiko


def _get_ssh_config():
    return subprocess.Popen(
            ['vagrant', 'ssh-config'], stdout=subprocess.PIPE).communicate()[0]


def _parse_ssh_config(vagrant_ssh_output):
    return dict(
        [l.strip().split(' ')
         for l
         in vagrant_ssh_output.strip().split('\n')])


def ssh_config():
    return _parse_ssh_config(_get_ssh_config())


def _conn_spec_bare(vagrant_ssh_config):
    v = vagrant_ssh_config
    return {'username': v['User'],
            'host': v['HostName'],
            'port': int(v['Port']),
            'key_filename': v['IdentityFile'],
            'host_keys_path': v['UserKnownHostsFile'],
            'missing_host_key_policy': paramiko.AutoAddPolicy()}


def _conn_spec(vagrant_ssh_config, overrides):
    return mcv.util.merge_dicts(
        mcv.remote.conn_spec(),
        _conn_spec_bare(vagrant_ssh_config),
        overrides)


def conn_spec(overrides={}):
    """Return a connection spec for connecting to the local Vagrant"""
    return _conn_spec(ssh_config(), overrides)
