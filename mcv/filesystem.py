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

    if os.path.exists(dev + "1"): #e.g. /dev/sdb -> /dev/sdb1
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
            out = subprocess.check_output(cmd, stderr=sys.stderr)
            src_fstype = out.strip()

    if src_fstype == dst_fstype:
        return True

    elif src_fstype and not force:
        msg_tmpl = "{dev} is already used as {fs}, use force=True to overwrite"
        msg = msg_tmpl.format(dev=dev, fs=fs)
        sys.stderr.write(msg)
        return False

    else: # actually make the filesystem
        cmd = [mkfs_path, '-t', dst_fstype] + ([opts] if opts else []) + [dev]
        status = subprocess.call(cmd, stdout=sys.stdout, stderr=sys.stderr)
        if status != 0:
            sys.stderr.write("Creating filesystem %s on device '%s' failed" % (fstype,dev))
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

def mount(name):
    """ mount up a path or remount if needed """
    if os.path.ismount(name):
        cmd = [ mount_path, '-o', 'remount', name ]
    else:
        cmd = [ mount_path, name ]

    return subprocess.call(cmd, stdout=sys.stdout, stderr=sys.stderr)

def umount(name):
    """ unmount a path """
    return subprocess.call([umount_path, name], stdout=sys.stdout, stderr=sys.stderr)
