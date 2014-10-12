import mcv.util
from nose.tools import eq_


def test_select_keys_hit():
    d = {'foo': 20, 'bar': 40}

    eq_(mcv.util.select_keys(d, ['foo']),
        {'foo': 20})


def test_select_keys_miss():
    d = {'foo': 20, 'bar': 40}

    eq_(mcv.util.select_keys(d, ['foo', 'baz']),
        {'foo': 20})


def test_merge_dicts():
    d0 = {'foo': 20, 'bar': 40}
    d1 = {'baz': 60}
    d2 = {'foo': 30}

    eq_(mcv.util.merge_dicts(d0, d1, d2),
        {'foo': 30,
         'bar': 40,
         'baz': 60})
