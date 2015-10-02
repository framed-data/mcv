import mcv.hostname
from nose.tools import eq_


def test__splice_alias():
    l1 = '255.255.255.255    broadcasthost'
    l2 = '127.0.0.1 localhost'
    l3 = '127.0.0.1 localhost wozzle'
    eq_(mcv.hostname._splice_alias('wozzle', l1), l1)
    eq_(mcv.hostname._splice_alias('wozzle', l2),
        '127.0.0.1 localhost wozzle')
    eq_(mcv.hostname._splice_alias('wozzle', l3), l3)
