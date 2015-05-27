import subprocess
import sys
import paramiko
import getpass
import os
import tempfile
import StringIO
import pipes
import itertools
import select

from contextlib import contextmanager

import mcv.util


def conn_spec(overrides={}):
    """Return a connection specification with sane default values."""
    return mcv.util.merge_dicts(
        {'username': getpass.getuser(),
         'port': 22,
         'missing_host_key_policy': paramiko.WarningPolicy(),
         'host_keys_path': os.path.join("~", ".ssh", "known_hosts")},
        overrides)


@contextmanager
def connection(connspec, verbose=False):
    """Takes a connection specification with standard Paramiko values, i.e.:

    - host
    - port
    - username (default: getpass.getuser())
    - key_filename (path to private key)

    As well as 'extended' configuration for Paramiko:
    - missing_host_key_policy
    - host_keys_path
    """
    ssh = paramiko.SSHClient()

    missing_host_key_policy = connspec.pop('missing_host_key_policy', None)
    if missing_host_key_policy:
        ssh.set_missing_host_key_policy(missing_host_key_policy)

    host_keys_path = os.path.expanduser(connspec.pop('host_keys_path', ''))
    if host_keys_path and os.path.exists(host_keys_path):
        ssh.load_host_keys(host_keys_path)

    host = connspec.pop('host', None)

    if verbose:
        sys.stderr.write(
            "Connecting to {user}@{host}:{port}...".format(
                user=connspec['username'],
                host=host,
                port=connspec['port']))

    ssh.connect(host, **connspec)

    if verbose:
        sys.stderr.write("OK.\n")

    yield ssh
    ssh.close()


@contextmanager
def sftp_connection(ssh_connection):
    sftp = ssh_connection.open_sftp()
    yield sftp
    sftp.close()


def execute(ssh, cmd, sudo=False, stdout=sys.stdout, stderr=sys.stderr):
    """Executes a command on remote machine over SSH

    Takes:
    - Paramiko ssh connection
    - command in either string "/bin/ls" or list ["/bin/ls", "/etc"]
      form

    Returns:
    - stdout string
    - stderr string
    - exit status of remote command
    """
    # cmd might not be a string; might be a list i.e.
    # `subprocess`-style.  Handle it nicely.
    cmd_string = cmd if isinstance(cmd, basestring) else ' '.join(cmd)

    final_cmd = '/usr/bin/sudo /bin/sh -c {0}'.format(
        pipes.quote(cmd_string)) if sudo else cmd_string

    bufsize = -1
    chan = ssh._transport.open_session()
    chan.get_pty()
    chan.settimeout(timeout=None)
    chan.exec_command(final_cmd)

    out_streams = {'out': stdout,
                   'err': stderr}

    out_strings = {'out': StringIO.StringIO(),
                   'err': StringIO.StringIO()}
    while True:
        if chan.exit_status_ready():
            break
        rl, wl, xl = select.select([chan], [], [], 0.0)

        if len(rl) > 0:
            if chan.recv_ready():
                output = chan.recv(1024)
                out_streams['out'].write(output)
                out_strings['out'].write(output)
            if chan.recv_stderr_ready():
                output = chan.recv_stderr(1024)
                out_streams['err'].write(output)
                out_strings['err'].write(output)

    exit = chan.recv_exit_status()

    return (out_strings['out'].read(), out_strings['err'].read(), exit)


def _copy(ssh, local_src, remote_dst, sudo=False):
    """Copies individual files"""
    if sudo:
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('mktemp')
        remote_temppath = ssh_stdout.read().strip()
        with sftp_connection(ssh) as sftp:
            sftp.put(local_src, remote_temppath)
        cmd = '/usr/bin/sudo mv {0} {1}'.format(remote_temppath, remote_dst)
        print cmd
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
    else:
        with sftp_connection(ssh) as sftp:
            sftp.put(local_src, remote_dst)


def copy(ssh, local_src, remote_dst, sudo=False):
    """Copies individual files"""
    _copy(ssh, local_src, remote_dst, sudo)


def deploy(ssh, local_src, remote_dst, sudo=False, excludes=['.git']):
    """Copies whole directories to remote machine"""
    temp = tempfile.NamedTemporaryFile()
    exclude_pairs = [['--exclude', e] for e in excludes]

    cmd = ['/bin/tar', '-cf', temp.name] + \
          [e for e in itertools.chain(*exclude_pairs)] + \
          [local_src]

    sys.stderr.write("Tarring with: " + str(cmd) + "\n")

    out = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]

    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('mktemp')
    remote_temppath = ssh_stdout.read().strip()

    sys.stderr.write("Copying tarball to {0}\n".format(remote_temppath))

    _copy(ssh, temp.name, remote_temppath, sudo=False)

    sys.stderr.write("Making target directory\n")
    mkdir_cmd = 'mkdir -p {0}'.format(remote_dst)

    out, err, exit = execute(ssh, mkdir_cmd, sudo=sudo)

    tar_cmd = 'tar -xf {0} -C {1}'.format(remote_temppath, remote_dst)

    sys.stderr.write("Extracting tar to target directory\n")

    out, err, exit = execute(ssh, tar_cmd, sudo=sudo)
