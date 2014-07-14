import mcv.remote

from nose.tools import eq_

def test_conn_spec_default_username():
    assert mcv.remote.conn_spec()['username']

def test_conn_spec_default_port():
    assert mcv.remote.conn_spec()['port']

def test_conn_spec_default_missing_host_key_policy():
    assert mcv.remote.conn_spec()['missing_host_key_policy']

def test_conn_spec_default_host_keys_path():
    assert mcv.remote.conn_spec()['host_keys_path']

def test_conn_spec_overrides_no_collision():
    defaults = mcv.remote.conn_spec()
    with_override = mcv.remote.conn_spec({'foobar': 'baz'})
    assert len(with_override) == len(defaults) + 1

def test_conn_spec_overrides_collision():
    defaults = mcv.remote.conn_spec()
    with_override = mcv.remote.conn_spec({'port': 2222})
    assert len(with_override) == len(defaults)
