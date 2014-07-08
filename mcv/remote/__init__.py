import subprocess
import sys
import paramiko
import getpass
import os
import tempfile
import StringIO
import pipes

from contextlib import contextmanager

def conn_spec():
    """Return a connection specification with sane default values."""
    return {'username': getpass.getuser(),
            'missing_host_key_policy': paramiko.AutoAddPolicy(),
            'host_keys_path': os.path.join("~", ".ssh", "known_hosts")}

@contextmanager
def connection(connspec, verbose=False):
    ssh = paramiko.SSHClient()

    missing_host_key_policy = connspec.pop('missing_host_key_policy', None)
    if missing_host_key_policy:
        ssh.set_missing_host_key_policy(missing_host_key_policy)

    host_keys_path = os.path.expanduser(connspec.pop('host_keys_path', ''))
    if host_keys_path and os.path.exists(host_keys_path):
        ssh.load_host_keys(host_keys_path)

    host = connspec.pop('host', None)

    sys.stderr.write("Connecting...")
    ssh.connect(host, **connspec)
    sys.stderr.write("OK.\n")
    yield ssh
    ssh.close()

@contextmanager
def sftp_connection(ssh_connection):
    sftp = ssh_connection.open_sftp()
    yield sftp
    sftp.close()

def execute(ssh, cmd, sudo=False):
    # cmd might not be a string; might be a list i.e.
    # `subprocess`-style.  Handle it nicely.
    cmd_string = cmd if isinstance(cmd, basestring) else ' '.join(cmd)

    final_cmd = '/usr/bin/sudo /bin/sh -c {}'.format(
            pipes.quote(cmd_string)) if sudo else cmd_string

    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(final_cmd)
    out = ssh_stdout.read()
    err = ssh_stderr.read()
    return (out, err)

def _copy(ssh, local_src, remote_dst, sudo=False):
    """Copies individual files"""
    if sudo:
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('mktemp')
        remote_temppath = ssh_stdout.read().strip()
        with sftp_connection(ssh) as sftp:
            sftp.put(local_src, remote_temppath)
        cmd = '/usr/bin/sudo mv {} {}'.format(remote_temppath, remote_dst)
        print cmd
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
    else:
        with sftp_connection(ssh) as sftp:
            sftp.put(local_src, remote_dst)

def copy(ssh, local_src, remote_dst, sudo=False):
    """Copies individual files"""
    _copy(ssh, local_src, remote_dst, sudo)

def deploy(ssh, local_src, remote_dst, sudo=False, verbose=False):
    temp = tempfile.NamedTemporaryFile()
    cmd = ['/bin/tar', '-cvf', temp.name, local_src]
    print "Tarring to " + temp.name
    out = subprocess.check_output(cmd)

    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('mktemp')
    remote_temppath = ssh_stdout.read().strip()
    print "Copying tarball to " + remote_temppath
    _copy(ssh, temp.name, remote_temppath, sudo=False)

    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(
        '{}mkdir -p {}'.format(
            'sudo ' if sudo else '',
            remote_dst))

    if verbose:
        sys.stdout.write(ssh_stdout.read())
        sys.stderr.write(ssh_stderr.read())

    tar_cmd = '{}tar -xvf {} -C {}'.format(
                  'sudo ' if sudo else '',
                  remote_temppath,
                  remote_dst)
    print tar_cmd
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(tar_cmd)

    if verbose:
        sys.stdout.write(ssh_stdout.read())
        sys.stderr.write(ssh_stderr.read())
