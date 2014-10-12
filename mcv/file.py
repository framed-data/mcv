"""OS Manipulation

Wrappers around os, os.path"""

from __future__ import absolute_import

import os
import mcv.user
import grp
import subprocess
import tempfile

opt_keys = ['owner', 'group', 'mode']


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
        'mode': 02775,
        'parents': False,
    })
    """
    if not os.path.exists(path):
        if opts.get('parents'):
            retval = subprocess.call(['mkdir', '-p', path])
        else:
            os.mkdir(path, opts.get('mode', 0777))  # use Python's default mode

    ch_ext(path, opts)


def link(source, link_name, force=False):
    """Creates symlink at `link_name` pointing at `source`.

    If `link_name` is already a symlink, atomically move link
    with `mv -T`

    Idempotent!  Creates or updates link.  If target is non-link,
    will be idempotent with force=True.
    """
    if os.path.lexists(link_name) and os.path.islink(link_name):
        tmppath = tempfile.mkdtemp()
        tmp_link = os.path.join(tmppath, 'link')
        os.symlink(source, tmp_link)
        subprocess.call(['mv', '-T', tmp_link, link_name])
    elif os.path.lexists(link_name) and force is True:
        os.unlink(link_name)
        os.symlink(source, link_name)
    else:
        os.symlink(source, link_name)


def unlink(path):
    """Idempotent unlink"""
    if os.path.exists(path):
        os.unlink(path)
