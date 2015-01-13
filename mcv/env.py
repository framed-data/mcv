import re
from contextlib import contextmanager
import os

env_file = '/etc/environment'


def parse_environment_file():
    """Return a list of (name, value) tuples representing the env vars in
    /etc/environment."""
    with open(env_file, 'r') as efile:
        raw_lines = efile.readlines()
        lines = [re.sub(r'#.*$', '', line).strip() for line in raw_lines]
        matches = [re.match(r'^(\w+)=(.*)$', line) for line in lines]
        return dict((m.group(1), m.group(2)) for m in matches if m)


def append_env_setting(name, value):
    """Append the given variable to /etc/environment."""
    with open(env_file, 'a') as efile:
        efile.write("%s=%s\n" % (name, value))


def add_environment_var(name, value):
    """Idempotently add a variable to /etc/environment."""
    env = parse_environment_file()
    if name not in env:
        append_env_setting(name, value)


@contextmanager
def context(env_mappings, clear=False):
    e0 = os.environ.copy()
    if clear:
        os.environ.clear()
    os.environ.update(env_mappings)
    yield os.environ
    os.environ.clear()
    os.environ.update(e0)
