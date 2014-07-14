"""Tests for mcv.dir module"""

import mcv.dir
from nose.tools import eq_

tree0 = mcv.dir.tree(
    ('/', [
         ('opt', [
             ('framed', [
                 ('bin')]),
             ('mcv', [
                 ('bin'),
                 ('tests')])])]))

framed_attrs = {
    'group': 'framed',
    'mode': 02775,
}

tree1 = mcv.dir.tree(
    ('/', [
         ('opt', [
             ('framed', framed_attrs, [
                 ('bin'),
                 ('public', { 'mode': 0777 })]),
             ('mcv', framed_attrs, [
                 ('bin') ])])]))

def test_subpath_hit():
    eq_(mcv.dir.subpath(tree0, 'framed', 'src'),
        "/opt/framed/src")

def test_subpath_miss():
    eq_(mcv.dir.subpath(tree0, 'nonsense!', 'src'), None)

def test_paths():
    eq_(mcv.dir.paths(tree0),
        ['/',
         '/opt',
         '/opt/framed',
         '/opt/framed/bin',
         '/opt/mcv',
         '/opt/mcv/bin',
         '/opt/mcv/tests'])

def test__mktree():
    eq_(mcv.dir._mktree(tree1),
        [("/", {}),
         ("/opt", {}),
         ("/opt/framed", framed_attrs),
         ("/opt/framed/bin", framed_attrs),
         ("/opt/framed/public", { 'group': 'framed', 'mode': 0777 }),
         ("/opt/mcv", framed_attrs),
         ("/opt/mcv/bin", framed_attrs)])

