"""Configuration loading

The primary interface is that a config loader is callable with a
hostname, and returns a dict of information that should be serialized
to a target host and used to bootstrap configuration thereof.

E.g. if a host `webserver.my.com` should know that it has

{'role': 'web'}

Then configloader('webserver.my.com') should return that dict
above.
"""

import yaml


class ConfigLoader:
    def __init__(self, path):
        self.filepath = path
        with open(self.filepath, 'r') as f:
            self.data = yaml.load(f.read())

    def get(self, hostname):
        return self.data.get(hostname)

    def __call__(self, hostname):
        return self.get(hostname)
