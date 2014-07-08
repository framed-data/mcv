import subprocess
import sys
import paramiko
import getpass
import os
import tempfile
import StringIO

from contextlib import contextmanager

@contextmanager
def connection(connspec, verbose=False):
    host = connspec['host']
    username = connspec.get('username', getpass.getuser())
    password = connspec.get('password')

    ssh = paramiko.SSHClient()

    missing_host_key_policy = connspec.get('missing_host_key_policy',
            paramiko.AutoAddPolicy())
    if missing_host_key_policy:
        ssh.set_missing_host_key_policy(missing_host_key_policy)

    host_keys_path = connspec.get('host_keys_path',
                         os.path.join("~", ".ssh", "known_hosts"))
    host_keys_path_expanded = os.path.expanduser(host_keys_path)
    if os.path.exists(host_keys_path_expanded):
        ssh.load_host_keys(host_keys_path_expanded)

    sys.stderr.write("Connecting...")
    ssh.connect(connspec['host'], username=username, password=password)
    sys.stderr.write("OK.\n")
    yield ssh
    ssh.close()

@contextmanager
def sftp_connection(ssh_connection):
    sftp = ssh_connection.open_sftp()
    yield sftp
    sftp.close()

def execute(connspec, cmd, stdout=sys.stdout, stderr=sys.stderr):
    with connection(connspec) as ssh:
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
        stdout.write(ssh_stdout.read())
        stderr.write(ssh_stderr.read())

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

def copy(connspec, local_src, remote_dst, sudo=False):
    """Copies individual files"""
    with connection(connspec) as ssh:
        _copy(ssh, local_src, remote_dst, sudo)

def deploy(connspec, local_src, remote_dst, sudo=False, verbose=False):
    temp = tempfile.NamedTemporaryFile()
    cmd = ['/bin/tar', '-cvf', temp.name, local_src]
    print "Tarring to " + temp.name
    out = subprocess.check_output(cmd)

    with connection(connspec, verbose=verbose) as ssh:
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
