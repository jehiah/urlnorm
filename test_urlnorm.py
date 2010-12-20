"""
this is a py.test test file
"""
import urlnorm

def pytest_generate_tests(metafunc):
    if metafunc.function in [test_norms]:
        """ test suite; some taken from RFC1808. Run with py.test"""
        tests = {    
            '/foo/bar/.':                    '/foo/bar/', 
            '/foo/bar/./':                   '/foo/bar/',
            '/foo/bar/..':                   '/foo/',
            '/foo/bar/../':                  '/foo/',
            '/foo/bar/../baz':               '/foo/baz',
            '/foo/bar/../..':                '/',
            '/foo/bar/../../':               '/',
            '/foo/bar/../../baz':            '/baz',
            '/foo/bar/../../../baz':         '/../baz',
            '/foo/bar/../../../../baz':      '/baz',
            '/./foo':                        '/foo',
            '/../foo':                       '/../foo',
            '/foo.':                         '/foo.',
            '/.foo':                         '/.foo',
            '/foo..':                        '/foo..',
            '/..foo':                        '/..foo',
            '/./../foo':                     '/../foo',
            '/./foo/.':                      '/foo/',
            '/foo/./bar':                    '/foo/bar',
            '/foo/../bar':                   '/bar',
            '/foo//':                        '/foo/',
            '/foo///bar//':                  '/foo/bar/',    
            'http://www.foo.com:80/foo':     'http://www.foo.com/foo',
            'http://www.foo.com:8000/foo':   'http://www.foo.com:8000/foo',
            'http://www.foo.com./foo/bar.html': 'http://www.foo.com/foo/bar.html',
            'http://www.foo.com.:81/foo':    'http://www.foo.com:81/foo',
            'http://www.foo.com/%7ebar':     'http://www.foo.com/~bar',
            'http://www.foo.com/%7Ebar':     'http://www.foo.com/~bar',
            'ftp://user:pass@ftp.foo.net/foo/bar': 'ftp://user:pass@ftp.foo.net/foo/bar',
            'http://USER:pass@www.Example.COM/foo/bar': 'http://USER:pass@www.example.com/foo/bar',
            'http://www.example.com./':      'http://www.example.com/',
            'http://test.example/?a=%26&b=1': 'http://test.example/?a=%26&b=1', # should not un-encode the & that is part of a parameter value
            'http://test.example/?a=%e3%82%82%26': 'http://test.example/?a=\xe3\x82\x82%26'.decode('utf8'), # should return a unicode character
            # note: this breaks the internet for parameters that are positional (stupid nextel) and/or don't have an = sign
            # 'http://test.example/?a=1&b=2&a=3': 'http://test.example/?a=1&a=3&b=2', # should be in sorted/grouped order
            'http://s.xn--q-bga.de/':       'http://s.q\xc3\xa9.de/'.decode('utf8'), # should be in idna format
            'http://test.example/?':        'http://test.example/', # no trailing ?
            # 'http://test.example?':       'http://test.example/', # with trailing /
            'http://a/path/?b&a' : 'http://a/path/?b&a',
            # test utf8 and unicode
            u'http://XBLA\u306eXbox.com': 'http://xbla\xe3\x81\xaexbox.com'.decode('utf8'),
            u'http://XBLA\u306eXbox.com'.encode('utf8'): 'http://xbla\xe3\x81\xaexbox.com'.decode('utf8'),
            u'http://XBLA\u306eXbox.com': 'http://xbla\xe3\x81\xaexbox.com'.decode('utf8'),
            # test idna + utf8 domain
            u'http://xn--q-bga.XBLA\u306eXbox.com'.encode('utf8'): 'http://q\xc3\xa9.xbla\xe3\x81\xaexbox.com'.decode('utf8'),
            '-':                             '-',
            'http://ja.wikipedia.org/wiki/%E3%82%AD%E3%83%A3%E3%82%BF%E3%83%94%E3%83%A9%E3%83%BC%E3%82%B8%E3%83%A3%E3%83%91%E3%83%B3': 'http://ja.wikipedia.org/wiki/\xe3\x82\xad\xe3\x83\xa3\xe3\x82\xbf\xe3\x83\x94\xe3\x83\xa9\xe3\x83\xbc\xe3\x82\xb8\xe3\x83\xa3\xe3\x83\x91\xe3\x83\xb3'.decode('utf8'),
            
            # check that %23 (#) is not escaped where it shouldn't be
            'http://test.example/?p=%23val#test-%23-val': 'http://test.example/?p=%23val#test-%23-val',
            # check that %20 is not unescaped to ' '
            'http://test.example/?p=%20val%20' : 'http://test.example/?p=%20val%20',
        }
        for bad, good in tests.items():
            metafunc.addcall(funcargs=dict(bad=bad, good=good))

    elif metafunc.function in [test_invalid_urls]:
        for url in [
            'http://http://www.exemple.com/',
            ]:
            metafunc.addcall(funcargs=dict(url=url))

def test_invalid_urls(url):
    try:
        urlnorm.norm(url)
    except urlnorm.InvalidUrl:
        return
    assert 1 == 0, "this should have raised an InvalidUrl exception"

def test_norms(bad, good):
    new_url = urlnorm.norm(bad)
    print "bad", repr(bad)
    print "new_url", repr(new_url)
    print "good", repr(good)
    print "new_url", new_url
    print "good", good
    assert new_url == good
