import subprocess
import sys
import itertools
import os


def ent_passwd(username):
    command = ["/usr/bin/getent", "passwd", username]
    out = subprocess.Popen(command, stdout=subprocess.PIPE).communicate()[0].\
            strip()
    if bool(out):
        field_keys = ['user', 'pass', 'uid', 'gid', 'comment', 'home', 'shell']
        field_types = [str, str, int, int, str, str, str]
        field_values = out.split(':')
        return dict((k, t(v))
                    for k, t, v
                    in zip(field_keys, field_types, field_values))
    else:
        return None


def exists(username, verbose='error'):
    out = open('/dev/null', 'w') if verbose is not True else sys.stdout
    status = subprocess.call(["/usr/bin/getent", "passwd", username],
                             stdout=out)
    return status == 0


def _add(username):
    cmd = ["useradd", username]
    print cmd
    retval = subprocess.call(cmd, stdout=sys.stdout)
    return retval


def join_arg(string_or_list):
    if not isinstance(string_or_list, basestring):
        return ",".join(string_or_list)
    return string_or_list


def mod(username, opt_dict):
    """Standard options for usermod

    Variable names get prefixed by --, and iterables
    get chained, so:

        {'groups': ['framed', 'sudo']}

    Gets converted to:

        '--groups framed,sudo '

    As you'd expect.
    """
    if len(opt_dict) == 0:
        return

    cmd_args = dict(("--" + k, join_arg(v)) for k, v in opt_dict.iteritems())
    opts = list(itertools.chain(*cmd_args.iteritems()))
    cmd = ["usermod"] + opts + [username]
    retval = subprocess.call(cmd, stdout=sys.stdout)
    return retval


def homedir(username):
    passwd_entry = ent_passwd(username)
    return passwd_entry['home'] if passwd_entry else None


def ssh_keys(username, keys_str):
    home_dir = homedir(username)
    passwd_entry = ent_passwd(username)

    ssh_dir = os.path.join(home_dir, '.ssh')

    if not os.path.exists(ssh_dir):
        if not os.path.exists(home_dir):
            os.mkdir(home_dir, 0755)
            os.chown(home_dir, passwd_entry['uid'], passwd_entry['gid'])
        os.mkdir(ssh_dir, 0700)
        os.chown(ssh_dir, passwd_entry['uid'], passwd_entry['gid'])

    keyfile = os.path.join(ssh_dir, 'authorized_keys')
    with open(keyfile, 'w') as f:
        f.write(keys_str)

    os.chmod(keyfile, 0600)
    os.chown(keyfile, passwd_entry['uid'], passwd_entry['gid'])


def ext(username, opt_dict):
    """Extended options for MCV, e.g. `authorized_keys`"""
    handlers = {'authorized_keys': ssh_keys}

    for opt_name, opt_args in opt_dict.iteritems():
        if opt_name in handlers:
            handler = handlers[opt_name]
            handler(username, opt_args)


def add(username, mod_opts={}, ext_opts={}):
    if not exists(username):
        _add(username)
    mod(username, mod_opts)
    ext(username, ext_opts)


def userdel(username, kill=True):
    if exists(username):
        if kill:
            subprocess.call(['pkill', '-9', '-U', username])
        subprocess.call(['deluser', '--remove-home', username])


def groupadd(groupname):
    cmd = ['/usr/sbin/groupadd', '-f', groupname]
    retval = subprocess.call(cmd, stdout=sys.stdout)
