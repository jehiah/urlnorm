"""
this is a py.test test file
"""
import urlnorm
from urlnorm import _unicode

def pytest_generate_tests(metafunc):
    if metafunc.function in [test_norms]:
        """ test suite; some taken from RFC1808. Run with py.test"""
        tests = {
            'http://1113982867/':            'http://66.102.7.147/', # ip dword encoding
            'http://www.thedraymin.co.uk:/main/?p=308': 'http://www.thedraymin.co.uk/main/?p=308', # empty port
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
            
            # 'http://s.xn--q-bga.de/':       'http://s.q\xc3\xa9.de/'.decode('utf8'), # should be in idna format
            'http://test.example/?':        'http://test.example/', # no trailing ?
            'http://test.example?':       'http://test.example/', # with trailing /
            'http://a.COM/path/?b&a' : 'http://a.com/path/?b&a',
            # test utf8 and unicode
            u'http://XBLA\u306eXbox.com': 'http://xbla\xe3\x81\xaexbox.com/'.decode('utf8'),
            u'http://XBLA\u306eXbox.com'.encode('utf8'): 'http://xbla\xe3\x81\xaexbox.com/'.decode('utf8'),
            u'http://XBLA\u306eXbox.com': 'http://xbla\xe3\x81\xaexbox.com/'.decode('utf8'),
            # test idna + utf8 domain
            # u'http://xn--q-bga.XBLA\u306eXbox.com'.encode('utf8'): 'http://q\xc3\xa9.xbla\xe3\x81\xaexbox.com'.decode('utf8'),
            'http://ja.wikipedia.org/wiki/%E3%82%AD%E3%83%A3%E3%82%BF%E3%83%94%E3%83%A9%E3%83%BC%E3%82%B8%E3%83%A3%E3%83%91%E3%83%B3': 'http://ja.wikipedia.org/wiki/\xe3\x82\xad\xe3\x83\xa3\xe3\x82\xbf\xe3\x83\x94\xe3\x83\xa9\xe3\x83\xbc\xe3\x82\xb8\xe3\x83\xa3\xe3\x83\x91\xe3\x83\xb3'.decode('utf8'),
            'http://test.example/\xe3\x82\xad': 'http://test.example/\xe3\x82\xad',
            
            # check that %23 (#) is not escaped where it shouldn't be
            'http://test.example/?p=%23val#test-%23-val%25': 'http://test.example/?p=%23val#test-%23-val%25',
            # check that %20 or %25 is not unescaped to ' ' or %
            'http://test.example/%25/?p=%20val%20%25' : 'http://test.example/%25/?p=%20val%20%25',
            "http://test.domain/I%C3%B1t%C3%ABrn%C3%A2ti%C3%B4n%EF%BF%BDliz%C3%A6ti%C3%B8n" : "http://test.domain/I\xc3\xb1t\xc3\xabrn\xc3\xa2ti\xc3\xb4n\xef\xbf\xbdliz\xc3\xa6ti\xc3\xb8n",
            # check that spaces in paths are not escaped
            'http://test.example/abcde%20def' : 'http://test.example/abcde def',
            # check that spaces are collated to '+'
            "http://test.example/path/with a%20space+/" : "http://test.example/path/with a space+/",  # spaces in apths are ok
            "http://[2001:db8:1f70::999:de8:7648:6e8]/test" : "http://[2001:db8:1f70::999:de8:7648:6e8]/test", #ipv6 address
            "http://[::ffff:192.168.1.1]/test" : "http://[::ffff:192.168.1.1]/test", # ipv4 address in ipv6 notation
            "http://[::ffff:192.168.1.1]:80/test" : "http://[::ffff:192.168.1.1]/test", # ipv4 address in ipv6 notation
            "htTps://[::fFff:192.168.1.1]:443/test" : "https://[::ffff:192.168.1.1]/test", # ipv4 address in ipv6 notation

            # python 2.5 urlparse doesn't handle unknown protocols, so skipping this for now
            #"itms://itunes.apple.com/us/app/touch-pets-cats/id379475816?mt=8#23161525,,1293732683083,260430,tw" : "itms://itunes.apple.com/us/app/touch-pets-cats/id379475816?mt=8#23161525,,1293732683083,260430,tw", #can handle itms://

        }
        for bad, good in tests.items():
            metafunc.addcall(funcargs=dict(bad=bad, good=good))
    
    elif metafunc.function == test_unquote:
        for bad, good, unsafe in (
            ('%20', ' ', ''),
            ('%3f', '%3F', '?'), # don't unquote it, but uppercase it
            ('%E3%82%AD', u'\u30ad', ''),
            ):
            metafunc.addcall(funcargs=dict(bad=bad, good=good, unsafe=unsafe))
    
    elif metafunc.function in [test_invalid_urls]:
        for url in [
            'http://http://www.exemple.com/', # invalid domain
            '-',
            'asdf',
            'HTTP://4294967297/test', # one more than max ip > int
            'http://[img]http://i790.photobucket.com/albums/yy185/zack-32009/jordan.jpg[/IMG]',
            ]:
            metafunc.addcall(funcargs=dict(url=url))
    elif metafunc.function == test_norm_path:
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
        }
        for bad, good in tests.items():
            metafunc.addcall(funcargs=dict(bad=bad, good=good))

def test_invalid_urls(url):
    try:
        output = urlnorm.norm(url)
        print '%r' % output
    except urlnorm.InvalidUrl:
        return
    assert 1 == 0, "this should have raised an InvalidUrl exception"

def test_unquote(bad, good, unsafe):
    output = urlnorm.unquote_safe(bad, unsafe)
    assert output == good

def test_norms(bad, good):
    new_url = urlnorm.norm(bad)
    assert new_url == _unicode(good)

def test_norm_path(bad, good):
    output = urlnorm.norm_path("http", bad)
    assert output == _unicode(good)
