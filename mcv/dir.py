"""Directory operations

A thin wrapper on top of treant

For the sake of clarity, we'll keep the term `path` reserved for
directory paths, and we'll call treant tree paths `tpath`s.

This module should mostly expose things in terms of `path`s, not
`tpaths`, though it should be possible to drop down to the lower
level  if necessary.
"""

import treant
import os
import mcv.file
import mcv.util


def tree(node):
    """Construct a tree from nodes; use the treant 'smart' node
    constructor with flexible tuple interpretation:

    (value)
    (value, <[list-is-children]>)
    (value, <{dict-is-attributes}>)
    (value, <[list-is-children]>, <{dict-is-attributes}>)
    (value, <{dict-is-attributes}>, <[list-is-children]>)
    """
    return treant.tree(node, node_constructor=treant.n)


def _path(tree_path):
    """Given a tree path returns its directory path.

    - Treepath = [<root_node>, <home_node>, <john_node>]
    - Directory path => "/home/john"
    """
    # convert nodes e.g. [<root_node>, <home_node>, <john_node>]
    # to their values, e.g. ["/", "home", "john"]
    tpath_values = [treant.value(node) for node in tree_path]
    return os.path.join(*tpath_values)


def _opts(tree_path):
    """Given a tree path return its computed opts.  Opts
    merge hierarchically, combining and overriding
    down the hierarchy.

    - Treepath = [<home_node, opts={'group': 'mycompany', 'mode': 02755}>,
                  <john_node, opts={'owner': 'john'}>,
                  <public_node, opts={'mode': 02775}>]
    - opts => {'owner': 'john',
               'group': 'mycompany',
               'mode': 02775}
   """
    tpath_opts = [treant.attrs(node) for node in tree_path]
    return mcv.util.merge_dicts(*tpath_opts)


def root_path(tree):
    """Returns the root path of a tree, assumed to just be its value."""
    return treant.value(tree)


def subpath(tree, search_name, *subpaths):
    """Find a node in the tree and return a subpath thereof.

    Given a tree corresponding to:

    - /foos
      - bar
      - baz
        - quux

        tree = <setup the above>

        subpath(tree, 'quux', 'fizz', buzz')
        # => "/foo/baz/quux/fizz/buzz"

        subpath(tree, 'nonsense!', 'fizz', buzz')
        # => None #; if the search fails, don't subpath.
    """
    # get the path values themselves out of the tpath, not the full nodes
    root_tpath = treant.find_path_ex(tree,
                                     lambda n: treant.value(n) == search_name)

    if not root_tpath:
        return None

    return os.path.join(*[_path(root_tpath)] + [p for p in subpaths])


def paths(tree):
    # list of tpaths, i.e. list of (list of nodes)
    tps = [tp for tp in treant.paths_preorder(tree)]
    return [_path(tp) for tp in tps]


def _mktree(tree):
    """Given a tree, return a list of (path, opts) tuples
    with opts applied hiearchically, i.e. opts specified at a node
    also get applied to subnodes (unless later overridden)"""
    tps = [tp for tp in treant.paths_preorder(tree)]

    # construct two parallel lists: paths, and opts of each path
    paths = [_path(tp) for tp in tps]
    opts = [_opts(tp) for tp in tps]

    return zip(paths, opts)


def mktree(tree, pred=lambda opts: True):
    """Given a tree, make all the directories in the tree
    recursively, with opts applied hiearchically, i.e. opts specified
    at a node also get applied to subnodes (unless later
    overridden)

    Optionally accepts a `pred`icate function that takes
    an options dict for each node, and returns boolean
    whether that node should be created.
    """
    for path, opts in _mktree(tree):
        if pred(opts):
            mcv.file.mkdir(path, opts=opts)
