"""Filesytem module

Credit to Alexander Bulimov <lazywolf0@gmail.com>
for writing the Ansible module on which this is based."""

import sys
import os
import subprocess

# def mkfs(dev, fstype, opts, force):
#     if not os.path.exists(dev):
#         raise Exception("Device %s not found." % dev)
# 
#     blkid_path = "/sbin/blkid"
#     cmd = [blkid_path, "-c", "/dev/null", "-o", "value", "-s", "TYPE", dev]
#     subprocess.check_output(cmd, stdout=sys.stdout)
# 
#     rc, raw_fs, err = 
#     fs = raw_fs.strip()
# 
#     if fs == fstype:
#         # No change
#         return
# 
#     elif fs and not force:
#         msg_tmpl = "{dev} is already used as {fs}, use force=True to overwrite"
#         msg = msg_tmpl.format(dev=dev, fs=fs)
#         raise Exception(msg)
# 
#     else: # actually make the filesystem
#         mkfs_path = "/sbin/mkfs"
#         cmd = None
#         if opts is None:
#             cmd = "%s -t %s '%s'" % (mkfs, fstype, dev)
#         else:
#             cmd = "%s -t %s %s '%s'" % (mkfs, fstype, opts, dev)
#         rc,_,err = module.run_command(cmd)
#         if rc == 0:
#             changed = True
#         else:
#             module.fail_json(msg="Creating filesystem %s on device '%s' failed"%(fstype,dev), rc=rc, err=err)
# 
#     return True
