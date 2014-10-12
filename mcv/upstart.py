import subprocess
import re


def status(service_name):
    """Query Upstart status"""
    output = subprocess.check_output(['status', service_name])
    re_tmpl = '(?P<service>\S+) (?P<status>[\w/]+)(, process (?P<proc>\d+))?'
    r = re.compile(re_tmpl)
    m = r.match(output)
    service, status, _, pid = m.groups()
    return [service, status, pid]


def start(service_name, restart=False):
    """Idempotent Upstart start"""
    _, service_status, _ = status(service_name)

    action = None
    if service_status == 'start/running' and restart:
        action = 'restart'
    else:
        action = 'start'

    if action:
        return subprocess.call([action, service_name])
    else:
        return None
