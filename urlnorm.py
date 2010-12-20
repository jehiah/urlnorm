#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
urlnorm.py - URL normalisation routines

urlnorm normalizes a URL by:
  * lowercasing the scheme and hostname
  * converting the hostname to IDN format
  * taking out default port if present (e.g., http://www.foo.com:80/)
  * collapsing the path (./, ../, etc)
  * removing the last character in the hostname if it is '.'
  * unquoting any % escaped characters (where possible)

Available functions:
  norm - given a URL (string), returns a normalised URL

  norm_netloc
  norm_path
  unquote_path
  unquote_qs
  unquote_fragment
  
 
CHANGES:
1.0.1 fix problem unescaping %23 and %20 in query string
1.0 - new release
0.94 - idna handling, unescaping querystring, fragment, add ws + wss ports
0.92 - unknown schemes now pass the port through silently
0.91 - general cleanup
     - changed dictionaries to lists where appropriate
     - more fine-grained authority parsing and normalisation    
"""

__license__ = """
Copyright (c) 1999-2002 Mark Nottingham <mnot@pobox.com>
Copyright (c) 2010 Jehiah Czebotar <jehiah@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# also update in setup.py
__version__ = "1.0.1"

from urlparse import urlparse, urlunparse
from string import lower
import re

class InvalidUrl(Exception):
    pass

_collapse = re.compile('([^/]+/\.\./?|/\./|//|/\.$|/\.\.$)')
_server_authority = re.compile('^(?:([^\@]+)\@)?([^\:]+)(?:\:(.+))?$')
_default_port = {   'http': '80',
                    'itms': '80',
                    'ws': '80',
                    'https': '443',
                    'wss': '443',
                    'gopher': '70',
                    'news': '119',
                    'snews': '563',
                    'nntp': '119',
                    'snntp': '563',
                    'ftp': '21',
                    'telnet': '23',
                    'prospero': '191',
                }
_relative_schemes = [   'http',
                        'https',
                        'ws',
                        'wss',
                        'itms',
                        'news',
                        'snews',
                        'nntp',
                        'snntp',
                        'ftp',
                        'file',
                        ''
                    ]
_server_authority_schemes = [   'http',
                                'https',
                                'ws',
                                'wss',
                                'itms',
                                'news',
                                'snews',
                                'ftp',
                            ]

qs_unsafe_list = ' /?&=;+%#'
fragment_unsafe_list = ' #'
path_unsafe_list = ' /?;%+#'
_hextochr = dict(('%02x' % i, chr(i)) for i in range(256))
_hextochr.update(('%02X' % i, chr(i)) for i in range(256))

def unquote_path(s):
    return unquote_safe(s, path_unsafe_list)

def unquote_qs(s):
    return unquote_safe(s, qs_unsafe_list)

def unquote_fragment(s):
    """unquote('%')"""
    return unquote_safe(s, fragment_unsafe_list)
    
def unquote_safe(s, unsafe_list):
    """unquote('abc%20def') -> 'abc def'."""
    # note: this build utf8 raw strings ,then does a .decode('utf8') at the end.
    # as a result it's doing .encode('utf8') on each block of the string as it's processed.
    res = _utf8(s).split('%')
    for i in xrange(1, len(res)):
        item = res[i]
        try:
            raw_chr = _hextochr[item[:2]]
            if raw_chr in unsafe_list or ord(raw_chr) < 20:
                res[i] = '%' + item
            else:
                res[i] = raw_chr + item[2:]
        except KeyError:
            res[i] = '%' + item
        except UnicodeDecodeError:
            # note: i'm not sure what this does
            res[i] = unichr(int(item[:2], 16)) + item[2:]
    o = "".join(res)
    return _unicode(o)

always_safe = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
               'abcdefghijklmnopqrstuvwxyz'
               '0123456789' '_.-')
_safemaps = {}

def norm(url):
    """given a string URL, return its normalised/unicode form"""
    url = _unicode(url) # operate on unicode strings
    url_tuple = urlparse(url)
    normalized_tuple = norm_tuple(*url_tuple)
    return urlunparse(normalized_tuple)

def norm_tuple(scheme, authority, path, parameters, query, fragment):
    """given individual url components, return its normalised form"""
    scheme = lower(scheme)
    authority = norm_netloc(scheme, authority)
    path = norm_path(scheme, path)
    # TODO: put query in sorted order; or at least group parameters together
    # Note that some websites use positional parameters or the name part of a query so this would break the internet
    # query = urlencode(parse_qs(query, keep_blank_values=1), doseq=1) 
    query = unquote_qs(query)
    fragment = unquote_fragment(fragment)
    return (scheme, authority, path, parameters, query, fragment)

def norm_path(scheme, path):
    if scheme in _relative_schemes:
        last_path = path
        while 1:
            path = _collapse.sub('/', path, 1)
            if last_path == path:
                break
            last_path = path
    path = unquote_path(path)
    return path

def norm_netloc(scheme, netloc):
    if not netloc:
        return netloc
    match = _server_authority.match(netloc)
    if not match:
        raise InvalidUrl('no host in netloc %r' % netloc)
    
    userinfo, host, port = match.groups()
    if host[-1] == '.':
        host = host[:-1]
    
    authority = lower(host)
    if 'xn--' in authority:
        # convert each section of the domain from idna individually
        domains = authority.split('.')
        for i in range(len(domains)):
            if 'xn--' in domains[i]:
                try:
                    domains[i] = domains[i].decode('idna')
                except UnicodeError:
                    raise InvalidUrl('Error converting domain to IDN %r' % authority)
        authority = '.'.join(domains)
        
    if userinfo:
        authority = "%s@%s" % (userinfo, authority)
    if port and port != _default_port.get(scheme, None):
        authority = "%s:%s" % (authority, port)
    return authority


def _utf8(value):
    if isinstance(value, unicode):
        return value.encode("utf-8")
    assert isinstance(value, str)
    return value


def _unicode(value):
    if isinstance(value, str):
        return value.decode("utf-8")
    assert isinstance(value, unicode)
    return value
