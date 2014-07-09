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
            'port': 22,
            'missing_host_key_policy': paramiko.AutoAddPolicy(),
            'host_keys_path': os.path.join("~", ".ssh", "known_hosts")}

@contextmanager
def connection(connspec, verbose=False):
    """Takes a connection specification with standard Paramiko values, i.e.:

    - host
    - port
    - username (default: getpass.getuser())

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

def _exec_command(ssh, command, bufsize=-1, timeout=None, get_pty=False):
    """Version of paramiko.SSHClient.exec_command that also returns
    exit status"""
    chan = ssh._transport.open_session()
    if get_pty:
        chan.get_pty()
    chan.settimeout(timeout)
    chan.exec_command(command)
    stdin = chan.makefile('wb', bufsize)
    stdout = chan.makefile('r', bufsize)
    stderr = chan.makefile_stderr('r', bufsize)
    exit = chan.recv_exit_status()
    return stdin, stdout, stderr, exit

def execute(ssh, cmd, sudo=False, verbose='error'):
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

    final_cmd = '/usr/bin/sudo /bin/sh -c {}'.format(
            pipes.quote(cmd_string)) if sudo else cmd_string

    ssh_stdin, ssh_stdout, ssh_stderr, exit = _exec_command(ssh, final_cmd)
    out = ssh_stdout.read()
    err = ssh_stderr.read()

    if verbose == True or (verbose == 'error' and exit != 0):
        sys.stdout.write(out)
        sys.stderr.write(err)
        sys.stderr.write("Exited with status: {}\n".format(exit))

    return (out, err, exit)

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

def deploy(ssh, local_src, remote_dst, sudo=False, verbose='error'):
    """Copies whole directories to remote machine"""
    temp = tempfile.NamedTemporaryFile()
    cmd = ['/bin/tar', '-cvf', temp.name, local_src]

    if verbose == True:
        sys.stderr.write("Tarring to {}\n".format(temp.name))

    out = subprocess.check_output(cmd)

    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('mktemp')
    remote_temppath = ssh_stdout.read().strip()

    if verbose == True:
        sys.stderr.write("Copying tarball to {}\n".format(remote_temppath))

    _copy(ssh, temp.name, remote_temppath, sudo=False)

    mkdir_cmd = 'mkdir -p {}'.format(remote_dst)

    out, err, exit = execute(ssh, mkdir_cmd, sudo=sudo, verbose=verbose)

    tar_cmd = 'tar -xvf {} -C {}'.format(remote_temppath, remote_dst)
    out, err, exit = execute(ssh, tar_cmd, sudo=sudo, verbose=verbose)
