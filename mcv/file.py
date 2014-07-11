"""OS Manipulation

Wrappers around os, os.path"""

from __future__ import absolute_import

import os
import mcv.user
import grp
import subprocess

def chmod(path, mode, recursive=False):
    if not mode:
        return

    if not recursive:
        return os.chmod(path, mode)
    else:
        return subprocess.call(['chmod', '-R', "{0:o}".format(mode), path])

def chown(path, owner=None, group=None, recursive=False):
    if owner:
        uid = mcv.user.ent_passwd(owner)['uid'] \
            if isinstance(owner, basestring) \
            else owner

        if not recursive:
            os.chown(path, uid, -1)
        else:
            subprocess.call(['chown', '-R', str(uid), path])

    if group:
        gid = grp.getgrnam(group).gr_gid \
            if isinstance(group, basestring) \
            else group

        if not recursive:
            os.chown(path, -1, gid)
        else:
            subprocess.call(['chgrp', '-R', str(gid), path])

def ch_ext(path, opts={}):
    """Change extended file attributes:

    - mode
    - owner
    - group"""
    recursive = opts.get('recursive', False)
    chmod(path, opts.get('mode'), recursive=recursive)
    chown(path, opts.get('owner'), opts.get('group'), recursive=recursive)

def mkdir(path, opts={}):
    """Idempotent mkdir
    
    opts={
        'owner': 'johndoe',
        'group': 'framed',
        'mode': '02775'
    })
    """
    if not os.path.exists(path):
        os.mkdir(path, opts.get('mode', 0777)) # same default mode as Python

    ch_ext(path, opts)
