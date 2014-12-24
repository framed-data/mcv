"""Filesytem module

Credit to Alexander Bulimov <lazywolf0@gmail.com> and Seth Vidal (RIP)
for writing the Ansible modules on which this is based."""

import sys
import os
import subprocess

blkid_path = "/sbin/blkid"
mkfs_path = "/sbin/mkfs"
sgdisk_path = "/sbin/sgdisk"
mount_path = "/bin/mount"
umount_path = "/bin/umount"


def partition(dev):
    """Partition an empty disk drive to have exactly 1 partition
    on it filling the whole space."""

    # TODO: this is a hack for now; figure out if there's a better way
    # to test if a disk has been partitioned.  Two known alternatives:
    #
    # 1. parse `parted -lm` output
    # 2. investigate not-super-publicly-accessible `pyparted` RedHat package

    if os.path.exists(dev + "1"):  # e.g. /dev/sdb -> /dev/sdb1
        return None

    cmd = [sgdisk_path, dev, "-N", str(1)]
    status = subprocess.call(cmd, stdout=sys.stdout, stderr=sys.stderr)
    return status


def mkfs(dev, dst_fstype, opts, force=False, verbose='error'):
    if not os.path.exists(dev):
        raise Exception("Device %s not found." % dev)

    cmd = [blkid_path, "-c", "/dev/null", "-o", "value", "-s", "TYPE", dev]

    with open('/dev/null', 'w') as devnull:
        out = subprocess.call(cmd, stdout=devnull, stderr=devnull)
        if out != 0:
            src_fstype = None
        else:
            out = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE,
                    stderr=sys.stderr).communicate()[0]
            src_fstype = out.strip()

    if src_fstype == dst_fstype:
        return True

    elif src_fstype and not force:
        msg_tmpl = "{dev} is already used as {fs}, use force=True to overwrite"
        msg = msg_tmpl.format(dev=dev, fs=fs)
        sys.stderr.write(msg)
        return False

    else:  # actually make the filesystem
        cmd = [mkfs_path, '-t', dst_fstype] + ([opts] if opts else []) + [dev]
        status = subprocess.call(cmd, stdout=sys.stdout, stderr=sys.stderr)
        if status != 0:
            msg_template = "Creating filesystem %s on device '%s' failed"
            sys.stderr.write(msg_template. format(dst_fstype, dev))
            return False
        return True


def _set_mount(fstab_in, args_in):
    """ set/change a mount point location in fstab """
    default_args = {
        'opts': 'defaults',
        'dump': '0',
        'passno': '0',
    }
    args = dict(default_args.items() + args_in.items())

    columns = ['src', 'name', 'fstype', 'opts', 'dump', 'passno']

    lines = [l.split() for l in fstab_in.strip().split("\n")]

    existing_line = None
    # src, name, fstype, opts, dump, passno
    for idx, l in enumerate(lines):
        if len(l) > 2 and l[1] == args['name']:
            existing_line = idx

    if existing_line:
        lines[existing_line] = [args[k] for k in columns]
    else:
        lines.append([args[k] for k in columns])

    return "".join([' '.join(l) + "\n" for l in lines])


def set_mount(args_in):
    """Sets up a mount in /etc/fstab

    Takes a dict of arguments:

       {'src': '/dev/sda1', # the device
        'name': '/tmp',     # where to mount the device
        'fstype': 'ext3',   # filesystem type
        'opts': 'defaults', # OPTIONAL mount opts, as a string
        'dump': '0',        # OPTIONAL dump, as a string
        'passno': '0',      # OPTIONAL passno, as a string
       }
    """
    with open("/etc/fstab", 'r') as f:
        input = f.read()
        output = _set_mount(input, args_in)

    with open("/etc/fstab", 'w') as f:
        f.write(output)


def mount(name, remount=False):
    """ mount up a path or remount if needed """
    cmd = None
    if os.path.ismount(name):
        if remount:
            cmd = [mount_path, '-o', 'remount', name]
    else:
        cmd = [mount_path, name]

    if cmd:
        return subprocess.call(cmd, stdout=sys.stdout, stderr=sys.stderr)
    else:
        return None


def _parse_mount_opts(s):
    opt_strings = s.split(',')
    opt_kv_pairs = [o.split('=') if '=' in o
                    else [o, True]
                    for o in opt_strings]
    return dict(opt_kv_pairs)


def _parse_mount_row(row_string):
    """Parse a row of /proc/mounts output into a nested dict
    {'dev': ...,
     'mount': ...,
     'opts': ...,}
    """
    dev, mnt, fs, opts_str, _, _ = row_string.split()
    return {
        'dev': dev,
        'mnt': mnt,
        'fs': fs,
        'opts': _parse_mount_opts(opts_str)}


def _parse_proc_mounts(mounts_output):
    """Return a list of mount data rows, given /proc/mounts output

    See `mount_status` for struture details.
    """
    return [_parse_mount_row(r) for r in mounts_output.split('\n')]


def mount_status(path='/proc/mounts'):
    """Return a list of mount data rows, reading /proc/mounts to get data.

    Each row is a list of columns
    [device, mount_point, fstype_, opts]

    Where opts is a list of mount optons, supporting either a string options,
    or a 2-tuple (key, value) pair.
    [opt0, opt1, [opt2key, opt2value], opt3]
    """
    with open(path, 'r') as f:
        mounts_output = f.read().strip()

    return _parse_proc_mounts(mounts_output)


def _mounted(mounts, mount):
    return any([m['mnt'] == mount for m in mounts])


def mounted(mount):
    return _mounted(mount_status(), mount)


def umount(name):
    """ unmount a path """
    return subprocess.call([umount_path, name],
                           stdout=sys.stdout,
                           stderr=sys.stderr)
