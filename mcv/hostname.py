import os

HOSTNAME_FILE = '/etc/hostname'
HOSTS_FILE = '/etc/hosts'


def _splice_alias(alias, line):
    """If line is an alias for localhost, append <alias>
    (if not already present)"""
    vs = line.split(' ')
    if vs[0] == '127.0.0.1' and alias not in vs[1:]:
        vs.append(alias)
        return ' '.join(vs)
    else:
        return line


def set_hostname(hostname):
    """Set the system hostname to <hostname> and add a
    corresponding entry to /etc/hosts"""
    os.system('hostname ' + hostname)
    with open(HOSTNAME_FILE, 'w') as f:
        f.write(hostname)
    with open(HOSTS_FILE, 'r') as f:
        stripped_lines = [l.rstrip() for l in f.readlines()]
        spliced_lines = [_splice_alias(hostname, l) for l in stripped_lines]
        new_contents = "\n".join(spliced_lines)
    with open(HOSTS_FILE, 'w') as f:
        f.write(new_contents)
