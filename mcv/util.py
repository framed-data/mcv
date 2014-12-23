"""General utilities for mcv"""

import itertools


def select_keys(d, keys):
    return dict((k, d.get(k)) for k in keys if d.get(k))


def merge_dicts(*ds):
    """Takes multiple dicts and shallowly merges their KV
    pairs.  KVs in later dicts replace the same K in earlier
    dicts."""
    d_lists = map(lambda d: d.items(), ds)
    return dict([i for i in itertools.chain(*d_lists)])
