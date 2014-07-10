"""OS Manipulation

Wrappers around os, os.path"""

from __future__ import absolute_import

import os
import mcv.user
import grp

def chmod(path, mode):
    if not mode:
        return

    os.chmod(path, mode)

def chown(path, owner=None, group=None):
    if owner:
        uid = mcv.user.ent_passwd(owner)['uid'] \
            if isinstance(owner, basestring) \
            else owner
        os.chown(path, uid, -1)

    if group:
        gid = grp.getgrnam(group).gr_gid \
            if isinstance(group, basestring) \
            else group
        os.chown(path, -1, gid)

def mkdir(path, opts={}):
    """Idempotent mkdir
    
    opts={
        'owner': 'johndoe',
        'group': 'framed',
        'mode': '02775'
    })
    """
    if not os.path.exists(path):
        os.mkdir(path, mode)

    chmod(path, opts.get('mode'))
    chown(path, opts.get('owner'), opts.get('group'))
