"""Patchwork notifications library

This module implements minimal functionality for the Patchwork notification
service. It supports machine registration and package updates.

Attributes:
    PATCHWORK_API_ENDPOINT (str): Patchwork notification service API url
    PATCHWORK_CONFIG_PATH (str): Absolute path to store machine metadata

.. _API documentation:
    https://patchworksecurity.com/docs/
"""
from __future__ import absolute_import

import json
import os
import subprocess

import requests

import mcv.os

PATCHWORK_API_ENDPOINT = "https://api.patchworksecurity.com/api/v1"
PATCHWORK_CONFIG_PATH = '/etc/patchwork/config'


def _post(api_key, data, uuid=None):
    """Perform Patchwork API request

    Args:
        api_key (str): Patchwork API key
        data (dict): JSON POST data
        uuid (Optional[str]): UUID to update

    Returns:
        dict: The JSON output from the server

    Raises:
        HTTPError: The server returned a 4XX / 5XX error
    """
    parts = [PATCHWORK_API_ENDPOINT, 'machine']

    if uuid is not None:
        parts.append(uuid)

    url = '/'.join(parts)

    headers = {
        'Accept': 'application/json',
        'Authorization': api_key,
    }

    r = requests.post(url, headers=headers, data=json.dumps(data), verify=True)

    r.raise_for_status()

    return r.json()


def register(api_key, name, config_path=PATCHWORK_CONFIG_PATH):
    """Register this machine

    The config data is stored at config_path. The machine is registered if a
    config file isn't found. The resulting config data is then stored at
    config_path if it is valid.

    Args:
        api_key (str): Patchwork API key
        name (str): Custom name to identify machine by
        config_path (Optional[str]): Absolute path to read / store machine
            metadata from. Default PATCHWORK_CONFIG_PATH

    Returns:
        dict: JSON metadata for this machine
    """
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)

    dirs = os.path.dirname(config_path)
    if not os.path.exists(dirs):
        os.makedirs(dirs)

    os_info = mcv.os.get_os_info()
    os_data = {
        'name': name,
        'os': os_info['os'],
        'version': os_info['version'],
    }

    machine_data = _post(api_key=api_key, data=os_data)

    assert 'uuid' in machine_data, "uuid not found in %r" % machine_data

    with open(config_path, 'w') as f:
        json.dump(machine_data, f)

    return machine_data


def gather_packages():
    """Get the list of packages installed on this machine

    Returns:
        List[tuple]: (Status, Package, Version) corresponding to dpkg-query
        format fields
    """
    dpkg_query_cmd = [
        "/usr/bin/dpkg-query", "-W",
        "-f", "${Status}\t${Package}\t${source:Version}\n",
    ]

    process = subprocess.Popen(dpkg_query_cmd, stdout=subprocess.PIPE)
    output, _ = process.communicate()

    return [tuple(line.split('\t')) for line in output.splitlines() if line]


def update(api_key, packages, uuid=None, config_path=PATCHWORK_CONFIG_PATH):
    """Update this machine's package set

    This replaces the package set stored on the server

    Args:
        api_key (str): Patchwork API key
        packages (List[tuple]): List of 3-tuples representing package state,
            name and version
        uuid (Optional[str]): UUID to update. Defaults to machine UUID
        config_path (Optional[str]): Absolute path to read machine metadata
            from. Defaults to PATCHWORK_CONFIG_PATH

    Returns:
        dict: The JSON output from the server
    """
    if uuid is None:
        with open(config_path, 'r') as f:
            uuid = json.load(f)['uuid']

    data = [
        dict(name=package, version=version)
        for status, package, version in packages
        if status == 'install ok installed'
    ]

    return _post(api_key=api_key, data=data, uuid=uuid)
