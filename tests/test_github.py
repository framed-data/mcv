import mcv.github
from nose.tools import eq_


def test__archive_url_no_auth():
    eq_(mcv.github._archive_url('myuser', 'myrepo', 'master'),
        "https://github.com/myuser/myrepo/archive/master.tar.gz")


def test__archive_url_auth():
    eq_(mcv.github._archive_url('myuser',
                                'myrepo',
                                'master',
                                auth=('me', '12345')),
        "https://me:12345@github.com/myuser/myrepo/archive/master.tar.gz")
