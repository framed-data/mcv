import subprocess
import re


def command(command_name):
    return '/sbin/{}'.format(command_name)


def status(service_name):
    """Query Upstart status"""
    output = subprocess.Popen([command('status'), service_name],
                              stdout=subprocess.PIPE)\
                       .communicate()[0]
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
        return subprocess.call([command(action), service_name])
    else:
        return None


def stop(service_name):
    _, service_status, _ = status(service_name)
    if service_status == 'start/running':
        subprocess.call([command('stop'), service_name])
